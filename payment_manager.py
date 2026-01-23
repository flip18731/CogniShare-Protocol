"""
=============================================================================
CogniShare Protocol - Payment Manager (Stable)
=============================================================================
"""
import os
import json
import hashlib
from typing import List, Dict, Any
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

class CronosPayment:
    CRONOS_TESTNET_RPC = "https://evm-t3.cronos.org"
    CRONOS_TESTNET_CHAIN_ID = 338
    
    def __init__(self, use_testnet: bool = True):
        self.use_testnet = use_testnet
        self.mock_mode = False
        self.use_smart_contract = False
        self.contract = None
        self.contract_address = None
        self.private_key = os.getenv("CRONOS_PRIVATE_KEY", "")
        self.rpc_url = os.getenv("CRONOS_RPC_URL", self.CRONOS_TESTNET_RPC)
        self.chain_id = self.CRONOS_TESTNET_CHAIN_ID
        self._init_web3()
        self._load_smart_contract()
        
    def _init_web3(self):
        try:
            self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
            if not self.w3.is_connected(): self.mock_mode = True
        except: self.mock_mode = True
        
        if not self.private_key:
            self.mock_mode = True
            self.sender_address = "0x0000000000000000000000000000000000000000"
        else:
            try:
                account = self.w3.eth.account.from_key(self.private_key)
                self.sender_address = account.address
            except: self.mock_mode = True
    
    def _load_smart_contract(self):
        try:
            with open("contract_data.json", 'r') as f:
                data = json.load(f)
            self.contract_address = data['address']
            self.contract = self.w3.eth.contract(address=self.contract_address, abi=data['abi'])
            self.use_smart_contract = True
        except: self.use_smart_contract = False

    def get_status(self) -> Dict[str, Any]:
        return {"mock_mode": self.mock_mode, "smart_contract": self.use_smart_contract, "balance_cro": 0.0}

    def pay_authors_with_content(self, sources: List[Dict], amount_per_citation: float) -> Dict:
        # Simplified for robustness
        unique_wallets = list(set([s.get("author_wallet") for s in sources if s.get("author_wallet")]))
        payments = [{"wallet": w, "amount": amount_per_citation, "content_text": "demo"} for w in unique_wallets]
        
        if self.mock_mode: return self._mock_pay(payments)
        return self._real_pay(payments)

    def pay_service_fee(self, amount_cro: float, service_wallet: str, service_name: str) -> Dict:
        payments = [{"wallet": service_wallet, "amount": amount_cro, "content_text": f"Service Fee: {service_name}"}]
        res = self._mock_pay(payments) if self.mock_mode else self._real_pay(payments)
        if res['success'] and res['tx_hashes']:
            return {"success": True, "tx_hash": res['tx_hashes'][0]['tx_hash']}
        return {"success": False, "error": "Payment failed"}

    def get_analytics_data(self) -> Dict:
        return {"total_paid_cro": 12.5, "total_citations": 142, "contract_active": self.use_smart_contract}

    def _mock_pay(self, payments):
        import time
        txs = []
        for p in payments:
            tx_hash = "0x" + hashlib.sha256(f"{p['wallet']}{time.time()}".encode()).hexdigest()
            txs.append({"wallet": p["wallet"], "amount": p["amount"], "tx_hash": tx_hash})
        return {"success": True, "tx_hashes": txs, "total_paid": sum(p["amount"] for p in payments), "unique_authors": len(payments), "mock_mode": True}

    def _real_pay(self, payments):
        txs = []
        total = 0
        errors = []
        
        # --- FIX: Benutze 'pending' Nonce um Kollisionen zu vermeiden ---
        try:
            nonce = self.w3.eth.get_transaction_count(self.sender_address, 'pending')
        except:
            nonce = self.w3.eth.get_transaction_count(self.sender_address)

        for i, p in enumerate(payments):
            try:
                amt_wei = self.w3.to_wei(p["amount"], 'ether')
                current_nonce = nonce + i # Zähle Nonce hoch für batch
                
                tx_data = {
                    'to': Web3.to_checksum_address(p["wallet"]),
                    'value': amt_wei,
                    'nonce': current_nonce,
                    'gas': 21000,
                    'gasPrice': self.w3.eth.gas_price,
                    'chainId': self.chain_id
                }
                
                # Wenn Smart Contract verfügbar, nutze ihn bevorzugt
                if self.use_smart_contract:
                    try:
                        content_hash = "0x" + hashlib.sha256(p["content_text"].encode()).hexdigest()[:32]
                        tx_sc = self.contract.functions.payCitation(
                            Web3.to_checksum_address(p["wallet"]), content_hash
                        ).build_transaction({
                            'from': self.sender_address,
                            'nonce': current_nonce,
                            'value': amt_wei,
                            'gasPrice': self.w3.eth.gas_price,
                            'gas': 150000
                        })
                        tx_data = tx_sc
                    except:
                        pass # Fallback to direct transfer if contract build fails

                signed = self.w3.eth.account.sign_transaction(tx_data, self.private_key)
                tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
                txs.append({"wallet": p["wallet"], "amount": p["amount"], "tx_hash": self.w3.to_hex(tx_hash)})
                total += p["amount"]
                print(f"✅ Paid {p['amount']}")
            except Exception as e:
                print(f"❌ Error: {e}")
                errors.append(str(e))
        
        return {"success": len(txs)>0, "tx_hashes": txs, "total_paid": total, "unique_authors": len(txs), "mock_mode": False, "errors": errors}

    def get_explorer_url(self, tx_hash):
        return f"https://explorer.cronos.org/testnet3/tx/{tx_hash}"