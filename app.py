from langchain_groq import ChatGroq
from langchain_community.tools import ArxivQueryRun, WikipediaQueryRun, DuckDuckGoSearchResults
from langchain_community.utilities import ArxivAPIWrapper, WikipediaAPIWrapper, DuckDuckGoSearchAPIWrapper
import streamlit as st
from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.tools.retriever import create_retriever_tool
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
import os
import uuid
from prompts import system_prompt

# Load environment variables and set HuggingFace token
load_dotenv()
os.environ["HF_TOKEN"] = os.getenv("HF_TOKEN")

# --- Streamlit State Initialization ---
# Persistent state for all document and chat management
if 'Document_store' not in st.session_state:
    st.session_state['Document_store'] = []  # All loaded documents (PDFs, web)
if 'papers_count' not in st.session_state:
    st.session_state['papers_count'] = 0
if 'web_links' not in st.session_state:
    st.session_state['web_links'] = []  # List of dicts: {url: str, docs: list}
if 'edit_link_idx' not in st.session_state:
    st.session_state['edit_link_idx'] = None
if 'edit_url_value' not in st.session_state:
    st.session_state['edit_url_value'] = ''
if 'vectorstore' not in st.session_state:
    st.session_state['vectorstore'] = None
if 'retriever' not in st.session_state:
    st.session_state['retriever'] = None
if 'last_doc_count' not in st.session_state:
    st.session_state['last_doc_count'] = 0
if 'uploader_key' not in st.session_state:
    st.session_state['uploader_key'] = 'default'
if 'pdf_uploaded' not in st.session_state:
    st.session_state['pdf_uploaded'] = False

# --- Streamlit UI ---
st.markdown("<h1 style='text-align: center;'>Chat with AI Agent</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.title("Settings")
    # API Key management
    try:
        groq_api_key = os.getenv("GROQ_API_KEY")
        llm = ChatGroq(model="gemma2-9b-it", api_key=groq_api_key)
    except Exception as e:
        st.error(f"Groq API Key is not set: {e}")
        st.stop()
    else:
        st.subheader("Groq API Key")
        groq_api_key = st.text_input("Enter your Groq API Key", type="password")

    st.subheader(f"Documents Stored: {st.session_state['papers_count']}", divider=True)
    # PDF Upload (with key reset to prevent repeated processing)
    uploaded_files = st.file_uploader(
        "Upload a PDF file", type=["pdf"], accept_multiple_files=True, key=st.session_state['uploader_key']
    )
    # Only process new uploads once
    if uploaded_files and not st.session_state['pdf_uploaded']:
        with st.spinner("Setting up your documents"):
            for file in uploaded_files:
                temppdf = f"temp{file.name}"
                with open(temppdf, "wb") as f:
                    f.write(file.getvalue())
                pdf_loader = PyPDFLoader(temppdf)
                docs = pdf_loader.load()
                st.session_state['Document_store'].extend(docs)
                st.toast(f"Loaded document {file.name} as {len(docs)} pages.")
                os.remove(temppdf)
            st.session_state['papers_count'] = len(st.session_state['Document_store'])
        st.session_state['uploader_key'] = str(uuid.uuid4())
        st.session_state['pdf_uploaded'] = True
    elif not uploaded_files:
        st.session_state['pdf_uploaded'] = False

    # Webpage management: add, edit, delete links and their docs
    st.subheader("Manage Webpages", divider=True)
    new_url = st.text_input("Enter the URL of the webpage", key="add_url")
    if st.button("Add Webpage", key="add_webpage") and new_url:
        loader = WebBaseLoader(new_url)
        docs = loader.load()
        st.session_state['web_links'].append({"url": new_url, "docs": docs})
        st.session_state['Document_store'].extend(docs)
        st.session_state['papers_count'] = len(st.session_state['Document_store'])
        st.toast(f"Loaded URL content as {len(docs)} pages.")

    # List and manage existing web links
    for idx, link in enumerate(st.session_state['web_links']):
        col1, col2 = st.columns([8, 2])
        with col1:
            st.write(link['url'])
        with col2:
            if st.button("Delete", key=f"delete_link_{idx}"):
                # Remove docs for this link
                for doc in link['docs']:
                    if doc in st.session_state['Document_store']:
                        st.session_state['Document_store'].remove(doc)
                del st.session_state['web_links'][idx]
                st.session_state['papers_count'] = len(st.session_state['Document_store'])
                st.toast("Webpage deleted.")
                break  # Avoid index errors after deletion

    # Session management for chat
    st.subheader("Session Management", divider=True)
    session_id = st.text_input("Enter the session ID", value="default_session")
    if st.button("Clear Chat", key="clear_chat"):
        if 'chat_history' in st.session_state and session_id in st.session_state.chat_history:
            st.session_state.chat_history[session_id].clear()
            st.success("Chat history cleared for this session.")
    if st.button("Clear Uploaded Content", key="clear_uploaded_content"):
        st.session_state['Document_store'].clear()
        st.session_state['web_links'].clear()
        st.session_state['papers_count'] = 0
        st.success("All uploaded documents and links have been cleared.")

# --- Main App Logic ---
if groq_api_key:
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = {}

    # Retrieve or create chat history for a session
    def get_session_history(session_id) -> BaseChatMessageHistory:
        if session_id not in st.session_state.chat_history:
            st.session_state.chat_history[session_id] = ChatMessageHistory()
        return st.session_state.chat_history[session_id]

    # Build or update the FAISS vectorstore and retriever if documents change
    def update_vectorstore():
        st.session_state['vectorstore'] = FAISS.from_documents(
            st.session_state['Document_store'],
            embedding=HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        )
        st.session_state['vectorstore'].save_local("faiss_index")
        st.session_state['retriever'] = st.session_state['vectorstore'].as_retriever()
        st.session_state['last_doc_count'] = len(st.session_state['Document_store'])

    # Only build vectorstore if there are documents
    if st.session_state['Document_store']:
        if (
            st.session_state['vectorstore'] is None or
            st.session_state['last_doc_count'] != len(st.session_state['Document_store'])
        ):
            update_vectorstore()
            st.toast(f"Total pages loaded: {len(st.session_state['Document_store'])}")
        retriever = st.session_state['retriever']
        try:
            # Set up agent and tools
            arxiv = ArxivQueryRun(api_wrapper=ArxivAPIWrapper(), description="If you need to search for any information from Arxiv online beyond the document store, use this tool for answering the question")
            wiki = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper(), description="If you need to search for any information from wikipedia beyond the document store, use this tool for answering the question")
            search = DuckDuckGoSearchResults(api_wrapper=DuckDuckGoSearchAPIWrapper(), description="Search engine: If we need to search for any information online beyond the document store, use this tool for answering the question")
            Document_Retriever = create_retriever_tool(
                retriever,
                name="Document_Retriever",
                description="A tool to retrieve documents from the document store"
            )
            tools = [arxiv, wiki, search, Document_Retriever]
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="chat_history", optional=True),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad")
            ])
            agent = create_openai_tools_agent(llm, tools, prompt)
            agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
            runnable_agent = RunnableWithMessageHistory(
                agent_executor,
                get_session_history,
                input_messages_key="input",
                history_messages_key="chat_history"
            )
        except Exception as e:
            st.error(f"Error setting up your agent: {e}")
            st.stop()

        # Chat input and response display
        if query := st.chat_input("Enter your message"):
            with st.spinner("Thinking..."):
                response = runnable_agent.invoke({"input": query}, config={"configurable": {"session_id": session_id}})
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






