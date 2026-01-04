"""
=============================================================================
CogniShare Protocol - x402 Payment Manager
=============================================================================
This module handles Cronos blockchain payments to knowledge authors.

The x402 Concept:
When AI retrieves and cites knowledge from the decentralized RAG,
the original authors automatically receive micropayments in CRO.

This creates a new revenue model for content creators - getting paid
every time their knowledge is useful to an AI system!

Hackathon MVP - Cronos Testnet
=============================================================================
"""

import os
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from decimal import Decimal

# Web3 for blockchain interaction
from web3 import Web3
from web3.exceptions import Web3Exception

# Environment variables
from dotenv import load_dotenv

load_dotenv()


class CronosPayment:
    """
    Handles x402 micropayments on Cronos EVM.
    
    The x402 protocol (inspired by HTTP 402 Payment Required) enables
    machine-to-machine payments for AI knowledge access.
    
    When RAG retrieves chunks from authors, this class sends them CRO!
    """
    
    # Cronos Testnet Configuration
    CRONOS_TESTNET_RPC = "https://evm-t3.cronos.org"
    CRONOS_TESTNET_CHAIN_ID = 338
    
    # Mainnet (for future production use)
    CRONOS_MAINNET_RPC = "https://evm.cronos.org"
    CRONOS_MAINNET_CHAIN_ID = 25
    
    def __init__(self, use_testnet: bool = True):
        """
        Initialize the Cronos payment handler.
        
        Args:
            use_testnet: If True, use Cronos Testnet. If False, Mainnet.
        """
        self.use_testnet = use_testnet
        self.mock_mode = False
        self.use_smart_contract = False
        self.contract = None
        self.contract_address = None
        
        # Get configuration from environment
        self.private_key = os.getenv("CRONOS_PRIVATE_KEY", "")
        self.rpc_url = os.getenv(
            "CRONOS_RPC_URL",
            self.CRONOS_TESTNET_RPC if use_testnet else self.CRONOS_MAINNET_RPC
        )
        self.chain_id = self.CRONOS_TESTNET_CHAIN_ID if use_testnet else self.CRONOS_MAINNET_CHAIN_ID
        
        # Initialize Web3 connection
        self._init_web3()
        
        # Try to load smart contract (optional enhancement)
        self._load_smart_contract()
        
    def _init_web3(self):
        """
        Initialize Web3 connection and wallet.
        
        If no private key is provided, we activate mock mode
        so the demo still works without real blockchain access.
        """
        try:
            self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
            
            # Check connection
            if self.w3.is_connected():
                print(f"✅ Connected to Cronos {'Testnet' if self.use_testnet else 'Mainnet'}")
                print(f"   Chain ID: {self.chain_id}")
            else:
                print("⚠️ Could not connect to Cronos RPC")
                self.mock_mode = True
                
        except Exception as e:
            print(f"⚠️ Web3 initialization failed: {e}")
            self.mock_mode = True
            self.w3 = None
        
        # Check for private key
        if not self.private_key:
            print("⚠️ No CRONOS_PRIVATE_KEY found - enabling mock mode")
            print("   (Add your private key to .env for real transactions)")
            self.mock_mode = True
            self.sender_address = "0x0000000000000000000000000000000000000000"
        else:
            try:
                # Derive sender address from private key
                account = self.w3.eth.account.from_key(self.private_key)
                self.sender_address = account.address
                print(f"💳 Sender wallet: {self.sender_address[:10]}...{self.sender_address[-6:]}")
            except Exception as e:
                print(f"⚠️ Invalid private key: {e}")
                self.mock_mode = True
                self.sender_address = "0x0000000000000000000000000000000000000000"
    
    def _load_smart_contract(self):
        """
        Load CogniShareRegistry smart contract if deployed.
        
        This enables on-chain citation tracking via events.
        Falls back to direct transfers if contract not found.
        
        Includes robust validation:
        - File existence check
        - JSON parsing with error handling
        - Schema validation (required fields)
        - Address format validation
        - Function signature verification
        - Network connectivity test
        """
        contract_data_path = Path("contract_data.json")
        
        if not contract_data_path.exists():
            print("📝 No smart contract found - using direct transfers")
            print("   Deploy contract with: python deploy_contract.py")
            self.use_smart_contract = False
            return
        
        if self.mock_mode or not self.w3:
            print("📝 Mock mode active - smart contract disabled")
            self.use_smart_contract = False
            return
        
        try:
            # Load and parse JSON
            with open(contract_data_path, 'r') as f:
                contract_data = json.load(f)
            
            # Validate required fields exist
            required_fields = ['address', 'abi']
            missing = [f for f in required_fields if f not in contract_data]
            
            if missing:
                print(f"⚠️ Contract data missing required fields: {missing}")
                print("   Re-deploy contract with: python deploy_contract.py")
                self.use_smart_contract = False
                return
            
            # Validate address format (must be 42 chars, start with 0x)
            address = contract_data['address']
            if not isinstance(address, str) or len(address) != 42 or not address.startswith('0x'):
                print(f"⚠️ Invalid contract address format: {address}")
                print("   Expected: 0x + 40 hex characters")
                self.use_smart_contract = False
                return
            
            # Validate ABI is a list
            abi = contract_data['abi']
            if not isinstance(abi, list):
                print(f"⚠️ Contract ABI must be a list, got: {type(abi)}")
                self.use_smart_contract = False
                return
            
            # Store validated data
            self.contract_address = address
            
            # Create contract instance
            self.contract = self.w3.eth.contract(
                address=self.contract_address,
                abi=abi
            )
            
            # Verify required functions exist in ABI
            required_functions = ['payCitation', 'getGlobalStats']
            for func_name in required_functions:
                if not hasattr(self.contract.functions, func_name):
                    print(f"⚠️ Contract missing required function: {func_name}")
                    print("   Contract ABI may be outdated or incompatible")
                    self.use_smart_contract = False
                    return
            
            # Verify contract is deployed and accessible
            try:
                stats = self.contract.functions.getGlobalStats().call()
                self.use_smart_contract = True
                print(f"✅ Smart Contract loaded: {self.contract_address[:10]}...{self.contract_address[-6:]}")
                print(f"   Total citations on-chain: {stats[0]}")
                print(f"   Total paid: {self.w3.from_wei(stats[1], 'ether'):.4f} CRO")
            except Exception as e:
                print(f"⚠️ Contract exists but is not accessible: {e}")
                print("   Ensure contract is deployed on the correct network")
                self.use_smart_contract = False
                
        except json.JSONDecodeError as e:
            print(f"⚠️ Contract data file is corrupted (invalid JSON): {e}")
            print("   Re-deploy contract with: python deploy_contract.py")
            self.use_smart_contract = False
        except KeyError as e:
            print(f"⚠️ Contract data missing expected field: {e}")
            print("   File may be from incompatible version")
            self.use_smart_contract = False
        except Exception as e:
            print(f"⚠️ Unexpected error loading smart contract: {e}")
            print("   Falling back to direct transfers")
            self.use_smart_contract = False
    
    def get_balance(self) -> float:
        """
        Get the CRO balance of the sender wallet.
        
        Returns:
            Balance in CRO (not Wei)
        """
        if self.mock_mode or not self.w3:
            return 100.0  # Mock balance for demo
            
        try:
            balance_wei = self.w3.eth.get_balance(self.sender_address)
            balance_cro = self.w3.from_wei(balance_wei, 'ether')
            return float(balance_cro)
        except Exception as e:
            print(f"⚠️ Could not fetch balance: {e}")
            return 0.0
    
    def pay_authors_with_content(
        self,
        sources: List[Dict[str, Any]],
        amount_per_citation: float = 0.01
    ) -> Dict[str, Any]:
        """
        Send x402 micropayments to knowledge authors WITH content attribution.
        
        This is the CORRECT method for smart contract integration - it passes
        the actual cited content text, enabling proper on-chain attribution.
        
        Args:
            sources: List of source dicts from RAG engine with:
                - 'author_wallet': Author address
                - 'text': Cited content text
                - 'score': (optional) Relevance score
            amount_per_citation: CRO to send per citation (default 0.01)
            
        Returns:
            Dict containing:
                - success: bool
                - tx_hashes: List of transaction hashes
                - total_paid: Total CRO sent
                - unique_authors: Number of unique authors paid
                - mock_mode: Whether this was a simulated payment
        """
        print(f"⚡ x402 Payment Triggered (with content attribution)")
        print(f"   Sources to process: {len(sources)}")
        print(f"   Amount per citation: {amount_per_citation} CRO")
        
        # Deduplicate wallets and aggregate content
        wallet_data: Dict[str, Dict] = {}
        
        for source in sources:
            wallet = source.get("author_wallet", "").strip()
            
            # Validate wallet: 42 chars, starts with 0x, not zero address
            if wallet and len(wallet) == 42 and wallet.startswith("0x") and wallet != "0x" + "0"*40:
                if wallet not in wallet_data:
                    wallet_data[wallet] = {
                        "count": 0,
                        "content_texts": []
                    }
                wallet_data[wallet]["count"] += 1
                # Store first 200 chars of each cited text
                content_text = source.get("text", "")[:200]
                wallet_data[wallet]["content_texts"].append(content_text)
            else:
                print(f"   ⚠️ Skipping invalid wallet: {wallet[:20] if wallet else 'empty'}...")
        
        unique_wallets = list(wallet_data.keys())
        print(f"   Unique authors: {len(unique_wallets)}")
        
        if not unique_wallets:
            return {
                "success": False,
                "error": "No valid wallets to pay",
                "tx_hashes": [],
                "total_paid": 0,
                "unique_authors": 0,
                "mock_mode": self.mock_mode
            }
        
        # Calculate payments with content
        payments = []
        for wallet, data in wallet_data.items():
            # Combine multiple content texts (if same author cited multiple times)
            combined_text = " | ".join(data["content_texts"])
            
            payments.append({
                "wallet": wallet,
                "citations": data["count"],
                "amount": amount_per_citation * data["count"],
                "content_text": combined_text  # ← CRITICAL: Now included!
            })
        
        # Execute payments (real or mock)
        if self.mock_mode:
            return self._mock_payments(payments)
        else:
            return self._real_payments(payments)
    
    def pay_authors(
        self,
        author_wallets: List[str],
        amount_per_citation: float = 0.01
    ) -> Dict[str, Any]:
        """
        Send x402 micropayments to knowledge authors (LEGACY METHOD).
        
        ⚠️ WARNING: This method does NOT pass content text, so smart contract
        attribution will be generic. Use pay_authors_with_content() instead
        for proper on-chain citation tracking.
        
        This method is kept for backward compatibility but converts wallet
        list to source format internally.
        
        Args:
            author_wallets: List of wallet addresses to pay
            amount_per_citation: CRO to send per citation (default 0.01)
            
        Returns:
            Dict containing:
                - success: bool
                - tx_hashes: List of transaction hashes
                - total_paid: Total CRO sent
                - unique_authors: Number of unique authors paid
                - mock_mode: Whether this was a simulated payment
        """
        print(f"⚠️ Using legacy pay_authors() - content attribution will be limited")
        print(f"   Consider switching to pay_authors_with_content() for full tracking")
        
        # Convert wallet list to sources format (without content text)
        sources = [{"author_wallet": wallet, "text": ""} for wallet in author_wallets]
        
        # Use the new method
        return self.pay_authors_with_content(sources, amount_per_citation)
    
    def _mock_payments(self, payments: List[Dict]) -> Dict[str, Any]:
        """
        Simulate payments for demo/testing.
        
        Returns fake transaction hashes that look realistic.
        
        NOTE: Mock mode ALWAYS returns success=True to allow demos to run
        without real blockchain access. In production, only _real_payments
        is used with proper success validation.
        """
        import hashlib
        import time
        
        tx_hashes = []
        total_paid = 0
        
        for payment in payments:
            # Generate realistic-looking fake TX hash
            fake_data = f"{payment['wallet']}{time.time()}"
            fake_hash = "0x" + hashlib.sha256(fake_data.encode()).hexdigest()
            
            tx_hashes.append({
                "wallet": payment["wallet"],
                "amount": payment["amount"],
                "tx_hash": fake_hash,
                "status": "simulated"
            })
            total_paid += payment["amount"]
            
            print(f"   💸 [MOCK] Paid {payment['amount']:.4f} CRO to {payment['wallet'][:10]}...")
        
        print(f"   ✅ Mock mode: {len(payments)} simulated payments successful")
        
        return {
            "success": True,  # Always True in mock mode for demo purposes
            "tx_hashes": tx_hashes,
            "total_paid": total_paid,
            "unique_authors": len(payments),
            "mock_mode": True,
            "message": "⚠️ Mock mode - no real transactions sent"
        }
    
    def _real_payments(self, payments: List[Dict]) -> Dict[str, Any]:
        """
        Execute real blockchain payments.
        
        Sends CRO to each author's wallet and returns TX hashes.
        
        CRITICAL: Returns success=True ONLY if at least one payment succeeded.
        This enforces the x402 protocol - if all payments fail, the system
        must not proceed with generating an answer.
        """
        tx_hashes = []
        total_paid = 0
        errors = []
        
        for payment in payments:
            try:
                # Generate content hash for smart contract
                content_hash = self._generate_content_hash(
                    payment["wallet"], 
                    payment.get("content_text", "")
                )
                
                tx_hash = self._send_cro(
                    to_address=payment["wallet"],
                    amount_cro=payment["amount"],
                    content_hash=content_hash
                )
                
                tx_hashes.append({
                    "wallet": payment["wallet"],
                    "amount": payment["amount"],
                    "tx_hash": tx_hash,
                    "status": "sent"
                })
                total_paid += payment["amount"]
                
                print(f"   ✅ Paid {payment['amount']:.4f} CRO to {payment['wallet'][:10]}...")
                print(f"      TX: {tx_hash[:20]}...")
                
            except Exception as e:
                error_msg = f"Failed to pay {payment['wallet'][:10]}...: {str(e)}"
                errors.append(error_msg)
                print(f"   ❌ {error_msg}")
        
        # CRITICAL: success=True ONLY if at least one TX succeeded
        # If all TXs failed, success=False enforces x402 (no payment = no answer)
        success = len(tx_hashes) > 0
        
        if not success:
            print("   🚫 ALL payments failed - x402 enforcement active")
        
        return {
            "success": success,
            "tx_hashes": tx_hashes,
            "total_paid": total_paid,
            "unique_authors": len(tx_hashes),
            "mock_mode": False,
            "errors": errors if errors else None
        }
    
    def _send_cro(self, to_address: str, amount_cro: float, content_hash: str = "") -> str:
        """
        Send CRO to a specific address.
        
        Uses smart contract if available (for on-chain citation tracking),
        otherwise falls back to direct transfer.
        
        Args:
            to_address: Recipient wallet address
            amount_cro: Amount in CRO (not Wei)
            content_hash: Hash of cited content (for smart contract)
            
        Returns:
            Transaction hash
        """
        amount_wei = self.w3.to_wei(amount_cro, 'ether')
        
        # Smart Contract Path (preferred)
        if self.use_smart_contract and self.contract:
            return self._send_via_contract(to_address, amount_wei, content_hash)
        
        # Direct Transfer Path (fallback)
        return self._send_direct_transfer(to_address, amount_wei)
    
    def _send_via_contract(self, to_address: str, amount_wei: int, content_hash: str) -> str:
        """
        Send payment via CogniShareRegistry smart contract.
        
        This creates an on-chain citation record with event logs.
        
        Args:
            to_address: Author wallet address
            amount_wei: Amount in Wei
            content_hash: Hash/ID of cited content
            
        Returns:
            Transaction hash
        """
        # Get current nonce
        nonce = self.w3.eth.get_transaction_count(self.sender_address)
        
        # Get gas price
        gas_price = self.w3.eth.gas_price
        
        # Build contract transaction
        tx = self.contract.functions.payCitation(
            Web3.to_checksum_address(to_address),
            content_hash if content_hash else "direct_payment"
        ).build_transaction({
            'chainId': self.chain_id,
            'from': self.sender_address,
            'nonce': nonce,
            'value': amount_wei,
            'gasPrice': gas_price,
            'gas': 100000,  # Smart contract call needs more gas
        })
        
        # Sign transaction
        signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
        
        # Send transaction
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        return self.w3.to_hex(tx_hash)
    
    def _send_direct_transfer(self, to_address: str, amount_wei: int) -> str:
        """
        Send CRO via direct transfer (legacy mode).
        
        Args:
            to_address: Recipient wallet address
            amount_wei: Amount in Wei
            
        Returns:
            Transaction hash
        """
        # Get current nonce
        nonce = self.w3.eth.get_transaction_count(self.sender_address)
        
        # Get current gas price
        gas_price = self.w3.eth.gas_price
        
        # Build transaction
        tx = {
            'nonce': nonce,
            'to': Web3.to_checksum_address(to_address),
            'value': amount_wei,
            'gas': 21000,  # Standard transfer gas
            'gasPrice': gas_price,
            'chainId': self.chain_id
        }
        
        # Sign transaction
        signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
        
        # Send transaction
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        return self.w3.to_hex(tx_hash)
    
    def get_explorer_url(self, tx_hash: str) -> str:
        """
        Get the block explorer URL for a transaction.
        
        Args:
            tx_hash: Transaction hash
            
        Returns:
            URL to view transaction on explorer
        """
        if self.use_testnet:
            return f"https://explorer.cronos.org/testnet3/tx/{tx_hash}"
        else:
            return f"https://explorer.cronos.org/tx/{tx_hash}"
    
    def _generate_content_hash(self, author_wallet: str, content_text: str) -> str:
        """
        Generate a unique hash for cited content.
        
        Used for on-chain attribution in smart contract events.
        
        Args:
            author_wallet: Author's wallet address
            content_text: Text content being cited
            
        Returns:
            SHA256 hash as hex string
        """
        # Combine wallet + content for unique identifier
        combined = f"{author_wallet}:{content_text[:100]}"
        hash_bytes = hashlib.sha256(combined.encode()).digest()
        return "0x" + hash_bytes.hex()[:32]  # First 32 chars for readability
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current payment system status.
        
        Returns comprehensive status including:
        - Network information (testnet/mainnet)
        - Connection status
        - Wallet balance
        - Mock mode status
        - Smart contract details (if active)
        - On-chain statistics (if available)
        """
        status = {
            "network": "Cronos Testnet" if self.use_testnet else "Cronos Mainnet",
            "rpc_url": self.rpc_url,
            "sender_address": self.sender_address,
            "balance_cro": self.get_balance(),
            "mock_mode": self.mock_mode,
            "connected": self.w3.is_connected() if self.w3 else False,
            "smart_contract": self.use_smart_contract,
            "contract_address": self.contract_address if self.use_smart_contract else None
        }
        
        # Add contract stats if smart contract is active
        if self.use_smart_contract and self.contract:
            try:
                citations, paid_wei = self.contract.functions.getGlobalStats().call()
                status["total_citations_onchain"] = int(citations)
                status["total_paid_onchain"] = float(self.w3.from_wei(paid_wei, 'ether'))
                
                # Add contract deployment info if available
                if hasattr(self, 'contract_address'):
                    status["contract_address_short"] = f"{self.contract_address[:10]}...{self.contract_address[-6:]}"
                    
            except Exception as e:
                # If contract call fails, add error info
                status["contract_error"] = str(e)
                status["total_citations_onchain"] = 0
                status["total_paid_onchain"] = 0.0
        
        return status


# =============================================================================
# Quick test when running directly
# =============================================================================
if __name__ == "__main__":
    print("🧪 Testing Cronos Payment Manager...")
    
    payment = CronosPayment(use_testnet=True)
    
    # Print status
    status = payment.get_status()
    print(f"\n📊 Status:")
    for key, value in status.items():
        print(f"   {key}: {value}")
    
    # Test payment (will be mock if no private key)
    print("\n💰 Testing payment...")
    result = payment.pay_authors(
        author_wallets=[
            "0x742d35Cc6634C0532925a3b844Bc9e7595f5bE21",
            "0x8ba1f109551bD432803012645Hc136c5E2C6bc",
            "0x742d35Cc6634C0532925a3b844Bc9e7595f5bE21"  # Duplicate
        ],
        amount_per_citation=0.01
    )
    
    print(f"\n📋 Payment Result:")
    print(f"   Success: {result['success']}")
    print(f"   Total Paid: {result['total_paid']} CRO")
    print(f"   Unique Authors: {result['unique_authors']}")
    print(f"   Mock Mode: {result['mock_mode']}")

