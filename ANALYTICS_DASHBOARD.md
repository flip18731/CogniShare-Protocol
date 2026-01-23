# 📊 Network Analytics Dashboard

## Overview

The **Network Analytics Dashboard** provides real-time insights into the CogniShare Protocol's on-chain activity. Built with Plotly and Streamlit, it offers a professional, Dune Analytics-style interface for monitoring citations, payments, and author earnings.

---

## 🎯 Features

### **1. Key Metrics (Big Number Cards)**

Four prominent metrics displayed at the top:

| Metric | Description | Data Source |
|--------|-------------|-------------|
| 💰 **Total Knowledge Value** | Total CRO paid to authors | Smart Contract + Session |
| ✅ **Verified Citations** | Number of on-chain citations | Smart Contract + Session |
| 👥 **Active Authors** | Unique authors who received payments | Session State |
| 📈 **Avg Payment** | Average CRO per citation | Calculated |

**Features:**
- Real-time updates
- Delta indicators (session vs total)
- Color-coded for quick scanning

---

### **2. Earnings per Author (Bar Chart)**

**Visualization:** Horizontal bar chart with gradient colors

**Data Shown:**
- Author wallet (shortened: `0x1234...abcd`)
- Total earnings in CRO
- Citation count (on hover)

**Features:**
- Color gradient based on earnings (Viridis scale)
- Hover tooltips with full details
- Auto-sorted by earnings (highest first)
- Dark theme for professional look

**Use Cases:**
- Identify top contributors
- Track author performance
- Verify fair distribution

---

### **3. Citations Over Time (Line Chart)**

**Visualization:** Cumulative line chart with markers

**Data Shown:**
- Timestamp of each query (HH:MM:SS)
- Cumulative citation count
- Growth trajectory

**Features:**
- Smooth line with markers
- Hover tooltips with exact values
- Real-time updates as queries happen
- Shows protocol adoption rate

**Use Cases:**
- Monitor protocol usage
- Identify peak activity times
- Demonstrate growth to stakeholders

---

### **4. Smart Contract Information**

**Displays:**
- ✅ Contract status (Active/Not Deployed)
- 📜 Contract address (with copy button)
- 🔍 Direct link to Cronos Explorer
- 🌐 Network information
- 🔢 Current block number
- ⛽ Gas price (in Gwei)

**Use Cases:**
- Quick contract verification
- Network health monitoring
- Gas price tracking for optimization

---

### **5. Detailed Author Statistics (Table)**

**Columns:**
- **Author:** Wallet address (shortened)
- **Citations:** Number of times cited
- **Earnings (CRO):** Total earnings
- **Avg per Citation:** Average payment

**Features:**
- Sortable by any column
- Searchable (Streamlit dataframe)
- Export-ready format
- Auto-updates with new data

---

## 🔄 Data Flow

### **Session State Tracking**

```python
# Initialized on app start
st.session_state.citation_timeline = []
st.session_state.author_earnings = {}

# Updated on each query
st.session_state.citation_timeline.append({
    "timestamp": datetime.now(),
    "citations": len(sources),
    "amount": payment_result['total_paid']
})

st.session_state.author_earnings[wallet] = {
    "earnings": 0.01 * citations,
    "citations": citations
}
```

### **Smart Contract Integration**

```python
# Fetch live data from blockchain
analytics = payment_manager.get_analytics_data()

# Returns:
{
    "total_citations": 42,           # From contract
    "total_paid_cro": 0.42,          # From contract
    "average_payment": 0.01,         # Calculated
    "block_number": 12345678,        # Current block
    "gas_price_gwei": 5000,          # Current gas
    "contract_address": "0x...",     # Contract addr
    "status": "Live"                 # Status
}
```

---

## 🎨 Visual Design

### **Color Scheme**

| Element | Color | Purpose |
|---------|-------|---------|
| Background | Dark (`#0e1117`) | Professional, easy on eyes |
| Primary Accent | Green (`#00ff88`) | Success, growth |
| Secondary Accent | Purple (`#e94560`) | Highlights, warnings |
| Charts | Viridis Gradient | Data visualization |
| Text | Light Gray (`#fafafa`) | Readability |

### **Typography**

- **Headers:** Space Grotesk (bold, modern)
- **Metrics:** Large numbers with units
- **Charts:** JetBrains Mono for data labels
- **Captions:** Small, gray, informative

---

## 📈 Chart Specifications

### **Bar Chart (Earnings)**

```python
fig_earnings = go.Figure()

fig_earnings.add_trace(go.Bar(
    x=authors,                    # Wallet addresses
    y=earnings,                   # CRO amounts
    text=[f"{e:.4f} CRO" for e in earnings],
    textposition='auto',
    marker=dict(
        color=earnings,           # Color by value
        colorscale='Viridis',     # Professional gradient
        showscale=False
    ),
    hovertemplate='<b>%{x}</b><br>Earnings: %{y:.4f} CRO<br>Citations: %{customdata}<extra></extra>',
    customdata=citations
))

fig_earnings.update_layout(
    xaxis_title="Author Wallet",
    yaxis_title="Earnings (CRO)",
    height=400,
    template="plotly_dark",
    showlegend=False
)
```

### **Line Chart (Timeline)**

