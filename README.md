AI Research Assistant (RAG-based PDF Analyzer)

An AI-powered research assistant that allows users to upload a PDF and ask questions about its content using semantic search and large language models.

Built with:
- Flask (Backend API)
- FAISS (Vector similarity search)
- OpenRouter (LLM + Embeddings)
- Meta llama 3.3 70b instruct


Features

- Upload any PDF
- Automatic text extraction
- Text chunking for retrieval
- Embedding generation
- Cosine similarity search (FAISS)
- Top-k semantic retrieval
- Context-aware question answering (RAG pipeline)


How It Works (RAG Pipeline)

1. PDF is uploaded
2. Text is extracted using pdfplumber
3. Text is chunked into smaller segments
4. Each chunk is converted into embeddings
5. Embeddings are stored in a FAISS vector index
6. When a question is asked:
   - The question is embedded
   - Top-k similar chunks are retrieved
   - Retrieved chunks are passed to the LLM as context
   - LLM generates a grounded answer


Project Structure

AI-Assistant/
 app.py
 requirement.txt
 README.md
 .gitignore


Future Improvements

- Streaming responses
- Persistent database storage
- User authentication
- Multi-document sessions
- Hybrid search (BM25 + embeddings)
- Deployment to Render/Railway

How To Run Locally
1. Install Dependencies
pip install -r requirement.txt

2. Run Flask App
   -app.py

3. Test App:
   Edit pdf file path in test.py
   Run test.py

License
This project is for educational and research purposes.

Author
Awwal Ajao