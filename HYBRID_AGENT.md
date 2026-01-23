# 🤖 Hybrid Agent - Multi-Modal x402 Payments

## Overview

The **Hybrid Agent** extends CogniShare Protocol from a single-purpose RAG system to a **multi-modal AI agent** with dual payment models:

1. **Pay-per-Citation:** Authors earn CRO when their knowledge is cited (PDF content)
2. **Pay-per-Call:** Data providers earn CRO when their APIs are accessed (Live market data)

This creates a comprehensive x402 ecosystem where **all value is compensated** - both static knowledge and dynamic data.

---

## 🎯 Value Proposition

### **Problem:**
- Traditional AI agents access data for free
- Content creators aren't compensated
- Data providers have no revenue model
- No transparency in data usage

### **Solution:**
- **Every data access is paid** via x402
- **Transparent on-chain records** of all payments
- **Fair compensation** for both knowledge and data
- **Sustainable ecosystem** for AI services

---

## 💰 Dual Payment Model

### **Model 1: Knowledge Citations (Existing)**

**What:** PDF content ingested into RAG system

**Payment Trigger:** When AI cites the content in an answer

**Cost:** 0.01 CRO per citation

**Recipients:** Content authors (wallet provided at upload)

**Use Case:**
```
User: "What is decentralized AI?"
→ RAG finds relevant PDF chunks
→ Pay 0.01 CRO to each cited author
→ Generate answer with citations
```

---

### **Model 2: Live Data Access (NEW)**

**What:** Real-time cryptocurrency market data

**Payment Trigger:** When AI needs to fetch live data

**Cost:** 0.05 CRO per API call

**Recipients:** Data service providers

**Use Case:**
```
User: "What is the price of CRO?"
→ Detect market data request
→ Pay 0.05 CRO to data provider
→ Fetch live price from CoinGecko
→ Return formatted market data
```

---

## 🔧 Technical Implementation

### **New Components:**

#### **1. market_tool.py - Crypto Market Data Tool**

```python
class CryptoMarketTool:
    """
    Tool for accessing real-time cryptocurrency market data.
    Premium feature: 0.05 CRO per call
    """
    
    SERVICE_WALLET = "0x742d35Cc6634C0532925a3b844Bc9e7595f5bE21"
    CALL_COST_CRO = 0.05
    
    def get_price(self, symbol: str) -> Dict[str, Any]:
        """
        Get current market price for a cryptocurrency.
        
        Returns:
            - price_usd: float
            - price_change_24h: float
            - market_cap: float
            - volume_24h: float
            - formatted_message: str
            - requires_payment: bool (always True)
        """
    
    def is_market_query(self, user_query: str) -> bool:
        """
        Detect if user query requires market data.
        
        Keywords: price, cost, worth, market, trading, etc.
        Symbols: cro, bitcoin, ethereum, etc.
        """
    
    def extract_symbol_from_query(self, user_query: str) -> str:
        """Extract cryptocurrency symbol from query."""
```

**Supported Cryptocurrencies:**
- CRO / Cronos
- Bitcoin (BTC)
- Ethereum (ETH)
- BNB, Cardano (ADA), Solana (SOL)
- Polkadot (DOT), Dogecoin (DOGE)
- Polygon (MATIC)

---

#### **2. payment_manager.py - Service Fee Payment**

```python
def pay_service_fee(
    self,
    amount_cro: float,
    service_wallet: str,
    service_name: str = "Premium Service"
) -> Dict[str, Any]:
    """
    Pay a service fee for premium features.
    
    Extends x402 protocol to include:
    - API access fees
    - Computational resources
    - Data subscriptions
    
    Returns:
        - success: bool
        - tx_hash: str
        - amount: float
        - service: str
        - mock_mode: bool
    """
```

**Features:**
- ✅ Smart contract integration (if deployed)
- ✅ Direct transfer fallback
- ✅ Mock mode for testing
- ✅ Input validation
- ✅ Error handling

---

#### **3. app.py - Hybrid Query Processing**

**Flow Chart:**

```
User Query
    ↓
Is Market Query? (Check keywords + symbols)
    ├─ YES → Market Data Flow
    │   ↓
    │   1. Display: "Detected market data request"
    │   2. Pay 0.05 CRO to service provider
    │   3. Fetch live data from CoinGecko
    │   4. Display formatted market data
    │   5. Store in chat history
    │   └─ DONE
    │
    └─ NO → Normal RAG Flow
        ↓
        1. Search knowledge base
        2. Pay 0.01 CRO per cited author
        3. Generate AI answer
        4. Display with sources
        └─ DONE
```

