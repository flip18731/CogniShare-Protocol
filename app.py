"""
=============================================================================
CogniShare Protocol - Streamlit UI (Final Hackathon Version)
=============================================================================
"""

import os
import time
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv
import plotly.graph_objects as go
import pandas as pd

# Import Custom Modules
from rag_core import RAGEngine
from payment_manager import CronosPayment
from market_tool import CryptoMarketTool

# Load env
load_dotenv()

# =============================================================================
# Page Config & Styling
# =============================================================================
st.set_page_config(
    page_title="CogniShare Protocol",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');
    
    .stApp { font-family: 'Space Grotesk', sans-serif; }
    
    .hero-banner {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        border-radius: 16px; padding: 2rem; margin-bottom: 2rem;
        border: 1px solid #e94560; box-shadow: 0 0 30px rgba(233, 69, 96, 0.2);
    }
    .hero-title {
        font-size: 2.5rem; font-weight: 700;
        background: linear-gradient(90deg, #e94560, #ff6b6b, #feca57);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .payment-alert {
        background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
        border-left: 4px solid #00ff88; border-radius: 8px; padding: 1rem; margin: 1rem 0;
    }
    .payment-alert .amount { font-size: 1.5rem; color: #00ff88; font-weight: 600; }
    
    .source-card {
        background: #1a1a2e; border: 1px solid #3a3a5a; border-radius: 8px; padding: 1rem; margin: 0.5rem 0;
    }
    .wallet-badge {
        background: #16213e; border: 1px solid #e94560; border-radius: 20px;
        padding: 0.25rem 0.75rem; font-family: 'JetBrains Mono'; font-size: 0.8rem; color: #e94560;
    }
    .status-online { color: #00ff88; }
    .status-offline { color: #ff6b6b; }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# Initialization
# =============================================================================
if "messages" not in st.session_state: st.session_state.messages = []
if "total_payments" not in st.session_state: st.session_state.total_payments = 0.0
if "market_tool_enabled" not in st.session_state: st.session_state.market_tool_enabled = False
if "citation_timeline" not in st.session_state: st.session_state.citation_timeline = []
if "author_earnings" not in st.session_state: st.session_state.author_earnings = {}

@st.cache_resource
def get_engines():
    return RAGEngine(), CronosPayment(use_testnet=True), CryptoMarketTool()

rag_engine, payment_manager, market_tool = get_engines()

def generate_answer(query: str, context_chunks: list) -> str:
    """Generate answer using OpenAI."""
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key: return "⚠️ OpenAI Key missing."
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=openai_key)
        
        context_text = "\n\n".join([f"Source (Author: {c['author_wallet']}):\n{c['text']}" for c in context_chunks])
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are CogniShare AI. Use the provided context to answer. Authors are paid via x402."},
                {"role": "user", "content": f"Context:\n{context_text}\n\nQuestion: {query}"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# =============================================================================
# Main UI
# =============================================================================
def main():
    # --- Sidebar ---
    with st.sidebar:
        st.header("⚙️ Config")
        
        # Status
        st.subheader("System Status")
        rag_stats = rag_engine.get_stats()
        st.markdown(f"**Vector DB:** {'🟢 Pinecone' if rag_stats['pinecone_connected'] else '🟡 Mock'}")
        
        pay_status = payment_manager.get_status()
        if pay_status.get("smart_contract"):
            st.markdown(f"**Payment:** 🟢 Smart Contract")
            st.caption(f"Contract: `{pay_status['contract_address'][:8]}...`")
        else:
            st.markdown(f"**Payment:** {'🟡 Mock Mode' if pay_status['mock_mode'] else '🟢 Direct Transfer'}")
            
        # Upload
        st.divider()
        st.subheader("📤 Upload Knowledge")
        author_wallet = st.text_input("Author Wallet (0x...)", placeholder="0x...")
        
        # --- NEW: Tabs for Input Method ---
        input_tab1, input_tab2 = st.tabs(["📄 PDF File", "✍️ Paste Text"])
        
        with input_tab1:
            uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
            if st.button("🚀 Ingest PDF", use_container_width=True):
                if uploaded_file and author_wallet:
                    with st.spinner("Ingesting PDF..."):
                        try:
                            res = rag_engine.ingest_document(uploaded_file, author_wallet)
                            st.success(f"Indexed {res['chunks_created']} chunks!")
                        except Exception as e:
                            st.error(f"Error: {e}")
                else:
                    st.error("Missing wallet or file.")
        
        with input_tab2:
            text_input = st.text_area("Enter Knowledge directly", height=150, placeholder="Paste article text here...")
            if st.button("🚀 Ingest Text", use_container_width=True):
                if text_input and author_wallet:
                    with st.spinner("Ingesting Text..."):
                        try:
                            res = rag_engine.ingest_text(text_input, author_wallet)
                            st.success(f"Indexed {res['chunks_created']} chunks!")
                        except Exception as e:
                            st.error(f"Error: {e}")
                else:
                    st.error("Missing wallet or text.")

        # Premium Toggle
        st.divider()
        st.subheader("⚡ Premium")
        st.session_state.market_tool_enabled = st.toggle("Enable Market Data (0.05 CRO)", value=st.session_state.market_tool_enabled)

    # --- Main Content ---
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">🧠 CogniShare Protocol</div>
        <div class="hero-subtitle">Decentralized RAG • x402 Micropayments • Cronos EVM</div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["💬 Chat & Agent", "📊 Network Analytics"])

    # --- TAB 1: Chat ---
    with tab1:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if "payment" in msg.get("metadata", {}):
                    p = msg["metadata"]["payment"]
                    st.markdown(f"""<div class="payment-alert">⚡ <b>Paid {p['total_paid']:.4f} CRO</b> to {p['unique_authors']} authors</div>""", unsafe_allow_html=True)

        if prompt := st.chat_input("Ask about uploaded documents or crypto prices..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)

            with st.chat_message("assistant"):
                # 1. Check Market Tool (Premium)
                if st.session_state.market_tool_enabled and market_tool.is_market_query(prompt):
                    symbol = market_tool.extract_symbol_from_query(prompt)
                    with st.spinner(f"💰 Paying 0.05 CRO service fee for {symbol}..."):
                        # Pay Fee
                        fee_res = payment_manager.pay_service_fee(0.05, market_tool.SERVICE_WALLET, "Market Data")
                        
                        if fee_res['success']:
                            st.success(f"✅ Service Fee Paid! TX: {fee_res['tx_hash'][:10]}...")
                            data = market_tool.get_price(symbol)
                            response = f"**Live Market Data:**\n\n{data['formatted_message']}"
                            st.markdown(response)
                            st.session_state.messages.append({"role": "assistant", "content": response})
                        else:
                            st.error("Payment failed. Cannot access premium data.")
                
                # 2. Standard RAG Flow
                else:
                    with st.spinner("🔍 Searching Knowledge Base..."):
                        sources = rag_engine.query(prompt)
                    
                    with st.spinner("⚡ Processing x402 Micropayments..."):
                        # Pay Authors
                        pay_res = payment_manager.pay_authors_with_content(sources, 0.01)
                    
                    if pay_res['success'] or pay_res['mock_mode']:
                        # Show Payment Success
                        st.markdown(f"""
                        <div class="payment-alert">
                            <h4>⚡ x402 Payment Successful</h4>
                            <div class="amount">{pay_res['total_paid']:.4f} CRO</div>
                            <small>Transferred to Authors via Smart Contract</small>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if pay_res['tx_hashes']:
                            with st.expander("🔗 View On-Chain Transactions"):
                                for tx in pay_res['tx_hashes']:
                                    url = payment_manager.get_explorer_url(tx['tx_hash'])
                                    st.markdown(f"- Paid {tx['amount']} CRO: [{tx['tx_hash'][:10]}...]({url})")

                        # Track Stats
                        st.session_state.total_payments += pay_res['total_paid']
                        st.session_state.citation_timeline.append({
                            "time": datetime.now(), "amount": pay_res['total_paid']
                        })
                        for s in sources:
                            w = s['author_wallet']
                            if w not in st.session_state.author_earnings: st.session_state.author_earnings[w] = 0.0
                            st.session_state.author_earnings[w] += 0.01

                        # Generate Answer
                        with st.spinner("🤖 Generating answer..."):
                            answer = generate_answer(prompt, sources)
                            st.markdown(answer)
                            st.session_state.messages.append({
                                "role": "assistant", 
                                "content": answer, 
                                "metadata": {"payment": pay_res}
                            })
                    else:
                        st.error("🚫 **x402 Enforced:** Payment failed. Answer withheld.")

    # --- TAB 2: Analytics ---
    with tab2:
        st.subheader("📊 Network Analytics")
        analytics = payment_manager.get_analytics_data()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Value Transferred", f"{analytics['total_paid_cro']:.4f} CRO")
        c2.metric("Total Citations", analytics['total_citations'])
        c3.metric("Active Authors", len(st.session_state.author_earnings))
        
        st.divider()
        
        c_chart1, c_chart2 = st.columns(2)
        with c_chart1:
            st.markdown("#### 💸 Author Earnings")
            if st.session_state.author_earnings:
                df = pd.DataFrame(list(st.session_state.author_earnings.items()), columns=['Wallet', 'CRO'])
                st.bar_chart(df.set_index('Wallet'))
            else:
                st.info("No earnings data yet.")
                
        with c_chart2:
            st.markdown("#### 📈 Citation Velocity")
            if st.session_state.citation_timeline:
                df_time = pd.DataFrame(st.session_state.citation_timeline)
                st.line_chart(df_time.set_index('time')['amount'])
            else:
                st.info("Waiting for citations...")

if __name__ == "__main__":
    main()