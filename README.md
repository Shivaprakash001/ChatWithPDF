# Chat with PDF 📚

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/LangChain-Latest-green.svg)](https://github.com/langchain-ai/langchain)
[![Streamlit](https://img.shields.io/badge/Streamlit-Latest-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An intelligent RAG (Retrieval-Augmented Generation) application that allows you to have interactive conversations with your PDF documents using advanced AI. Upload your PDFs, ask questions, and get contextual answers powered by LangChain and Groq.

## 📋 Description

Chat with PDF is a powerful document question-answering system that combines the capabilities of Large Language Models (LLMs) with vector search to provide accurate, context-aware responses from your PDF documents. The application maintains conversation history, allowing for natural follow-up questions and contextual understanding.

## ✨ Key Features

- **📂 Multi-PDF Upload**: Upload and process multiple PDF files simultaneously
- **💬 Conversational AI**: Natural language conversations with context retention
- **🧠 Smart Context Retrieval**: History-aware document retrieval for better answers
- **📊 Chunk Management**: Intelligent document chunking for optimal performance
- **🔐 Session Management**: Multiple independent conversation sessions
- **🗑️ Database Control**: Clear vector database and reset conversations
- **⚡ Fast Processing**: Powered by Groq's optimized LLM infrastructure
- **🎯 Accurate Responses**: Only answers based on document context
- **🔄 Persistent Storage**: ChromaDB for reliable vector storage

## 🏗️ Architecture

```
┌──────────────┐
│  PDF Upload  │
└──────┬───────┘
       │
       ↓
┌──────────────────┐
│ Text Extraction  │
│  & Chunking      │
└──────┬───────────┘
       │
       ↓
┌──────────────────┐
│   Embeddings     │
│ (HuggingFace)    │
└──────┬───────────┘
       │
       ↓
┌──────────────────┐
│   ChromaDB       │
│ Vector Storage   │
└──────┬───────────┘
       │
       ↓
┌──────────────────┐
│   RAG Chain      │
│ History-Aware    │
│   Retrieval      │
└──────┬───────────┘
       │
       ↓
┌──────────────────┐
│  Groq LLM        │
│ (Gemma2-9b-It)   │
└──────┬───────────┘
       │
       ↓
┌──────────────────┐
│  User Response   │
└──────────────────┘
```

## 📂 Project Structure

```
ChatwithPDF/
├── app.py                 # Main Streamlit application
├── chroma_db/             # Vector database storage
├── requirements.txt       # Python dependencies
├── pyproject.toml         # Project configuration
├── uv.lock                # UV lock file
├── .env                   # Environment variables (not in repo)
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## 🛠️ Technologies Used

- **Streamlit** - Interactive web interface
- **LangChain** - LLM application framework
- **LangChain-Groq** - Groq LLM integration (Gemma2-9b-It)
- **ChromaDB** - Vector database for document embeddings
- **HuggingFace Embeddings** - Sentence transformers (all-MiniLM-L6-v2)
- **PyPDFLoader** - PDF document processing
- **Python 3.12+**

## 📦 Installation

### Prerequisites

- Python 3.12 or higher
- Groq API key ([Get one here](https://console.groq.com/))
- HuggingFace token (optional, for embeddings)

### Setup

1. **Clone the repository**:
```bash
git clone https://github.com/Shivaprakash001/ChatWithPDF.git
cd ChatWithPDF
```

2. **Install dependencies**:

Using pip:
```bash
pip install -r requirements.txt
```

Using UV (recommended):
```bash
pip install uv
uv sync
```

3. **Set up environment variables**:

Create a `.env` file:
```env
GROQ_API_KEY=your_groq_api_key_here
HF_TOKEN=your_huggingface_token_here  # Optional
```

## 💻 Usage

### Run the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

### Step-by-Step Guide

1. **Enter API Key** (if not in `.env`):
   - Open the sidebar
   - Enter your Groq API key

2. **Upload PDFs**:
   - Click "Upload PDF files" in the sidebar
   - Select one or multiple PDF files
   - Wait for processing to complete

3. **Configure Session** (optional):
   - Set a custom session ID for separate conversations
   - Default: "default_session"

4. **Ask Questions**:
   - Type your question in the chat input
   - Get contextual answers from your documents
   - Ask follow-up questions naturally

5. **Manage Sessions**:
   - **Reset Chat**: Clear current session history
   - **Clear Database**: Remove all documents and start fresh

## 🎯 Use Cases

- **📖 Research**: Query academic papers and research documents
- **📑 Legal Documents**: Search through contracts and legal files
- **📚 Study Materials**: Get answers from textbooks and notes
- **📊 Reports**: Analyze business reports and financial documents
- **📝 Documentation**: Navigate technical documentation easily
- **🎓 Education**: Interactive learning from course materials

## 🔧 Configuration

### Customize LLM Model

Edit `app.py` to change the model:
```python
llm = ChatGroq(model_name="llama-3.3-70b-versatile", api_key=api_key)
```

Available Groq models:
- `Gemma2-9b-It` (default, balanced)
- `llama-3.3-70b-versatile` (larger, more capable)
- `llama-3.1-8b-instant` (faster, lighter)
- `mixtral-8x7b-32768` (large context window)

### Adjust Chunk Size

Modify chunking parameters in `app.py`:
```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=5000,      # Adjust based on document complexity
    chunk_overlap=300     # Overlap for context continuity
)
```

### Change Embedding Model

Update the embedding model:
```python
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
```

Other options:
- `all-mpnet-base-v2` (better quality, slower)
- `multi-qa-MiniLM-L6-cos-v1` (optimized for Q&A)

## 🎨 Features in Detail

### History-Aware Retrieval
The system reformulates questions based on conversation context:
```
User: "What is machine learning?"
AI: [Answers based on PDF]
User: "What are its applications?"
System reformulates to: "What are the applications of machine learning?"
```

### Session Management
- Multiple independent conversations
- Persistent chat history per session
- Easy session switching and reset

### Smart Document Processing
- Automatic PDF text extraction
- Intelligent chunking for optimal retrieval
- Vector embeddings for semantic search

## 🚀 Advanced Usage

### Adding Web Loader (Optional)

Uncomment the web loader section in `app.py` to load content from websites:
```python
st.subheader("Web Loader")
web_url = st.text_input("Enter Website URL")
if st.button("Load Web Content"):
    web_loader = WebBaseLoader(web_url)
    web_docs = web_loader.load()
    documents.extend(web_docs)
```

### Customizing System Prompts

Modify the system prompt in `app.py`:
```python
system_prompt = """
You are an expert assistant specialized in [domain].
Answer questions based on the provided documents.
Always cite specific sections when possible.
Context: {context}
"""
```

## 📊 Performance Tips

1. **Chunk Size**: Larger chunks (5000+) for general documents, smaller (1000-2000) for technical content
2. **Overlap**: 10-20% overlap ensures context continuity
3. **Model Selection**: Use faster models for simple Q&A, larger models for complex analysis
4. **Database Persistence**: ChromaDB persists across sessions for faster subsequent queries

## 🐛 Troubleshooting

**Issue**: Slow PDF processing
- **Solution**: Reduce chunk size or process fewer pages at once

**Issue**: "API key not found" error
- **Solution**: Ensure `.env` file exists with valid `GROQ_API_KEY`

**Issue**: Out of memory
- **Solution**: Clear vector database, reduce chunk size, or process fewer PDFs

**Issue**: Inaccurate responses
- **Solution**: Adjust chunk size/overlap, try a different model, or rephrase your question

**Issue**: Database locked error
- **Solution**: Clear the `chroma_db` folder and restart

## 🔒 Security Notes

- Never commit `.env` file to version control
- Keep API keys secure and rotate them regularly
- Limit file upload size for production deployments
- Sanitize user inputs in production environments

## 🔮 Future Enhancements

- [ ] Support for more document formats (DOCX, TXT, HTML)
- [ ] Batch processing of large documents
- [ ] Export conversation history
- [ ] Advanced search filters and metadata
- [ ] Multi-language support
- [ ] Document summarization feature
- [ ] Citation and source highlighting
- [ ] User authentication and authorization
- [ ] API endpoint for programmatic access
- [ ] Mobile-responsive UI improvements

## 📚 Documentation

### API Response Format

The RAG chain returns responses with:
- `answer`: The generated answer
- `context`: Retrieved document chunks
- `source_documents`: Original PDF sources

### Session State Variables

- `chat_history`: Dictionary of session histories
- `documents`: Loaded PDF documents
- `vectorstore`: ChromaDB vector store
- `retriever`: Document retriever

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the MIT License.

## 👤 Author

**Shivaprakash**
- GitHub: [@Shivaprakash001](https://github.com/Shivaprakash001)

## 🙏 Acknowledgments

- LangChain for the excellent RAG framework
- Groq for ultra-fast LLM inference
- HuggingFace for embedding models
- Streamlit for the intuitive UI framework

## 📞 Support

If you encounter issues or have questions:
- Open an issue on GitHub
- Check the troubleshooting section
- Review LangChain documentation

---

⭐ **If this project helped you, please give it a star!** ⭐

**Made with ❤️ using LangChain and Streamlit**
