# 🧠 CogniShare Protocol

> **Decentralized RAG with x402 Micropayments on Cronos EVM**

A hackathon MVP demonstrating how AI agents can automatically pay knowledge authors via micropayments when their content is cited in AI responses.

![Cronos](https://img.shields.io/badge/Cronos-Testnet-blue)
![Python](https://img.shields.io/badge/Python-3.9+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 💡 The Concept

**Problem:** AI models use human-created content but authors receive nothing.

**Solution:** CogniShare Protocol tracks who contributed what knowledge and automatically sends them CRO micropayments when AI cites their work.

```
┌─────────────────────────────────────────────────────────────┐
│                    CogniShare Protocol                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   1. Author uploads PDF + Wallet Address                     │
│              ↓                                               │
│   2. Document → Chunks → Embeddings → Pinecone               │
│      (Each chunk tagged with author's wallet!)               │
│              ↓                                               │
│   3. User asks AI a question                                 │
│              ↓                                               │
│   4. RAG retrieves relevant chunks                           │
│              ↓                                               │
│   5. x402 Payment: Send CRO to chunk authors                 │
│              ↓                                               │
│   6. GPT-4o-mini generates answer using context              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy template
copy env.template .env  # Windows
cp env.template .env    # Mac/Linux

# Edit .env with your API keys
```

**Minimum Required:**
- `OPENAI_API_KEY` - For embeddings and chat

**Optional (for full features):**
- `PINECONE_API_KEY` - Production vector storage
- `CRONOS_PRIVATE_KEY` - Real blockchain payments

### 3. Run the App

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser!

---

## 🎮 Testing Modes

### Mock Mode (Default)
If API keys are missing, the app automatically uses:
- **Mock Vector Storage** - In-memory storage with demo data
- **Mock Payments** - Simulated TX hashes (no real CRO sent)

This lets you test the full UX without any configuration!

### Production Mode
With all API keys configured:
- **Pinecone** - Scalable vector database
- **Real Payments** - Actual CRO transactions on Cronos Testnet

---

## 📁 Project Structure

```
CogniShare-Protocol/
├── app.py              # Streamlit UI (main entry point)
├── rag_core.py         # RAG Engine (embeddings, search)
├── payment_manager.py  # Cronos x402 payments
├── requirements.txt    # Python dependencies
├── env.template        # Environment variables template
└── README.md           # You are here!
```

---

## 🔧 Architecture

### `rag_core.py` - RAGEngine Class

```python
engine = RAGEngine()

# Ingest a document with author attribution
engine.ingest_document(pdf_file, "0xAuthorWallet...")

# Query for relevant chunks
results = engine.query("What is decentralized AI?")
# Returns: [{"text": "...", "author_wallet": "0x...", "score": 0.95}, ...]
```

**Key Feature:** Every chunk stores `author_wallet` in Pinecone metadata!

### `payment_manager.py` - CronosPayment Class

```python
payment = CronosPayment(use_testnet=True)

# Pay authors from RAG results
result = payment.pay_authors(
    author_wallets=["0x123...", "0x456..."],
    amount_per_citation=0.01  # CRO per citation
)
# Returns: {"tx_hashes": [...], "total_paid": 0.02, ...}
```

**Key Feature:** Deduplicates wallets and batches payments!

### `app.py` - Streamlit Interface

- **Sidebar:** Upload documents, configure API keys
- **Main:** Chat interface with real-time payment visualization
- **State:** Uses `st.session_state` for chat history

---

## 🌐 Cronos Testnet Setup

### Add to MetaMask

| Setting | Value |
|---------|-------|
| Network Name | Cronos Testnet |
| RPC URL | https://evm-t3.cronos.org |
| Chain ID | 338 |
| Symbol | tCRO |
| Explorer | https://explorer.cronos.org/testnet3 |

### Get Test CRO

1. Visit [Cronos Faucet](https://cronos.org/faucet)
2. Enter your wallet address
3. Receive free test CRO

---

## 🔐 Security Notes

- **Never commit `.env`** - Contains private keys!
- **Use testnet first** - Validate before mainnet
- **Rotate keys regularly** - Best practice

---

## 🏆 Hackathon Features

✅ PDF ingestion with author wallet attribution  
✅ Semantic search with Pinecone/mock fallback  
✅ x402 micropayments on Cronos EVM  
✅ GPT-4o-mini for answer generation  
✅ Beautiful Streamlit UI  
✅ Graceful degradation (mock modes)  
✅ Transaction tracking & explorer links  

---

## 📜 License

MIT License - Build on this!

---

## 🤝 Credits

Built for the **Cronos Hackathon** 🏆

*Decentralizing AI, one citation at a time.*

