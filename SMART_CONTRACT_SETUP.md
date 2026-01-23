# 🚀 Smart Contract Setup Guide

## Quick Start: Deploy CogniShareRegistry

This guide walks you through deploying the smart contract to enable **on-chain citation tracking**.

---

## 📋 Prerequisites

### 1. Install New Dependencies

```bash
pip install py-solc-x
```

### 2. Verify Environment

Make sure your `.env` has:
```env
CRONOS_PRIVATE_KEY=your_private_key_here
```

### 3. Get Test CRO

Visit: https://cronos.org/faucet  
Request test CRO for deployment gas (~0.005 CRO needed)

---

## 🔧 Deployment Steps

### Step 1: Run Deployment Script

```bash
python deploy_contract.py
```

**Expected Output:**
```
🚀 CogniShare Contract Deployer
============================================================
📡 Connecting to Cronos Testnet...
✅ Connected to Cronos Testnet (Chain ID: 338)
💳 Deployer Address: 0x...
💰 Balance: 1.2345 CRO

📝 Compiling Smart Contract...
------------------------------------------------------------
🔧 Installing Solidity compiler v0.8.20...
✅ Compilation successful!

🚀 Deploying Contract to Cronos Testnet...
------------------------------------------------------------
📤 Broadcasting transaction...
⏳ Waiting for confirmation...

============================================================
✅ CONTRACT DEPLOYED SUCCESSFULLY!
============================================================
📍 Contract Address: 0x1234567890abcdef...
🔗 TX Hash: 0xabcdef123456...
⛽ Gas Used: 789,456
🔍 Explorer: https://explorer.cronos.org/testnet3/tx/0x...
============================================================

💾 Saving Deployment Data...
✅ Saved to: contract_data.json

🔍 Verifying Deployment...
✅ Contract code verified (12,345 bytes)
✅ Contract is functional
   Total Citations: 0
   Total Paid: 0 Wei

============================================================
🎉 DEPLOYMENT COMPLETE!
============================================================
```

### Step 2: Verify Files Created

```bash
ls -la
```

You should see:
- ✅ `contract_data.json` - Contract address & ABI
- ✅ `contract_data.backup.json` - Backup copy

### Step 3: Restart the App

```bash
# Stop current app (Ctrl+C)
py -m streamlit run app.py
```

The app will automatically detect and use the smart contract!

---

## 🎯 How to Verify It's Working

### In the App UI

1. **Check Status Indicator:**
   - Sidebar → "System Status"
   - Should show: `Smart Contract: 0x1234...`

2. **Make a Test Query:**
   - Ask any question
   - Payment will go through smart contract
   - TX hash will be different format

3. **Check Explorer:**
   - Copy TX hash from payment
   - Visit: `https://explorer.cronos.org/testnet3/tx/{hash}`
   - Click "Logs" tab
   - You'll see `Citation` event! 🎉

---

## 📊 Contract vs Direct Transfer Comparison

| Feature | Direct Transfer | Smart Contract |
|---------|----------------|----------------|
| **Speed** | Fast (~3s) | Fast (~3s) |
| **Gas Cost** | 21,000 gas | ~60,000 gas |
| **On-Chain Record** | ❌ No | ✅ Yes (Events) |
| **Attribution** | ❌ No | ✅ Yes (Content Hash) |
| **Analytics** | ❌ No | ✅ Yes (Query Events) |
| **Audit Trail** | ❌ No | ✅ Yes (Immutable) |

---

## 🔄 Switching Between Modes

### Use Smart Contract (Default after deployment)
```bash
# Just have contract_data.json present
ls contract_data.json  # Should exist
```

### Use Direct Transfers (Fallback)
```bash
# Temporarily rename the file
mv contract_data.json contract_data.json.disabled
```

### Re-enable Smart Contract
```bash
mv contract_data.json.disabled contract_data.json
```

---

## 🐛 Troubleshooting

### Error: "Could not install solc"

**Solution 1 - Manual Install:**
```bash
pip install py-solc-x --upgrade
python -c "from solcx import install_solc; install_solc('0.8.20')"
```

**Solution 2 - Use Pre-compiled:**
Download from: https://github.com/ethereum/solidity/releases/tag/v0.8.20

---

### Error: "Insufficient funds for gas"

**Check Balance:**
```python
from payment_manager import CronosPayment
pm = CronosPayment()
print(f"Balance: {pm.get_balance()} CRO")
```