---

## 🎨 User Interface

### **Sidebar - Premium Features Toggle**

```
⚡ Premium Features
─────────────────────────
☐ 📡 Live Market Data
  💰 Cost: 0.05 CRO per query
  📊 Provider: CoinGecko API
  
  💡 Enable for live crypto prices
```

**When Enabled:**
```
✅ Market data active
💰 Cost: 0.05 CRO per query
📊 Provider: CoinGecko API
```

---

### **Chat Interface - Market Query Example**

**User Input:**
```
What is the current price of CRO?
```

**Agent Response:**
```
🔍 Detected market data request

💰 Paying 0.05 CRO for Live Data Access...
✅ Paid 0.05 CRO for data access

📊 Fetching live data for CRO...
✅ Retrieved live market data for CRO

─────────────────────────────────────
🪙 CRO Market Data (Live)

💵 Current Price: $0.1234 USD
📈 24h Change: +5.67%
📊 Market Cap: $3,123,456,789 USD
💹 24h Volume: $123,456,789 USD

Data provided by CoinGecko API
─────────────────────────────────────

Based on live market data:
[Market data displayed above]

*This data was accessed via premium x402 service (0.05 CRO per call)*
```

---

## 🔄 Payment Flow Comparison

### **Knowledge Citation (RAG):**

```
1. User asks question
2. RAG searches PDF chunks
3. Finds 3 relevant sources
4. Extracts author wallets
5. PAY 0.01 CRO × 3 = 0.03 CRO
6. Generate answer with citations
7. Display sources + payment confirmation
```

**Total Cost:** 0.03 CRO (3 citations × 0.01)

---

### **Market Data Access:**

```
1. User asks "What's the price of CRO?"
2. Detect market query (keywords + symbol)
3. PAY 0.05 CRO to service provider
4. Fetch live data from CoinGecko API
5. Format and display market data
6. Store in chat history
```

**Total Cost:** 0.05 CRO (1 API call)

---

### **Hybrid Query (Both):**

```
1. User asks "Compare CRO price to what the whitepaper says"
2. Detect market query → PAY 0.05 CRO
3. Fetch CRO price
4. Search RAG for whitepaper content
5. Find 2 relevant chunks → PAY 0.02 CRO
6. Generate comparative answer
7. Display market data + citations
```

**Total Cost:** 0.07 CRO (0.05 + 0.02)

---

## 📊 Analytics Integration

### **New Metrics:**

**Session Stats:**
- Total Uploads: 5
- Total Paid Out: 0.12 CRO
  - Knowledge Citations: 0.07 CRO
  - Service Fees: 0.05 CRO

**Network Analytics:**
- Service Fee Payments: 3 calls
- Average Service Cost: 0.05 CRO
- Total Service Revenue: 0.15 CRO

---

## 🎯 Use Cases

### **1. Crypto Trading Assistant**

**Query:** "What's Bitcoin's price and what does our research say about it?"

**Agent Actions:**
1. Pay 0.05 CRO → Fetch BTC price ($45,000)
2. Pay 0.02 CRO → Cite 2 research papers
3. Generate: "Bitcoin is currently $45,000. According to our research [Author A], Bitcoin shows strong fundamentals..."

**Value:** Real-time data + historical knowledge

---

### **2. Market Analysis Bot**

**Query:** "Compare CRO, ETH, and BTC prices"

**Agent Actions:**
1. Pay 0.15 CRO → Fetch 3 prices (0.05 × 3)
2. Generate comparison table
3. Display: CRO $0.12, ETH $2,500, BTC $45,000

**Value:** Multi-asset analysis

---

### **3. Research + Market Combo**

**Query:** "What's Cronos EVM and how is CRO performing?"

**Agent Actions:**
1. Pay 0.05 CRO → Fetch CRO price
2. Pay 0.03 CRO → Cite 3 technical docs
3. Generate: Technical explanation + current market status

**Value:** Education + real-time context

---

## 🔐 Security Considerations

### **Payment Validation:**

```python
# Before accessing data
if amount_cro <= 0:
    return {"success": False, "error": "Invalid amount"}

if not is_valid_wallet(service_wallet):
    return {"success": False, "error": "Invalid wallet"}

# Execute payment
payment_result = pay_service_fee(...)

# Check success
if not payment_result['success']:
    if not mock_mode:
        st.stop()  # Halt execution
```

