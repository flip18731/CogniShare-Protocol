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
        
        # Get configuration from environment
        self.private_key = os.getenv("CRONOS_PRIVATE_KEY", "")
        self.rpc_url = os.getenv(
            "CRONOS_RPC_URL",
            self.CRONOS_TESTNET_RPC if use_testnet else self.CRONOS_MAINNET_RPC
        )
        self.chain_id = self.CRONOS_TESTNET_CHAIN_ID if use_testnet else self.CRONOS_MAINNET_CHAIN_ID
        
        # Initialize Web3 connection
        self._init_web3()
        
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
    
    def pay_authors(
        self,
        author_wallets: List[str],
        amount_per_citation: float = 0.01
    ) -> Dict[str, Any]:
        """
        Send x402 micropayments to knowledge authors.
        
        This is the core of the CogniShare value proposition:
        Authors get paid in CRO every time their knowledge is cited!
        
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
        print(f"⚡ x402 Payment Triggered")
        print(f"   Authors to pay: {len(author_wallets)}")
        print(f"   Amount per citation: {amount_per_citation} CRO")
        
        # Deduplicate wallets to save gas
        # (If same author is cited 3 times, pay them once × 3)
        wallet_counts: Dict[str, int] = {}
        for wallet in author_wallets:
            wallet = wallet.strip()
            if wallet and wallet != "0x0":
                wallet_counts[wallet] = wallet_counts.get(wallet, 0) + 1
        
        unique_wallets = list(wallet_counts.keys())
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
        
        # Calculate payments
        payments = []
        for wallet in unique_wallets:
            citation_count = wallet_counts[wallet]
            total_for_author = amount_per_citation * citation_count
            payments.append({
                "wallet": wallet,
                "citations": citation_count,
                "amount": total_for_author
            })
        
        # Execute payments (real or mock)
        if self.mock_mode:
            return self._mock_payments(payments)
        else:
            return self._real_payments(payments)
    
    def _mock_payments(self, payments: List[Dict]) -> Dict[str, Any]:
        """
        Simulate payments for demo/testing.
        
        Returns fake transaction hashes that look realistic.
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
        
        return {
            "success": True,
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
        """
        tx_hashes = []
        total_paid = 0
        errors = []
        
        for payment in payments:
            try:
                tx_hash = self._send_cro(
                    to_address=payment["wallet"],
                    amount_cro=payment["amount"]
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
        
        return {
            "success": len(tx_hashes) > 0,
            "tx_hashes": tx_hashes,
            "total_paid": total_paid,
            "unique_authors": len(tx_hashes),
            "mock_mode": False,
            "errors": errors if errors else None
        }
    
    def _send_cro(self, to_address: str, amount_cro: float) -> str:
        """
        Send CRO to a specific address.
        
        Args:
            to_address: Recipient wallet address
            amount_cro: Amount in CRO (not Wei)
            
        Returns:
            Transaction hash
        """
        # Convert CRO to Wei
        amount_wei = self.w3.to_wei(amount_cro, 'ether')
        
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
    
    def get_status(self) -> Dict[str, Any]:
        """Get current payment system status."""
        return {
            "network": "Cronos Testnet" if self.use_testnet else "Cronos Mainnet",
            "rpc_url": self.rpc_url,
            "sender_address": self.sender_address,
            "balance_cro": self.get_balance(),
            "mock_mode": self.mock_mode,
            "connected": self.w3.is_connected() if self.w3 else False
        }


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