```python
fig_timeline = go.Figure()

fig_timeline.add_trace(go.Scatter(
    x=timestamps,                 # Time series
    y=cumulative_citations,       # Running total
    mode='lines+markers',
    name='Citations',
    line=dict(color='#00ff88', width=3),
    marker=dict(size=8),
    hovertemplate='<b>%{x}</b><br>Total Citations: %{y}<extra></extra>'
))

fig_timeline.update_layout(
    xaxis_title="Time",
    yaxis_title="Cumulative Citations",
    height=400,
    template="plotly_dark"
)
```

---

## 🔄 Refresh Mechanism

**Button:** 🔄 Refresh Data

**Action:** `st.rerun()`

**Effect:**
1. Re-fetches data from smart contract
2. Recalculates all metrics
3. Redraws all charts
4. Updates session state

**Use Case:** Get latest on-chain data without full page reload

---

## 📊 Data Sources

| Metric | Source | Update Frequency |
|--------|--------|------------------|
| Total Citations (On-Chain) | Smart Contract | On refresh |
| Total Paid (On-Chain) | Smart Contract | On refresh |
| Session Citations | Session State | Real-time |
| Session Payments | Session State | Real-time |
| Author Earnings | Session State | Real-time |
| Citation Timeline | Session State | Real-time |
| Block Number | Blockchain | On refresh |
| Gas Price | Blockchain | On refresh |

---

## 🎯 Use Cases

### **For Hackathon Demo:**

1. **Show Growth:**
   - Ask 3-5 questions
   - Show timeline chart growing
   - Highlight cumulative value

2. **Prove Fairness:**
   - Show earnings bar chart
   - Explain distribution logic
   - Demonstrate transparency

3. **Verify On-Chain:**
   - Click "View on Explorer"
   - Show Citation events
   - Prove immutability

### **For Production:**

1. **Author Dashboard:**
   - Authors track their earnings
   - See citation frequency
   - Monitor performance

2. **Protocol Analytics:**
   - Track total value locked
   - Monitor adoption rate
   - Identify top contributors

3. **Governance:**
   - Data-driven decisions
   - Fair reward distribution
   - Protocol health monitoring

---

## 🛠️ Technical Implementation

### **Dependencies Added:**

```python
# requirements.txt
plotly>=5.18.0
```

### **Imports Added:**

```python
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
```

### **New Methods:**

**payment_manager.py:**
- `get_analytics_data()` - Fetch smart contract metrics
- `get_author_stats(address)` - Get per-author statistics

**app.py:**
- Session state tracking for analytics
- Tab-based navigation
- Plotly chart generation
- Real-time data updates

---

## 📱 Responsive Design

**Desktop (>1200px):**
- 4 metric columns
- 2 chart columns side-by-side
- Full-width table

**Tablet (768px - 1200px):**
- 2 metric columns
- 2 chart columns
- Full-width table

**Mobile (<768px):**
- 1 metric column (stacked)
- 1 chart column (stacked)
- Scrollable table

---

## 🎨 Customization

### **Change Color Scheme:**

```python
# In chart creation
marker=dict(
    color=earnings,
    colorscale='Plasma',  # Try: Viridis, Plasma, Inferno, Magma
    showscale=False
)
```

### **Add More Metrics:**

```python
# In session state
if "new_metric" not in st.session_state:
    st.session_state.new_metric = 0

# In metrics section
st.metric(
    label="🆕 New Metric",
    value=st.session_state.new_metric
)
```

### **Add More Charts:**

```python
# Pie chart example
fig_pie = go.Figure(data=[go.Pie(
    labels=authors,
    values=earnings,
    hole=.3  # Donut chart
)])

st.plotly_chart(fig_pie, use_container_width=True)
```

---

## 🐛 Troubleshooting

### **Charts Not Showing:**

**Issue:** Plotly not installed

**Fix:**
```bash
pip install plotly
```

### **No Data in Charts:**

**Issue:** No queries made yet

**Fix:** Ask a question in the Chat tab first

### **Contract Data Not Loading:**

**Issue:** Smart contract not deployed

**Fix:**
```bash
python deploy_contract.py
```

### **Refresh Not Working:**

**Issue:** Browser cache

**Fix:** Hard refresh (Ctrl+Shift+R)

---

## 📈 Future Enhancements

### **Planned Features:**

1. **Event Log Viewer:**
   - Query Citation events from blockchain
   - Show transaction details
   - Filter by author/date

2. **Export Functionality:**
   - Download charts as PNG
   - Export data as CSV
   - Generate PDF reports

3. **Advanced Filters:**
   - Date range selector
   - Author filter
   - Amount range filter

4. **Comparison Mode:**
   - Compare authors
   - Compare time periods
   - Benchmark metrics

5. **Alerts:**
   - Low balance warnings
   - High gas price alerts
   - Milestone notifications

---

## 🏆 Hackathon Impact

**Before Analytics Dashboard:**
- ✅ Payments work
- ❌ No visibility into protocol activity
- ❌ Can't track growth
- ❌ No author insights

**After Analytics Dashboard:**
- ✅ Payments work
- ✅ **Real-time protocol monitoring**
- ✅ **Visual growth demonstration**
- ✅ **Author performance tracking**
- ✅ **Professional presentation**

**Demo Impact:** +50% wow factor! 🚀

---

## 📚 Resources

- **Plotly Docs:** https://plotly.com/python/
- **Streamlit Docs:** https://docs.streamlit.io/
- **Cronos Explorer:** https://explorer.cronos.org/testnet3

---

**Built with ❤️ for the Cronos Hackathon**

