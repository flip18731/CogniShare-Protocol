"""
=============================================================================
CogniShare Protocol - Smart Contract Deployment Script
=============================================================================
Deploys the CogniShareRegistry contract to Cronos Testnet.

This script:
1. Compiles the Solidity contract using py-solc-x
2. Deploys it to Cronos Testnet using Web3.py
3. Saves the contract address and ABI to contract_data.json

Usage:
    python deploy_contract.py

Requirements:
    - CRONOS_PRIVATE_KEY in .env file
    - Sufficient CRO in wallet for gas fees
    - Internet connection to Cronos Testnet RPC

Hackathon Submission - Cronos EVM
=============================================================================
"""

import json
import os
import sys
from pathlib import Path

from web3 import Web3
from dotenv import load_dotenv
from solcx import compile_source, install_solc, set_solc_version

# Load environment variables
load_dotenv()


class ContractDeployer:
    """
    Handles compilation and deployment of CogniShareRegistry contract.
    """
    
    # Cronos Testnet Configuration
    CRONOS_TESTNET_RPC = "https://evm-t3.cronos.org"
    CRONOS_TESTNET_CHAIN_ID = 338
    
    def __init__(self):
        """Initialize Web3 connection and load configuration."""
        
        print("🚀 CogniShare Contract Deployer")
        print("=" * 60)
        
        # Get private key
        self.private_key = os.getenv("CRONOS_PRIVATE_KEY", "")
        if not self.private_key:
            print("❌ Error: CRONOS_PRIVATE_KEY not found in .env file")
            print("   Please add your private key to deploy the contract")
            sys.exit(1)
        
        # Initialize Web3
        print("📡 Connecting to Cronos Testnet...")
        self.w3 = Web3(Web3.HTTPProvider(self.CRONOS_TESTNET_RPC))
        
        if not self.w3.is_connected():
            print("❌ Error: Could not connect to Cronos Testnet RPC")
            print(f"   RPC URL: {self.CRONOS_TESTNET_RPC}")
            sys.exit(1)
        
        print(f"✅ Connected to Cronos Testnet (Chain ID: {self.CRONOS_TESTNET_CHAIN_ID})")
        
        # Get account from private key
        self.account = self.w3.eth.account.from_key(self.private_key)
        self.deployer_address = self.account.address
        
        print(f"💳 Deployer Address: {self.deployer_address}")
        
        # Check balance
        balance_wei = self.w3.eth.get_balance(self.deployer_address)
        balance_cro = self.w3.from_wei(balance_wei, 'ether')
        print(f"💰 Balance: {balance_cro:.4f} CRO")
        
        if balance_cro < 0.1:
            print("⚠️  Warning: Low balance - deployment may fail")
            print("   Get test CRO from: https://cronos.org/faucet")
    
    def compile_contract(self) -> dict:
        """
        Compile the CogniShareRegistry.sol contract.
        
        Returns:
            dict: Compiled contract data (abi, bytecode)
        """
        print("\n📝 Compiling Smart Contract...")
        print("-" * 60)
        
        # Install Solidity compiler
        try:
            print("🔧 Installing Solidity compiler v0.8.20...")
            install_solc("0.8.20")
            set_solc_version("0.8.20")
        except Exception as e:
            print(f"⚠️  Warning: Could not install solc: {e}")
            print("   Trying with system solc...")
        
        # Read contract source
        contract_path = Path("contracts/CogniShareRegistry.sol")
        if not contract_path.exists():
            print(f"❌ Error: Contract file not found at {contract_path}")
            sys.exit(1)
        
        with open(contract_path, 'r', encoding='utf-8') as f:
            contract_source = f.read()
        
        print(f"📄 Source file: {contract_path}")
        print(f"📏 Source size: {len(contract_source)} bytes")
        
        # Compile
        try:
            compiled = compile_source(
                contract_source,
                output_values=['abi', 'bin']
            )
            
            # Get contract interface
            contract_id = list(compiled.keys())[0]
            contract_interface = compiled[contract_id]
            
            print(f"✅ Compilation successful!")
            print(f"   Contract ID: {contract_id}")
            print(f"   Bytecode size: {len(contract_interface['bin'])} bytes")
            print(f"   ABI functions: {len(contract_interface['abi'])} entries")
            
            return contract_interface
            
        except Exception as e:
            print(f"❌ Compilation failed: {e}")
            sys.exit(1)
    
    def deploy_contract(self, contract_interface: dict) -> dict:
        """
        Deploy the compiled contract to Cronos Testnet.
        
        Args:
            contract_interface: Compiled contract (abi, bytecode)
            
        Returns:
            dict: Deployment result (address, tx_hash, abi)
        """
        print("\n🚀 Deploying Contract to Cronos Testnet...")
        print("-" * 60)
        
        # Create contract object
        Contract = self.w3.eth.contract(
            abi=contract_interface['abi'],
            bytecode=contract_interface['bin']
        )
        
        # Get current nonce
        nonce = self.w3.eth.get_transaction_count(self.deployer_address)
        print(f"🔢 Nonce: {nonce}")
        
        # Get gas price
        gas_price = self.w3.eth.gas_price
        gas_price_gwei = self.w3.from_wei(gas_price, 'gwei')
        print(f"⛽ Gas Price: {gas_price_gwei:.2f} Gwei")
        
        # Build deployment transaction
        print("📦 Building deployment transaction...")
        constructor_txn = Contract.constructor().build_transaction({
            'chainId': self.CRONOS_TESTNET_CHAIN_ID,
            'from': self.deployer_address,
            'nonce': nonce,
            'gasPrice': gas_price,
            'gas': 2000000,  # Generous gas limit for deployment
        })
        
        # Estimate actual gas needed
        try:
            estimated_gas = self.w3.eth.estimate_gas(constructor_txn)
            constructor_txn['gas'] = int(estimated_gas * 1.2)  # Add 20% buffer
            print(f"⛽ Estimated Gas: {estimated_gas} (using {constructor_txn['gas']})")
        except Exception as e:
            print(f"⚠️  Could not estimate gas: {e}")
            print("   Using default gas limit")
        
        # Calculate deployment cost
        deployment_cost_wei = constructor_txn['gas'] * gas_price
        deployment_cost_cro = self.w3.from_wei(deployment_cost_wei, 'ether')
        print(f"💸 Estimated Cost: {deployment_cost_cro:.6f} CRO")
        
        # Sign transaction
        print("✍️  Signing transaction...")
        signed_txn = self.w3.eth.account.sign_transaction(
            constructor_txn, 
            self.private_key
        )
        
        # Send transaction
        print("📤 Broadcasting transaction...")
        try:
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            tx_hash_hex = self.w3.to_hex(tx_hash)
            print(f"📨 Transaction sent: {tx_hash_hex}")
            
            # Wait for receipt
            print("⏳ Waiting for confirmation...")
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(
                tx_hash,
                timeout=120  # 2 minutes max
            )
            
            if tx_receipt.status == 0:
                print("❌ Transaction failed on-chain!")
                sys.exit(1)
            
            contract_address = tx_receipt.contractAddress
            
            print("\n" + "=" * 60)
            print("✅ CONTRACT DEPLOYED SUCCESSFULLY!")
            print("=" * 60)
            print(f"📍 Contract Address: {contract_address}")
            print(f"🔗 TX Hash: {tx_hash_hex}")
            print(f"⛽ Gas Used: {tx_receipt.gasUsed:,}")
            print(f"🔍 Explorer: https://explorer.cronos.org/testnet3/tx/{tx_hash_hex}")
            print("=" * 60)
            
            return {
                "address": contract_address,
                "tx_hash": tx_hash_hex,
                "abi": contract_interface['abi'],
                "deployer": self.deployer_address,
                "network": "Cronos Testnet",
                "chain_id": self.CRONOS_TESTNET_CHAIN_ID,
                "block_number": tx_receipt.blockNumber,
                "gas_used": tx_receipt.gasUsed
            }
            
        except Exception as e:
            print(f"❌ Deployment failed: {e}")
            sys.exit(1)
    
    def save_deployment_data(self, deployment_data: dict):
        """
        Save contract address and ABI to contract_data.json.
        
        Args:
            deployment_data: Deployment result from deploy_contract()
        """
        print("\n💾 Saving Deployment Data...")
        print("-" * 60)
        
        output_file = Path("contract_data.json")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(deployment_data, f, indent=2)
        
        print(f"✅ Saved to: {output_file.absolute()}")
        print(f"📄 File size: {output_file.stat().st_size} bytes")
        
        # Also save a backup
        backup_file = Path("contract_data.backup.json")
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(deployment_data, f, indent=2)
        print(f"💾 Backup saved to: {backup_file}")
    
    def verify_deployment(self, contract_address: str):
        """
        Verify that the contract is deployed and working.
        
        Args:
            contract_address: Deployed contract address
        """
        print("\n🔍 Verifying Deployment...")
        print("-" * 60)
        
        # Check contract code exists
        code = self.w3.eth.get_code(contract_address)
        if len(code) <= 2:  # "0x" is empty
            print("❌ No contract code at address!")
            return False
        
        print(f"✅ Contract code verified ({len(code)} bytes)")
        
        # Try to call a view function
        try:
            # Load contract
            with open("contract_data.json", 'r') as f:
                data = json.load(f)
            
            contract = self.w3.eth.contract(
                address=contract_address,
                abi=data['abi']
            )
            
            # Call getGlobalStats
            citations, paid = contract.functions.getGlobalStats().call()
            print(f"✅ Contract is functional")
            print(f"   Total Citations: {citations}")
            print(f"   Total Paid: {paid} Wei")
            
            return True
            
        except Exception as e:
            print(f"⚠️  Could not verify contract functions: {e}")
            return False


def main():
    """Main deployment flow."""
    
    deployer = ContractDeployer()
    
    # Step 1: Compile
    contract_interface = deployer.compile_contract()
    
    # Step 2: Deploy
    deployment_data = deployer.deploy_contract(contract_interface)
    
    # Step 3: Save
    deployer.save_deployment_data(deployment_data)
    
    # Step 4: Verify
    deployer.verify_deployment(deployment_data['address'])
    
    print("\n" + "=" * 60)
    print("🎉 DEPLOYMENT COMPLETE!")
    print("=" * 60)
    print("\n📝 Next Steps:")
    print("1. Update your .env with CONTRACT_ADDRESS (optional)")
    print("2. Restart the CogniShare app: py -m streamlit run app.py")
    print("3. The app will automatically use the smart contract")
    print("\n🏆 Your citations are now recorded on-chain!")
    print("=" * 60)


if __name__ == "__main__":
    main()