**Get More CRO:**
https://cronos.org/faucet

---

### Error: "Contract deployment failed"

**Common Causes:**
1. **Network congestion** - Wait 30s and retry
2. **Gas price too low** - Script auto-adjusts, should work
3. **Invalid private key** - Check `.env` file

**Debug:**
```bash
python deploy_contract.py 2>&1 | tee deploy.log
```

---

### Warning: "Contract found but not accessible"

**Possible Causes:**
1. Contract deployed on different network (mainnet vs testnet)
2. RPC endpoint changed
3. Contract address wrong in `contract_data.json`

**Fix:**
```bash
# Re-deploy fresh
rm contract_data.json
python deploy_contract.py
```

---

## 📈 Monitoring Contract Activity

### Get Global Stats

```python
from payment_manager import CronosPayment

pm = CronosPayment(use_testnet=True)
status = pm.get_status()

if status['smart_contract']:
    print(f"Contract: {status['contract_address']}")
    print(f"Total Citations: {status['total_citations_onchain']}")
    print(f"Total Paid: {status['total_paid_onchain']} CRO")
```

### Query Citation Events

```python
from web3 import Web3
import json

# Load contract
with open('contract_data.json') as f:
    data = json.load(f)

w3 = Web3(Web3.HTTPProvider('https://evm-t3.cronos.org'))
contract = w3.eth.contract(address=data['address'], abi=data['abi'])

# Get all citations
events = contract.events.Citation.create_filter(fromBlock=0).get_all_entries()

for event in events:
    print(f"Author: {event.args.author}")
    print(f"Amount: {w3.from_wei(event.args.amount, 'ether')} CRO")
    print(f"Content: {event.args.contentHash}")
    print(f"Time: {event.args.timestamp}")
    print("-" * 60)
```

---

## 🏆 For Hackathon Demo

### Impressive Talking Points

1. **"Every citation is on-chain"**
   - Show event logs in explorer
   - Explain immutable audit trail

2. **"Gas-optimized batch payments"**
   - Mention `batchPayCitations` function
   - Show gas comparison

3. **"Production-ready security"**
   - Input validation
   - Fail-fast pattern
   - Reentrancy protection

4. **"Analytics-ready"**
   - Query events for dashboards
   - Author leaderboards
   - Citation tracking

### Demo Flow

```
1. "Let me show you the smart contract" 
   → Open contracts/CogniShareRegistry.sol

2. "Here's the deployment"
   → Show contract_data.json with address

3. "Let's make a citation"
   → Ask question in app

4. "And here's the on-chain proof"
   → Open TX in Cronos Explorer
   → Show Citation event in Logs tab

5. "This is how we decentralize AI attribution"
   → Explain x402 + blockchain = transparent payments
```

---

## 🎓 Advanced: Custom Contract Modifications

### Add New Features

1. Edit `contracts/CogniShareRegistry.sol`
2. Add your function (e.g., `withdrawFees()`)
3. Re-deploy:
   ```bash
   rm contract_data.json
   python deploy_contract.py
   ```
4. Update `payment_manager.py` to use new function

### Example: Add Pause Mechanism

```solidity
// Add to contract
bool public paused = false;
address public owner;

constructor() {
    owner = msg.sender;
}

modifier whenNotPaused() {
    require(!paused, "Contract is paused");
    _;
}

function pause() external {
    require(msg.sender == owner, "Only owner");
    paused = true;
}

function payCitation(...) external payable whenNotPaused {
    // existing code
}
```

---

## 📚 Resources

- **Cronos Docs:** https://docs.cronos.org/
- **Solidity Docs:** https://docs.soliditylang.org/
- **Web3.py Docs:** https://web3py.readthedocs.io/
- **Cronos Explorer:** https://explorer.cronos.org/testnet3

---

## ✅ Success Checklist

- [ ] `py-solc-x` installed
- [ ] `.env` has `CRONOS_PRIVATE_KEY`
- [ ] Wallet has test CRO (>0.01)
- [ ] `python deploy_contract.py` runs successfully
- [ ] `contract_data.json` created
- [ ] App shows "Smart Contract: 0x..."
- [ ] Test payment creates Citation event
- [ ] Event visible in Cronos Explorer

---

**🎉 Congratulations! Your citations are now on-chain!**

