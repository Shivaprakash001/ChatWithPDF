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
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import WebBaseLoader
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
st.set_page_config(page_title="Chat with your Notes", page_icon="🔖")

# Sidebar controls
with st.sidebar:
    st.header("Settings")

    st.subheader("Upload & Manage")
    uploaded_files = st.file_uploader("Upload PDF files", type=["pdf"], accept_multiple_files=True)

    # st.subheader("Web Loader")
    # web_url = st.text_input("Enter Website URL")
    # load_web_button = st.button("Load Web Content")

    try:
        api_key=os.getenv("GROQ_API_KEY")
    except:
        st.subheader("API Settings")
        api_key = st.text_input("Groq API Key", type="password")

    st.subheader("Session Management")
    session_id = st.text_input("Session ID", value="default_session")

    if st.button("Reset Chat"):
        if 'chat_history' in st.session_state and session_id in st.session_state.chat_history:
            st.session_state.chat_history[session_id] = ChatMessageHistory()
        st.success("Chat history reset.")

    st.subheader("Clear Database")
    if st.button("Clear Database"):
        if os.path.exists("./chroma_db"):
            shutil.rmtree("./chroma_db", ignore_errors=True)
            st.session_state.pop('documents', None)
            st.session_state.pop('vectorstore', None)
            st.session_state.pop('retriever', None)
            st.session_state.pop('chunks', None)
            st.success("Database and documents cleared.")
        else:
            st.warning("No database found.")

# Main Interface
st.title("Chat with your Notes")
st.write("Upload a PDF file in the sidebar and chat below.")
# Core Logic
if api_key:
    documents = []
    try:
        llm = ChatGroq(model_name="Gemma2-9b-It", api_key=api_key)
    except Exception as e:
        st.error(f"Error with API key: {e}")
        st.stop()

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = {}

    if uploaded_files:
        for file in uploaded_files:
            temp_pdf = f"./temp_{file.name}"
            with open(temp_pdf, "wb") as f:
                f.write(file.getvalue())

            loader = PyPDFLoader(temp_pdf)
            docs = loader.load()
            documents.extend(docs)
            os.remove(temp_pdf)
    # if load_web_button and web_url:
    #     try:
    #         web_loader = WebBaseLoader(web_url)
    #         web_docs = web_loader.load()
    #         documents.extend(web_docs)
    #         st.success(f"Loaded {len(web_docs)} documents from website.")
    #     except Exception as e:
    #         st.error(f"Failed to load website: {e}")

    if documents:
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=300)
        chunks = text_splitter.split_documents(documents)
        st.write(f"Processed {len(documents)} document(s) into {len(chunks)} chunks.")

        vectorstore = Chroma.from_documents(chunks, embeddings, persist_directory="./chroma_db")
        retriever = vectorstore.as_retriever()

        contextualized_q_prompt = ChatPromptTemplate.from_messages([
            ("system", "Given chat history and a question, retrieve relevant documents. Do not answer. Use chat history to form standalone questions."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
        ])

        history_aware_retriever = create_history_aware_retriever(
            retriever=retriever,
            prompt=contextualized_q_prompt,
            llm=llm,
        )

        system_prompt = """
        You are a concise, professional assistant.
        Only answer questions directly based on the provided document context.
        If unsure, respond with "I don't know."
        If the question is not related to the documents, ask for more clarification.
        Try to give every information that relates the question in a structured way. 
        Context: {context}
        """

        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
        ])

        stuff_chain = create_stuff_documents_chain(llm, qa_prompt)
        rag_chain = create_retrieval_chain(history_aware_retriever, stuff_chain)

        def get_session_history(session_id) -> BaseChatMessageHistory:
            if session_id not in st.session_state.chat_history:
                st.session_state.chat_history[session_id] = ChatMessageHistory()
            return st.session_state.chat_history[session_id]

        conversational_rag_chain = RunnableWithMessageHistory(
            rag_chain,
            get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
        )

        user_input = st.chat_input("Ask your question here...")

        if user_input:
            response = conversational_rag_chain.invoke(
                {"input": user_input},
                config={"configurable": {"session_id": session_id}}
            )
            

            session_history = get_session_history(session_id)

            for msg in session_history.messages:
                if msg.type == 'human':
                    with st.chat_message("user"):
                        st.write(msg.content)
                else:
                    with st.chat_message("assistant"):
                        st.write(msg.content)

else:
    st.warning("Please enter a valid API key in the sidebar to start.")