### **Rate Limiting:**

```python
# Prevent abuse
if market_tool.call_count > 100:
    st.warning("Daily limit reached")
    st.stop()
```

### **Input Sanitization:**

```python
# Validate symbol
symbol = symbol.lower().strip()
if symbol not in SUPPORTED_SYMBOLS:
    return {"error": "Unsupported symbol"}
```

---

## 🚀 Deployment

### **Step 1: Install Dependencies**

```bash
pip install pycoingecko
```

### **Step 2: Configure Service Wallet**

```python
# market_tool.py
SERVICE_WALLET = "0xYourServiceWallet..."  # Change this!
```

### **Step 3: Enable in UI**

1. Start app: `py -m streamlit run app.py`
2. Sidebar → Toggle "📡 Live Market Data"
3. Ask: "What is the price of CRO?"
4. See payment + data! 🎉

---

## 📈 Business Model

### **Revenue Streams:**

**For Platform:**
- Service fees (0.05 CRO per API call)
- Transaction fees (if using smart contract)
- Premium subscriptions (future)

**For Authors:**
- Citation fees (0.01 CRO per use)
- Passive income from knowledge
- Reputation building

**For Data Providers:**
- API access fees (0.05 CRO per call)
- Sustainable revenue model
- Pay-per-use pricing

---

## 🎓 Hackathon Advantages

### **Ecosystem Track Alignment:**

✅ **Multi-modal Agent:** RAG + Live Data  
✅ **Dual Payment Model:** Citations + Service Fees  
✅ **Real-world Use Case:** Crypto market data  
✅ **Scalable Architecture:** Easy to add more tools  
✅ **On-chain Verification:** All payments traceable  

### **Innovation Points:**

1. **First x402 implementation** with multiple payment types
2. **Hybrid AI agent** combining static + dynamic data
3. **Transparent pricing** (0.01 CRO vs 0.05 CRO)
4. **Production-ready** with mock mode fallback
5. **Extensible design** for future data sources

---

## 🔮 Future Extensions

### **More Data Sources:**

```python
# Weather data
weather_tool.get_forecast("New York")  # 0.02 CRO

# Stock prices
stock_tool.get_quote("AAPL")  # 0.05 CRO

# News feeds
news_tool.get_headlines("crypto")  # 0.03 CRO

# Social sentiment
sentiment_tool.analyze("CRO")  # 0.10 CRO
```

### **Dynamic Pricing:**

```python
# Based on data freshness
if real_time:
    cost = 0.05 CRO
elif cached_1h:
    cost = 0.02 CRO
elif cached_24h:
    cost = 0.01 CRO
```

### **Subscription Model:**

```python
# Monthly unlimited access
if has_premium_subscription:
    cost = 0 CRO  # Already paid monthly
else:
    cost = 0.05 CRO  # Pay-per-call
```

---

## 📚 API Reference

### **CryptoMarketTool**

```python
# Initialize
tool = CryptoMarketTool()

# Get price
result = tool.get_price("cro")
# Returns: {success, price_usd, price_change_24h, ...}

# Check if query needs market data
is_market = tool.is_market_query("What's the price of Bitcoin?")
# Returns: True

# Extract symbol
symbol = tool.extract_symbol_from_query("How much is CRO worth?")
# Returns: "cro"

# Get status
status = tool.get_status()
# Returns: {tool, status, cost_per_call, total_calls, ...}
```

### **Payment Manager**

```python
# Pay service fee
result = payment_manager.pay_service_fee(
    amount_cro=0.05,
    service_wallet="0x...",
    service_name="Market Data API"
)
# Returns: {success, tx_hash, amount, service, mock_mode}
```

---

## 🏆 Success Metrics

### **Technical:**
- ✅ Dual payment model implemented
- ✅ Market data integration working
- ✅ Smart contract compatible
- ✅ Mock mode for testing
- ✅ Error handling robust

### **User Experience:**
- ✅ Clear pricing (0.01 vs 0.05 CRO)
- ✅ Visual payment confirmations
- ✅ Formatted market data display
- ✅ Seamless hybrid queries

### **Ecosystem:**
- ✅ Multi-modal agent architecture
- ✅ Extensible for more data sources
- ✅ Fair compensation for all parties
- ✅ Transparent on-chain records

---

**🎉 CogniShare Protocol is now a full Hybrid Agent with multi-modal x402 payments!**

**Ecosystem Track: ✅ READY TO WIN** 🏆

