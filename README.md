# ChatWithPDF - AI Agent Chat Application

An intelligent AI-powered chat application that allows users to interact with documents and external knowledge sources through a conversational interface. Built with Streamlit, LangChain, and Groq's LLM.

## 🚀 Features

- **Document Upload & Processing**: Upload PDF files and add web pages for document retrieval
- **AI Agent Chat**: Conversational interface powered by Groq's Gemma2-9B model
- **Vector Search**: FAISS-powered semantic search through uploaded documents
- **External Knowledge Sources**:
  - Arxiv research papers
  - Wikipedia articles
  - DuckDuckGo web search
- **Session Management**: Persistent chat history across sessions
- **Real-time Responses**: Streaming chat interface with typing indicators

## 📋 Requirements

- Python 3.12+
- Groq API Key
- HuggingFace Token (for embeddings)

## 🛠️ Installation

### Using uv (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Shivaprakash001/ChatWithPDF.git
   cd ChatWithPDF
   ```

2. **Create and activate virtual environment:**
   ```bash
   uv venv
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   uv sync
   ```

### Using pip

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Shivaprakash001/ChatWithPDF.git
   cd ChatWithPDF
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Configuration

1. **Create a `.env` file in the root directory:**
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   HF_TOKEN=your_huggingface_token_here
   ```

2. **Get API Keys:**
   - **Groq API Key**: Sign up at [Groq Console](https://console.groq.com/)
   - **HuggingFace Token**: Create at [HuggingFace Settings](https://huggingface.co/settings/tokens)

## 🚀 Usage

### Running the Application

```bash
# Using uv
uv run streamlit run app.py

# Or if virtual environment is activated
streamlit run app.py
```

The application will be available at `http://localhost:8502`

### How to Use

1. **Enter API Key**: Input your Groq API key in the sidebar
2. **Upload Documents**:
   - Upload PDF files using the file uploader
   - Add web pages by entering URLs
3. **Start Chatting**: Enter your questions in the chat input
4. **Session Management**: Use different session IDs to maintain separate conversations

### Features Overview

- **Document Retrieval**: The AI agent can search through your uploaded documents to provide context-aware answers
- **External Tools**: When document context is insufficient, the agent uses Arxiv, Wikipedia, or web search
- **Chat History**: Conversations are preserved across sessions
- **Document Management**: Add or remove documents and web pages dynamically

## 🏗️ Architecture

- **Frontend**: Streamlit web interface
- **AI Model**: Groq's Gemma2-9B-IT via LangChain
- **Embeddings**: HuggingFace's all-MiniLM-L6-v2 for document vectorization
- **Vector Store**: FAISS for efficient similarity search
- **Tools Integration**: LangChain tools for external data sources

## 📁 Project Structure

```
ChatWithPDF/
├── app.py                 # Main Streamlit application
├── prompts.py             # System prompts and instructions
├── requirements.txt       # Python dependencies
├── pyproject.toml         # Project configuration
├── uv.lock               # uv dependency lock file
├── .env                  # Environment variables (not in repo)
├── .gitignore            # Git ignore rules
├── faiss_index/          # Vector store directory (auto-generated)
├── README.md             # This file
└── tools_agents.ipynb    # Jupyter notebook for development
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and commit: `git commit -am 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [LangChain](https://github.com/langchain-ai/langchain) for the agent framework
- [Streamlit](https://streamlit.io/) for the web interface
- [Groq](https://groq.com/) for fast LLM inference
- [HuggingFace](https://huggingface.co/) for embeddings and models

## 🔧 Troubleshooting

**Common Issues:**

1. **"Module not found" errors**: Ensure you've activated the virtual environment and installed dependencies
2. **API Key errors**: Verify your `.env` file contains valid API keys
3. **Document processing fails**: Check file permissions and ensure PDFs are not corrupted

**Performance Tips:**

- Large PDFs may take time to process initially
- The FAISS index is cached for faster subsequent loads
- Consider using smaller document chunks for better retrieval accuracy

---

**Made with ❤️ using LangChain, Streamlit, and Groq**
