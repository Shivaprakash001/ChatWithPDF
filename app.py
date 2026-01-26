from langchain_core.runnables import RunnableWithMessageHistory
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain_community.vectorstores import Chroma
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_huggingface import HuggingFaceEmbeddings
import os
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
import shutil

# Load environment variables
load_dotenv()
os.environ["HF_TOKEN"] = os.getenv("HF_TOKEN")

# Embeddings
@st.cache_resource
def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'}
    )

embeddings = get_embeddings()

# Streamlit page configuration
st.set_page_config(page_title="Chat with your Notes", page_icon="🔖", layout="wide")

# Initialize session states
if 'all_documents' not in st.session_state:
    st.session_state.all_documents = []
if 'loaded_sources' not in st.session_state:
    st.session_state.loaded_sources = []
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = {}

# Sidebar controls
with st.sidebar:
    st.header("Settings")

    st.subheader("📁 Upload PDFs")
    uploaded_files = st.file_uploader("Choose PDF files", type=["pdf"], accept_multiple_files=True)
    if st.button("Add PDFs"):
        if uploaded_files:
            new_docs_count = 0
            for file in uploaded_files:
                if file.name not in st.session_state.loaded_sources:
                    temp_pdf = f"./temp_{file.name}"
                    with open(temp_pdf, "wb") as f:
                        f.write(file.getvalue())
                    
                    try:
                        loader = PyPDFLoader(temp_pdf)
                        docs = loader.load()
                        st.session_state.all_documents.extend(docs)
                        st.session_state.loaded_sources.append(file.name)
                        new_docs_count += 1
                    finally:
                        if os.path.exists(temp_pdf):
                            os.remove(temp_pdf)
            if new_docs_count > 0:
                st.success(f"Added {new_docs_count} new PDF(s)")
                st.session_state.pop('vectorstore', None) # Force rebuild
            else:
                st.info("Files already added or no files selected.")

    st.subheader("🌐 Load Website")
    web_url = st.text_input("Enter URL")
    if st.button("Add URL"):
        if web_url:
            if web_url not in st.session_state.loaded_sources:
                with st.spinner("Scraping website..."):
                    try:
                        web_loader = WebBaseLoader(web_url)
                        web_docs = web_loader.load()
                        st.session_state.all_documents.extend(web_docs)
                        st.session_state.loaded_sources.append(web_url)
                        st.success(f"Loaded content from {web_url}")
                        st.session_state.pop('vectorstore', None) # Force rebuild
                    except Exception as e:
                        st.error(f"Failed to load website: {e}")
            else:
                st.warning("URL already added.")

    st.subheader("📖 Loaded Sources")
    if st.session_state.loaded_sources:
        for i, source in enumerate(st.session_state.loaded_sources):
            st.text(f"{i+1}. {source[:30]}...")
    else:
        st.info("No sources loaded yet.")

    st.subheader("⚙️ API Settings")
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        api_key = st.text_input("Groq API Key", type="password")
    
    groq_model = st.selectbox(
        "Select Groq Model",
        ["llama-3.1-8b-instant", "llama-3.3-70b-versatile"]
    )
    
    st.subheader("🧼 Cleanup")
    session_id = st.text_input("Session ID", value="default_session")
    if st.button("Reset Chat"):
        if session_id in st.session_state.chat_history:
            st.session_state.chat_history[session_id] = ChatMessageHistory()
        st.success("Chat history reset.")

    if st.button("Clear All Data"):
        if os.path.exists("./chroma_db"):
            shutil.rmtree("./chroma_db", ignore_errors=True)
        st.session_state.all_documents = []
        st.session_state.loaded_sources = []
        st.session_state.pop('vectorstore', None)
        st.session_state.pop('retriever', None)
        st.success("All documents and vectorstore cleared.")

# Main Interface
st.title("🔖 Chat with your Notes & Web")
st.write("Combined PDF and Web content analyzer.")

# Core Logic
if api_key:
    try:
        llm = ChatGroq(model_name=groq_model, api_key=api_key)
    except Exception as e:
        st.error(f"Error with API key: {e}")
        st.stop()

    # Rebuild vectorstore if needed
    if st.session_state.all_documents and 'vectorstore' not in st.session_state:
        with st.spinner("Indexing content..."):
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            chunks = text_splitter.split_documents(st.session_state.all_documents)
            
            # Use in-memory Chroma to avoid Streamlit Cloud 'readonly database' errors
            st.session_state.vectorstore = Chroma.from_documents(
                chunks, 
                embeddings
            )
            st.session_state.retriever = st.session_state.vectorstore.as_retriever(search_kwargs={"k": 5})

    if 'vectorstore' in st.session_state:
        contextualized_q_prompt = ChatPromptTemplate.from_messages([
            ("system", "Given chat history and a question, retrieve relevant documents. Do not answer. Use chat history to form standalone questions."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
        ])

        history_aware_retriever = create_history_aware_retriever(
            retriever=st.session_state.retriever,
            prompt=contextualized_q_prompt,
            llm=llm,
        )

        system_prompt = """
        You are a concise, professional assistant.
        Only answer questions directly based on the provided document and website context.
        If unsure, respond with "I don't know."
        Try to synthesize information from both PDFs and websites if applicable.
        Context: {context}
        """

        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
        ])

        stuff_chain = create_stuff_documents_chain(llm, qa_prompt)
        rag_chain = create_retrieval_chain(history_aware_retriever, stuff_chain)

        def get_session_history(sid) -> BaseChatMessageHistory:
            if sid not in st.session_state.chat_history:
                st.session_state.chat_history[sid] = ChatMessageHistory()
            return st.session_state.chat_history[sid]

        conversational_rag_chain = RunnableWithMessageHistory(
            rag_chain,
            get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
        )

        # UI for Chat
        chat_container = st.container()
        with chat_container:
            session_history = get_session_history(session_id)
            for msg in session_history.messages:
                with st.chat_message("user" if msg.type == 'human' else "assistant"):
                    st.write(msg.content)

        user_input = st.chat_input("Ask about your PDF or loaded websites...")

        if user_input:
            with st.chat_message("user"):
                st.write(user_input)

            with st.chat_message("assistant"):
                with st.spinner("Searching and thinking..."):
                    response = conversational_rag_chain.invoke(
                        {"input": user_input},
                        config={"configurable": {"session_id": session_id}}
                    )
                    st.write(response['answer'])
    else:
        st.info("👈 Please load some documents or URLs in the sidebar to start chatting.")
else:
    st.warning("Please provide a Groq API Key to start.")
