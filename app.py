"""
=============================================================================
CogniShare Protocol - Streamlit UI
=============================================================================
The main interface for the decentralized RAG + x402 micropayments MVP.

Features:
- Upload documents with author wallet attribution
- Chat interface for querying the knowledge base
- Real-time x402 micropayment visualization
- Beautiful hackathon-ready UI

Hackathon MVP - Cronos EVM
=============================================================================
"""

import os
import time
import streamlit as st
from dotenv import load_dotenv

# Import our custom modules
from rag_core import RAGEngine
from payment_manager import CronosPayment

# Load environment variables
load_dotenv()


# =============================================================================
# Page Configuration
# =============================================================================
st.set_page_config(
    page_title="CogniShare Protocol",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# Custom CSS for Hackathon-Ready Styling
# =============================================================================
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* Global Styles */
    .stApp {
        font-family: 'Space Grotesk', sans-serif;
    }
    
    /* Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 2rem;
        border: 1px solid #e94560;
        box-shadow: 0 0 30px rgba(233, 69, 96, 0.2);
    }
    
    .hero-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #e94560, #ff6b6b, #feca57);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .hero-subtitle {
        color: #a0a0a0;
        font-size: 1.1rem;
    }
    
    /* Payment Alert Box */
    .payment-alert {
        background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
        border-left: 4px solid #00ff88;
        border-radius: 8px;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .payment-alert h4 {
        color: #00ff88;
        margin: 0 0 0.5rem 0;
    }
    
    .payment-alert .amount {
        font-size: 1.5rem;
        color: #00ff88;
        font-weight: 600;
    }
    
    /* Source Card */
    .source-card {
        background: #1a1a2e;
        border: 1px solid #3a3a5a;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .source-card:hover {
        border-color: #e94560;
    }
    
    /* Wallet Badge */
    .wallet-badge {
        background: #16213e;
        border: 1px solid #e94560;
        border-radius: 20px;
        padding: 0.25rem 0.75rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        color: #e94560;
    }
    
    /* TX Hash Link */
    .tx-hash {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: #4ecdc4;
        word-break: break-all;
    }
    
    /* Chat Message Styling */
    .user-message {
        background: linear-gradient(135deg, #e94560 0%, #ff6b6b 100%);
        color: white;
        padding: 1rem;
        border-radius: 16px 16px 4px 16px;
        margin: 0.5rem 0;
    }
    
    .ai-message {
        background: #1a1a2e;
        border: 1px solid #3a3a5a;
        padding: 1rem;
        border-radius: 16px 16px 16px 4px;
        margin: 0.5rem 0;
    }
    
    /* Sidebar Styling */
    .sidebar-section {
        background: #1a1a2e;
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        border: 1px solid #3a3a5a;
    }
    
    /* Status Indicators */
    .status-online {
        color: #00ff88;
    }
    
    .status-offline {
        color: #ff6b6b;
    }
    
    /* Button Override */
    .stButton > button {
        background: linear-gradient(90deg, #e94560, #ff6b6b);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(233, 69, 96, 0.4);
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# Session State Initialization
# =============================================================================
def init_session_state():
    """Initialize all session state variables."""
    
    # Chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # RAG Engine (singleton pattern for efficiency)
    if "rag_engine" not in st.session_state:
        st.session_state.rag_engine = None
    
    # Payment Manager
    if "payment_manager" not in st.session_state:
        st.session_state.payment_manager = None
    
    # Upload stats
    if "total_uploads" not in st.session_state:
        st.session_state.total_uploads = 0
    
    # Payment stats
    if "total_payments" not in st.session_state:
        st.session_state.total_payments = 0.0
    
    # API Keys from input (if not in env)
    if "openai_key_input" not in st.session_state:
        st.session_state.openai_key_input = ""


# =============================================================================
# Engine Initialization
# =============================================================================
@st.cache_resource
def get_rag_engine():
    """Initialize and cache the RAG engine."""
    return RAGEngine()

@st.cache_resource
def get_payment_manager():
    """Initialize and cache the payment manager."""
    return CronosPayment(use_testnet=True)


# =============================================================================
# LLM Integration for Final Answer Generation
# =============================================================================
def generate_answer(query: str, context_chunks: list) -> str:
    """
    Generate an AI answer using GPT-4o-mini with retrieved context.
    
    This is the "Generation" part of RAG - we augment the prompt with
    retrieved knowledge and let the LLM synthesize an answer.
    """
    openai_key = os.getenv("OPENAI_API_KEY") or st.session_state.get("openai_key_input")
    
    if not openai_key:
        return "⚠️ OpenAI API key not configured. Please add it in the sidebar or .env file."
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=openai_key)
        
        # Build context from retrieved chunks
        context_text = "\n\n---\n\n".join([
            f"Source {i+1} (Author: {chunk['author_wallet'][:10]}...):\n{chunk['text']}"
            for i, chunk in enumerate(context_chunks)
        ])
        
        # System prompt explaining the x402 concept
        system_prompt = """You are an AI assistant powered by CogniShare Protocol - a decentralized RAG system.

You have access to a knowledge base where every piece of information has an author who gets paid in CRO cryptocurrency when you cite their work.

When answering questions:
1. Use the provided context to give accurate answers
2. Be concise but thorough
3. If the context doesn't contain relevant info, say so
4. Acknowledge that the knowledge came from decentralized contributors

Remember: The authors of the knowledge you're citing are being paid right now via x402 micropayments!"""

        # User prompt with context
        user_prompt = f"""Context from the decentralized knowledge base:

{context_text}

---

User Question: {query}

Please provide a helpful answer based on the context above."""

        # Call GPT-4o-mini
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"⚠️ Error generating answer: {str(e)}"


# =============================================================================
# Main Application
# =============================================================================
def main():
    """Main application entry point."""
    
    # Initialize session state
    init_session_state()
    
    # Get cached engines
    rag_engine = get_rag_engine()
    payment_manager = get_payment_manager()
    
    # =========================================================================
    # SIDEBAR
    # =========================================================================
    with st.sidebar:
        st.markdown("## ⚙️ Configuration")
        
        # API Key Configuration (if not in .env)
        with st.expander("🔑 API Keys", expanded=False):
            st.caption("Keys from .env are used automatically")
            
            # OpenAI Key
            if not os.getenv("OPENAI_API_KEY"):
                openai_input = st.text_input(
                    "OpenAI API Key",
                    type="password",
                    placeholder="sk-...",
                    help="Required for embeddings and chat"
                )
                if openai_input:
                    st.session_state.openai_key_input = openai_input
                    os.environ["OPENAI_API_KEY"] = openai_input
            else:
                st.success("✅ OpenAI Key loaded from .env")
        
        # Status Display
        st.markdown("---")
        st.markdown("### 📊 System Status")
        
        # RAG Status
        rag_stats = rag_engine.get_stats()
        if rag_stats["pinecone_connected"]:
            st.markdown("**Vector DB:** <span class='status-online'>🟢 Pinecone</span>", 
                       unsafe_allow_html=True)
        else:
            st.markdown("**Vector DB:** <span class='status-offline'>🟡 Mock Mode</span>", 
                       unsafe_allow_html=True)
        st.caption(f"Vectors stored: {rag_stats['total_vectors']}")
        
        # Payment Status
        payment_status = payment_manager.get_status()
        if payment_status["mock_mode"]:
            st.markdown("**Payments:** <span class='status-offline'>🟡 Mock Mode</span>", 
                       unsafe_allow_html=True)
            st.caption("Add CRONOS_PRIVATE_KEY to .env for real payments")
        else:
            st.markdown("**Payments:** <span class='status-online'>🟢 Live</span>", 
                       unsafe_allow_html=True)
            st.caption(f"Balance: {payment_status['balance_cro']:.4f} CRO")
        
        # Upload Section
        st.markdown("---")
        st.markdown("### 📤 Upload Knowledge")
        st.caption("Contribute to the decentralized knowledge base and earn CRO!")
        
        # Author wallet input
        author_wallet = st.text_input(
            "Your Wallet Address",
            placeholder="0x...",
            help="You'll receive CRO when AI cites your knowledge"
        )
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Upload PDF",
            type=["pdf"],
            help="PDF documents are processed into searchable chunks"
        )
        
        # Upload button
        if st.button("🚀 Ingest Document", use_container_width=True):
            if not uploaded_file:
                st.error("Please upload a PDF file")
            elif not author_wallet or not author_wallet.startswith("0x"):
                st.error("Please enter a valid wallet address (0x...)")
            else:
                with st.spinner("Processing document..."):
                    try:
                        result = rag_engine.ingest_document(uploaded_file, author_wallet)
                        st.success(f"✅ Ingested {result['chunks_created']} chunks!")
                        st.session_state.total_uploads += 1
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
        
        # Stats
        st.markdown("---")
        st.markdown("### 📈 Session Stats")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Uploads", st.session_state.total_uploads)
        with col2:
            st.metric("Paid Out", f"{st.session_state.total_payments:.4f} CRO")
    
    # =========================================================================
    # MAIN CONTENT
    # =========================================================================
    
    # Hero Banner
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">🧠 CogniShare Protocol</div>
        <div class="hero-subtitle">
            Decentralized RAG with x402 Micropayments | Powered by Cronos EVM
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Info
    st.info("""
    💡 **How it works:** Upload knowledge → Get cited by AI → Receive CRO micropayments automatically!
    
    Every time the AI uses your knowledge to answer a question, you get paid via the x402 protocol.
    """)
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show sources and payments for AI messages
            if message["role"] == "assistant" and "metadata" in message:
                metadata = message["metadata"]
                
                # Sources expander
                if "sources" in metadata:
                    with st.expander("📚 Knowledge Sources Used", expanded=False):
                        for i, source in enumerate(metadata["sources"]):
                            st.markdown(f"""
                            <div class="source-card">
                                <strong>Source {i+1}</strong> (Score: {source['score']:.2f})<br>
                                <span class="wallet-badge">{source['author_wallet'][:20]}...</span><br>
                                <small>{source['text'][:200]}...</small>
                            </div>
                            """, unsafe_allow_html=True)
                
                # Payment info
                if "payment" in metadata:
                    payment = metadata["payment"]
                    st.markdown(f"""
                    <div class="payment-alert">
                        <h4>⚡ x402 Payment Triggered</h4>
                        <div class="amount">{payment['total_paid']:.4f} CRO</div>
                        <small>Paid to {payment['unique_authors']} author(s) 
                        {'(Simulated)' if payment['mock_mode'] else '(On-Chain)'}</small>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Show TX hashes
                    if payment.get("tx_hashes"):
                        with st.expander("🔗 Transaction Details", expanded=False):
                            for tx in payment["tx_hashes"]:
                                explorer_url = payment_manager.get_explorer_url(tx["tx_hash"])
                                st.markdown(f"""
                                - **{tx['amount']:.4f} CRO** → `{tx['wallet'][:15]}...`
                                  - <span class="tx-hash">[{tx['tx_hash'][:30]}...]({explorer_url})</span>
                                """, unsafe_allow_html=True)
    
    # Chat input
    if prompt := st.chat_input("Ask the decentralized knowledge base..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Process query
        with st.chat_message("assistant"):
            # Step 1: Search knowledge base
            with st.spinner("🔍 Searching Knowledge Base..."):
                time.sleep(0.5)  # Brief delay for effect
                sources = rag_engine.query(prompt, top_k=3)
            
            st.success(f"📚 Found {len(sources)} relevant sources!")
            
            # Display sources preview
            with st.expander("📚 Knowledge Sources Found", expanded=True):
                for i, source in enumerate(sources):
                    st.markdown(f"""
                    **Source {i+1}** (Score: {source['score']:.2f})  
                    👤 Author: `{source['author_wallet'][:20]}...`  
                    📄 {source['text'][:150]}...
                    """)
            
            # Step 2: Process x402 payments
            with st.spinner("⚡ Processing x402 Micropayments..."):
                time.sleep(0.3)
                author_wallets = [s["author_wallet"] for s in sources]
                
                try:
                    payment_result = payment_manager.pay_authors(
                        author_wallets, 
                        amount_per_citation=0.01
                    )
                    
                    # CRITICAL x402 CHECK: Verify payment succeeded
                    if not payment_result['success']:
                        st.error("⚠️ **Payment Failed** - Cannot generate answer without compensating authors.")
                        
                        # Show error details
                        if payment_result.get('error'):
                            st.error(f"**Reason:** {payment_result['error']}")
                        
                        if payment_result.get('errors'):
                            with st.expander("⚠️ Transaction Error Details"):
                                for error in payment_result['errors']:
                                    st.warning(error)
                        
                        # In Mock Mode: Allow with warning (for demo purposes)
                        if payment_result['mock_mode']:
                            st.warning("🟡 **Mock Mode Active** - Continuing for demonstration purposes")
                            st.info("💡 In production mode, the answer would be withheld until payment succeeds.")
                        else:
                            # In Real Mode: ENFORCE x402 - No payment, no answer!
                            st.error("🚫 **x402 Protocol Enforced:** Answer withheld until authors are compensated.")
                            st.info("💡 Please ensure your wallet has sufficient CRO balance and try again.")
                            st.stop()  # Halt execution - true x402 behavior!
                
                except Exception as e:
                    st.error(f"❌ **Payment System Error:** {str(e)}")
                    st.error("🚫 Cannot proceed without functional payment system (x402 requirement)")
                    st.stop()
            
            # Display payment confirmation
            st.markdown(f"""
            <div class="payment-alert">
                <h4>⚡ x402 Payment Successful</h4>
                <div class="amount">{payment_result['total_paid']:.4f} CRO</div>
                <small>Paid to {payment_result['unique_authors']} unique author(s) 
                {'(Simulated)' if payment_result['mock_mode'] else '(On-Chain)'}</small>
            </div>
            """, unsafe_allow_html=True)
            
            # Update session stats
            st.session_state.total_payments += payment_result['total_paid']
            
            # Step 3: Generate AI answer (ONLY after successful payment!)
            with st.spinner("🤖 Generating answer with GPT-4o-mini..."):
                answer = generate_answer(prompt, sources)
            
            st.markdown("---")
            st.markdown("### 💡 Answer")
            st.markdown(answer)
            
            # Store message with metadata
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "metadata": {
                    "sources": sources,
                    "payment": payment_result
                }
            })
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.8rem;">
        <p>🏆 Built for the Cronos Hackathon | CogniShare Protocol</p>
        <p>Decentralized RAG • x402 Micropayments • Cronos EVM</p>
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# Entry Point
# =============================================================================
if __name__ == "__main__":
    main()

