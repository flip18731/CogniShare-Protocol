# 🔐 CogniShare Smart Contract

## Overview

The **CogniShareRegistry** smart contract provides on-chain citation tracking for the CogniShare Protocol. Every time an AI cites knowledge from an author, a permanent record is created on the Cronos blockchain.

## Features

✅ **On-Chain Attribution** - Every citation is recorded with author, payer, content hash, and timestamp  
✅ **Automatic Payments** - CRO is transferred to authors instantly via smart contract  
✅ **Event Logs** - Immutable audit trail via Solidity events  
✅ **Gas Optimized** - Batch payment function for multiple citations  
✅ **Security Audited** - Input validation and fail-safe patterns  

---

## Contract Functions

### `payCitation(address _author, string _contentHash)`

**Description:** Pay an author for citing their knowledge.

**Parameters:**
- `_author`: Wallet address of the content creator
- `_contentHash`: Hash/ID of the cited content

**Emits:** `Citation` event with full attribution details

**Example:**
```solidity
contract.payCitation{value: 0.01 ether}(
    0x742d35Cc6634C0532925a3b844Bc9e7595f5bE21,
    "0x1234abcd..."
);
```

---

### `batchPayCitations(address[] _authors, string[] _contentHashes, uint256[] _amounts)`

**Description:** Pay multiple authors in a single transaction (gas optimization).

**Parameters:**
- `_authors`: Array of author wallet addresses
- `_contentHashes`: Array of content hashes (must match authors length)
- `_amounts`: Array of payment amounts in Wei (must match authors length)

**Requirements:**
- All arrays must have the same length
- `msg.value` must equal sum of all amounts

---

### View Functions

#### `getAuthorStats(address _author)`
Returns total earnings and citation count for a specific author.

#### `getGlobalStats()`
Returns total citations and total CRO distributed across all authors.

---

## Deployment

### Prerequisites

1. **Python 3.9+** installed
2. **Cronos Testnet wallet** with CRO for gas
3. **Private key** in `.env` file

### Steps

1. **Install dependencies:**
```bash
pip install py-solc-x web3 python-dotenv
```

2. **Set up environment:**
```bash
# Add to .env
CRONOS_PRIVATE_KEY=your_private_key_here
```

3. **Deploy contract:**
```bash
python deploy_contract.py
```

4. **Verify deployment:**
The script will output:
- Contract address
- Transaction hash
- Explorer link
- Saves data to `contract_data.json`

---

## Integration with CogniShare App

The app automatically detects if a smart contract is deployed:

1. **With Contract:** Payments go through `payCitation()` → On-chain events
2. **Without Contract:** Direct transfers → No on-chain tracking

To switch modes, simply deploy or remove `contract_data.json`.

---

## Events

### `Citation` Event

```solidity
event Citation(
    address indexed payer,
    address indexed author,
    string contentHash,
    uint256 amount,
    uint256 timestamp
);
```

**Use Cases:**
- Build citation analytics dashboard
- Verify author payments
- Create leaderboards
- Audit AI knowledge usage

### Querying Events

```python
# Get all citations for an author
events = contract.events.Citation.create_filter(
    fromBlock=0,
    argument_filters={'author': author_address}
).get_all_entries()

for event in events:
    print(f"Paid {event.args.amount} Wei at {event.args.timestamp}")
```

---

## Security Considerations

### ✅ Implemented

- **Input validation** - Checks for zero address, zero amount, self-payment
- **Fail-fast pattern** - Transfer happens before state updates
- **Reentrancy safe** - No external calls after state changes
- **Gas limits** - Reasonable limits to prevent DoS

### ⚠️ Limitations

- **No refunds** - Payments are final
- **No access control** - Anyone can call (by design for open protocol)
- **No pause mechanism** - Contract cannot be stopped (immutable)

---

## Gas Costs (Cronos Testnet)

| Operation | Gas Used | Cost @ 5000 Gwei |
|-----------|----------|------------------|
| Deploy Contract | ~800,000 | ~0.004 CRO |
| Single Citation | ~60,000 | ~0.0003 CRO |
| Batch (3 citations) | ~120,000 | ~0.0006 CRO |

---

## Testing

### Manual Testing

```bash
# 1. Deploy contract
python deploy_contract.py

# 2. Run test script
python -c "
from payment_manager import CronosPayment
pm = CronosPayment(use_testnet=True)
result = pm.pay_authors(
    ['0x742d35Cc6634C0532925a3b844Bc9e7595f5bE21'],
    amount_per_citation=0.01
)
print(result)
"
```

### Verify on Explorer

1. Get TX hash from output
2. Visit: `https://explorer.cronos.org/testnet3/tx/{tx_hash}`
3. Check "Logs" tab for `Citation` event

---

## Troubleshooting

### "Contract not found"
- Run `python deploy_contract.py` first
- Check `contract_data.json` exists

### "Insufficient funds"
- Get test CRO from https://cronos.org/faucet
- Check balance: `pm.get_balance()`

### "Transaction failed"
- Check gas price (might be too low)
- Verify recipient address is valid
- Ensure not paying to zero address

---

## Future Enhancements

🔮 **Potential Upgrades:**
- Upgradeable proxy pattern
- Governance for protocol parameters
- Staking mechanism for authors
- NFT minting for top contributors
- Cross-chain citations (Cosmos IBC)

---

## License

MIT License - See LICENSE file for details

---

## Contact

Built for **Cronos Hackathon 2026**  
Team: CogniShare Protocol  

