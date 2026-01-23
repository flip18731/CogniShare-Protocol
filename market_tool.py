"""
=============================================================================
CogniShare Protocol - Crypto Market Data Tool
=============================================================================
This module provides real-time cryptocurrency market data access.

The x402 Concept Extended:
- Knowledge citation: Pay authors per use (PDF content)
- Live data access: Pay data providers per call (Market APIs)

This creates a hybrid payment model where both static knowledge and
dynamic data have value and compensation mechanisms.

Premium Feature: 0.05 CRO per market data call
=============================================================================
"""

from typing import Dict, Any, Optional
from pycoingecko import CoinGeckoAPI


class CryptoMarketTool:
    """
    Tool for accessing real-time cryptocurrency market data.
    
    This is a premium feature - each call costs 0.05 CRO paid via x402.
    The payment ensures data providers are compensated and prevents abuse.
    
    Supported via CoinGecko API as a proxy for Crypto.com market data.
    """
    
    # Service wallet for data access fees
    # NOTE: In production, this would be the data provider's wallet
    SERVICE_WALLET = "0x742d35Cc6634C0532925a3b844Bc9e7595f5bE21"  # Example service wallet
    
    # Cost per market data call
    CALL_COST_CRO = 0.05
    
    # Supported coin mappings (CoinGecko IDs)
    COIN_MAPPING = {
        "cro": "crypto-com-chain",
        "cronos": "crypto-com-chain",
        "bitcoin": "bitcoin",
        "btc": "bitcoin",
        "ethereum": "ethereum",
        "eth": "ethereum",
        "bnb": "binancecoin",
        "cardano": "cardano",
        "ada": "cardano",
        "solana": "solana",
        "sol": "solana",
        "polkadot": "polkadot",
        "dot": "polkadot",
        "dogecoin": "dogecoin",
        "doge": "dogecoin",
        "matic": "matic-network",
        "polygon": "matic-network"
    }
    
    def __init__(self):
        """Initialize the CoinGecko API client."""
        self.cg = CoinGeckoAPI()
        self.call_count = 0
    
    def get_price(self, symbol: str) -> Dict[str, Any]:
        """
        Get current market price for a cryptocurrency.
        
        ⚠️ PREMIUM FEATURE: Requires x402 payment of 0.05 CRO
        
        Args:
            symbol: Cryptocurrency symbol (e.g., 'cro', 'bitcoin', 'eth')
            
        Returns:
            Dict containing:
                - success: bool
                - symbol: str (original input)
                - coin_name: str (full name)
                - price_usd: float
                - price_change_24h: float (percentage)
                - market_cap: float
                - volume_24h: float
                - formatted_message: str (human-readable)
                - requires_payment: bool (always True)
                - payment_amount: float
                - service_wallet: str
        """
        # Normalize symbol
        symbol_lower = symbol.lower().strip()
        
        # Map to CoinGecko ID
        coin_id = self.COIN_MAPPING.get(symbol_lower)
        
        if not coin_id:
            return {
                "success": False,
                "error": f"Cryptocurrency '{symbol}' not supported",
                "supported_symbols": list(self.COIN_MAPPING.keys()),
                "requires_payment": True,
                "payment_amount": self.CALL_COST_CRO,
                "service_wallet": self.SERVICE_WALLET
            }
        
        try:
            # Fetch data from CoinGecko
            data = self.cg.get_price(
                ids=coin_id,
                vs_currencies='usd',
                include_market_cap=True,
                include_24hr_vol=True,
                include_24hr_change=True
            )
            
            if coin_id not in data:
                return {
                    "success": False,
                    "error": f"No data available for {symbol}",
                    "requires_payment": True,
                    "payment_amount": self.CALL_COST_CRO,
                    "service_wallet": self.SERVICE_WALLET
                }
            
            coin_data = data[coin_id]
            
            # Extract relevant information
            price_usd = coin_data.get('usd', 0)
            price_change_24h = coin_data.get('usd_24h_change', 0)
            market_cap = coin_data.get('usd_market_cap', 0)
            volume_24h = coin_data.get('usd_24h_vol', 0)
            
            # Format human-readable message
            change_emoji = "📈" if price_change_24h > 0 else "📉"
            change_sign = "+" if price_change_24h > 0 else ""
            
            formatted_message = f"""
🪙 **{symbol.upper()} Market Data** (Live)

💵 **Current Price:** ${price_usd:,.2f} USD
{change_emoji} **24h Change:** {change_sign}{price_change_24h:.2f}%
📊 **Market Cap:** ${market_cap:,.0f} USD
💹 **24h Volume:** ${volume_24h:,.0f} USD

*Data provided by CoinGecko API*
""".strip()
            
            self.call_count += 1
            
            return {
                "success": True,
                "symbol": symbol.upper(),
                "coin_id": coin_id,
                "price_usd": price_usd,
                "price_change_24h": price_change_24h,
                "market_cap": market_cap,
                "volume_24h": volume_24h,
                "formatted_message": formatted_message,
                "requires_payment": True,
                "payment_amount": self.CALL_COST_CRO,
                "service_wallet": self.SERVICE_WALLET,
                "call_count": self.call_count
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to fetch market data: {str(e)}",
                "requires_payment": True,
                "payment_amount": self.CALL_COST_CRO,
                "service_wallet": self.SERVICE_WALLET
            }
    
    def get_multiple_prices(self, symbols: list) -> Dict[str, Any]:
        """
        Get prices for multiple cryptocurrencies.
        
        ⚠️ PREMIUM FEATURE: Costs 0.05 CRO PER SYMBOL
        
        Args:
            symbols: List of cryptocurrency symbols
            
        Returns:
            Dict with results for each symbol
        """
        results = {}
        total_cost = len(symbols) * self.CALL_COST_CRO
        
        for symbol in symbols:
            results[symbol] = self.get_price(symbol)
        
        return {
            "success": True,
            "results": results,
            "total_symbols": len(symbols),
            "total_cost": total_cost,
            "service_wallet": self.SERVICE_WALLET
        }
    
    def is_market_query(self, user_query: str) -> bool:
        """
        Detect if user query requires market data access.
        
        Args:
            user_query: User's question
            
        Returns:
            True if query needs market data, False otherwise
        """
        # Keywords that indicate market data request
        market_keywords = [
            "price", "cost", "worth", "value", "market", "trading",
            "buy", "sell", "exchange", "rate", "ticker", "quote",
            "how much", "what's the price", "current price", "live price"
        ]
        
        # Crypto symbols
        crypto_symbols = list(self.COIN_MAPPING.keys())
        
        query_lower = user_query.lower()
        
        # Check if query contains market keywords AND crypto symbols
        has_market_keyword = any(keyword in query_lower for keyword in market_keywords)
        has_crypto_symbol = any(symbol in query_lower for symbol in crypto_symbols)
        
        return has_market_keyword and has_crypto_symbol
    
    def extract_symbol_from_query(self, user_query: str) -> Optional[str]:
        """
        Extract cryptocurrency symbol from user query.
        
        Args:
            user_query: User's question
            
        Returns:
            Cryptocurrency symbol or None
        """
        query_lower = user_query.lower()
        
        # Check for each supported symbol
        for symbol in self.COIN_MAPPING.keys():
            if symbol in query_lower:
                return symbol
        
        return None
    
    def get_status(self) -> Dict[str, Any]:
        """Get tool status and statistics."""
        return {
            "tool": "CryptoMarketTool",
            "status": "active",
            "cost_per_call": self.CALL_COST_CRO,
            "service_wallet": self.SERVICE_WALLET,
            "total_calls": self.call_count,
            "supported_symbols": list(self.COIN_MAPPING.keys()),
            "api_provider": "CoinGecko"
        }


# =============================================================================
# Quick test when running directly
# =============================================================================
if __name__ == "__main__":
    print("🧪 Testing Crypto Market Tool...")
    
    tool = CryptoMarketTool()
    
    # Test 1: Get CRO price
    print("\n📊 Test 1: Get CRO Price")
    result = tool.get_price("cro")
    if result["success"]:
        print(result["formatted_message"])
        print(f"\n💰 Payment Required: {result['payment_amount']} CRO")
        print(f"📍 Service Wallet: {result['service_wallet'][:10]}...")
    else:
        print(f"❌ Error: {result['error']}")
    
    # Test 2: Detect market query
    print("\n🔍 Test 2: Query Detection")
    queries = [
        "What is the price of CRO?",
        "Tell me about blockchain",
        "How much is Bitcoin worth?",
        "Explain Ethereum"
    ]
    
    for query in queries:
        is_market = tool.is_market_query(query)
        symbol = tool.extract_symbol_from_query(query)
        print(f"  '{query}'")
        print(f"    Market Query: {is_market} | Symbol: {symbol}")
    
    # Test 3: Get status
    print("\n📋 Test 3: Tool Status")
    status = tool.get_status()
    for key, value in status.items():
        if key != "supported_symbols":
            print(f"  {key}: {value}")

