"""
=============================================================================
CogniShare Protocol - RAG Core Engine
=============================================================================
This module handles:
  1. Document ingestion (PDF → chunks → embeddings → Pinecone)
  2. Semantic search with author attribution
  
The key innovation: Every chunk stores the author's wallet address in metadata,
enabling x402 micropayments when that knowledge is cited.

Hackathon MVP - Cronos EVM
=============================================================================
"""

import os
import hashlib
from typing import List, Dict, Any, Optional
from io import BytesIO

# Document processing
from PyPDF2 import PdfReader

# LangChain for text processing
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

# Environment variables
from dotenv import load_dotenv

load_dotenv()


class RAGEngine:
    """
    The brain of CogniShare Protocol.
    
    This class manages the knowledge base - ingesting documents with author
    attribution and retrieving relevant chunks for AI responses.
    
    Key Feature: Every chunk is tagged with the author's wallet address,
    so when AI cites that chunk, we know who to pay!
    """
    
    def __init__(self):
        """
        Initialize the RAG Engine.
        
        We try to connect to Pinecone first. If that fails (no API key, 
        network issues, etc.), we fall back to a local mock mode.
        This ensures the hackathon demo always works!
        """
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.pinecone_index_name = os.getenv("PINECONE_INDEX_NAME", "cognishare")
        
        # Track if we're using real Pinecone or mock mode
        self.use_mock = False
        self.mock_storage: List[Dict[str, Any]] = []  # Local fallback storage
        
        # Initialize embeddings (OpenAI's text-embedding-3-small is cost-effective)
        if self.openai_api_key:
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=self.openai_api_key,
                model="text-embedding-3-small"  # Cheap & fast for hackathon
            )
        else:
            self.embeddings = None
            print("⚠️ No OpenAI API key found - embeddings will be mocked")
        
        # Initialize Pinecone connection
        self._init_pinecone()
        
        # Text splitter for chunking documents
        # 500 chars with 50 overlap ensures good context per chunk
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def _init_pinecone(self):
        """
        Connect to Pinecone vector database.
        
        If connection fails, we activate mock mode so the demo still works.
        This is crucial for hackathon presentations!
        """
        if not self.pinecone_api_key:
            print("⚠️ No Pinecone API key found - using local mock storage")
            self.use_mock = True
            self.index = None
            return
        
        try:
            from pinecone import Pinecone
            
            # Initialize Pinecone client
            pc = Pinecone(api_key=self.pinecone_api_key)
            
            # Get or create index
            # Note: For hackathon, assume index exists (create via Pinecone console)
            self.index = pc.Index(self.pinecone_index_name)
            print(f"✅ Connected to Pinecone index: {self.pinecone_index_name}")
            
        except Exception as e:
            print(f"⚠️ Pinecone connection failed: {e}")
            print("📦 Falling back to local mock storage")
            self.use_mock = True
            self.index = None
    
    def _extract_text_from_pdf(self, file) -> str:
        """
        Extract all text content from a PDF file.
        
        Args:
            file: Streamlit UploadedFile or file-like object
            
        Returns:
            Concatenated text from all pages
        """
        try:
            # Handle Streamlit's UploadedFile
            if hasattr(file, 'read'):
                pdf_bytes = file.read()
                file.seek(0)  # Reset for potential re-read
                reader = PdfReader(BytesIO(pdf_bytes))
            else:
                reader = PdfReader(file)
            
            # Extract text from all pages
            text_content = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_content.append(page_text)
            
            full_text = "\n\n".join(text_content)
            print(f"📄 Extracted {len(full_text)} characters from PDF")
            return full_text
            
        except Exception as e:
            print(f"❌ PDF extraction failed: {e}")
            raise ValueError(f"Failed to extract text from PDF: {e}")
    
    def _generate_chunk_id(self, text: str, author_wallet: str) -> str:
        """
        Generate a unique ID for each chunk.
        
        Uses SHA256 hash of content + author to ensure:
        - Same content from same author = same ID (deduplication)
        - Same content from different authors = different IDs
        """
        unique_string = f"{author_wallet}:{text[:100]}"
        return hashlib.sha256(unique_string.encode()).hexdigest()[:16]
    
    def _mock_embed(self, text: str) -> List[float]:
        """
        Create a fake embedding for mock mode.
        
        Uses simple hash-based approach to create reproducible vectors.
        Real embeddings are 1536 dimensions for OpenAI's models.
        """
        # Create a deterministic "embedding" based on text hash
        hash_val = int(hashlib.md5(text.encode()).hexdigest(), 16)
        # Generate 1536 pseudo-random floats (same as OpenAI's dimension)
        import random
        random.seed(hash_val)
        return [random.uniform(-1, 1) for _ in range(1536)]
    
    def ingest_document(self, file, author_wallet: str) -> Dict[str, Any]:
        """
        Ingest a document into the knowledge base.
        
        This is where the magic happens:
        1. Extract text from PDF
        2. Split into digestible chunks
        3. Create embeddings for semantic search
        4. Store in Pinecone WITH author wallet metadata
        
        The author_wallet is CRITICAL - it enables x402 micropayments!
        
        Args:
            file: PDF file (Streamlit UploadedFile)
            author_wallet: Cronos wallet address (0x...)
            
        Returns:
            Dict with ingestion stats
        """
        # Step 1: Extract text from PDF
        print(f"📚 Ingesting document for author: {author_wallet[:10]}...")
        text = self._extract_text_from_pdf(file)
        
        if not text.strip():
            raise ValueError("PDF appears to be empty or unreadable")
        
        # Step 2: Split into chunks
        chunks = self.text_splitter.split_text(text)
        print(f"✂️ Split into {len(chunks)} chunks")
        
        # Step 3: Create embeddings and prepare for upsert
        vectors_to_upsert = []
        
        for i, chunk in enumerate(chunks):
            # Generate unique ID for this chunk
            chunk_id = self._generate_chunk_id(chunk, author_wallet)
            
            # Create embedding (real or mock)
            if self.embeddings:
                embedding = self.embeddings.embed_query(chunk)
            else:
                embedding = self._mock_embed(chunk)
            
            # Prepare vector with metadata
            # CRITICAL: We store author_wallet and source_text here!
            # This enables the x402 payment system to work
            vector = {
                "id": chunk_id,
                "values": embedding,
                "metadata": {
                    "author_wallet": author_wallet,  # WHO TO PAY
                    "source_text": chunk,            # WHAT WAS CITED
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "file_name": getattr(file, 'name', 'unknown.pdf')
                }
            }
            vectors_to_upsert.append(vector)
        
        # Step 4: Upsert to Pinecone (or mock storage)
        if self.use_mock:
            # Mock mode: store locally
            self.mock_storage.extend(vectors_to_upsert)
            print(f"📦 Stored {len(vectors_to_upsert)} vectors in mock storage")
        else:
            # Real Pinecone upsert
            try:
                # Batch upsert for efficiency
                batch_size = 100
                for i in range(0, len(vectors_to_upsert), batch_size):
                    batch = vectors_to_upsert[i:i + batch_size]
                    self.index.upsert(vectors=batch)
                print(f"☁️ Upserted {len(vectors_to_upsert)} vectors to Pinecone")
            except Exception as e:
                print(f"❌ Pinecone upsert failed: {e}")
                # Fallback to mock
                self.mock_storage.extend(vectors_to_upsert)
                print(f"📦 Fallback: Stored in mock storage")
        
        return {
            "success": True,
            "chunks_created": len(chunks),
            "author_wallet": author_wallet,
            "file_name": getattr(file, 'name', 'unknown.pdf')
        }
    
    def query(self, user_query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Search the knowledge base for relevant chunks.
        
        This is the retrieval part of RAG:
        1. Embed the user's query
        2. Find similar vectors in Pinecone
        3. Return results with author wallets for payment
        
        Args:
            user_query: The user's question
            top_k: Number of results to return (default 3)
            
        Returns:
            List of dicts with: text, author_wallet, score
        """
        print(f"🔍 Searching for: '{user_query[:50]}...'")
        
        # Create query embedding
        if self.embeddings:
            query_embedding = self.embeddings.embed_query(user_query)
        else:
            query_embedding = self._mock_embed(user_query)
        
        results = []
        
        if self.use_mock:
            # Mock mode: simple similarity search
            results = self._mock_search(query_embedding, top_k)
        else:
            # Real Pinecone search
            try:
                response = self.index.query(
                    vector=query_embedding,
                    top_k=top_k,
                    include_metadata=True
                )
                
                for match in response.matches:
                    results.append({
                        "text": match.metadata.get("source_text", ""),
                        "author_wallet": match.metadata.get("author_wallet", "0x0"),
                        "score": match.score,
                        "file_name": match.metadata.get("file_name", "unknown")
                    })
                    
            except Exception as e:
                print(f"⚠️ Pinecone query failed: {e}")
                # Fallback to mock search
                results = self._mock_search(query_embedding, top_k)
        
        print(f"📋 Found {len(results)} relevant chunks")
        return results
    
    def _mock_search(self, query_embedding: List[float], top_k: int) -> List[Dict[str, Any]]:
        """
        Perform similarity search on mock storage.
        
        Uses cosine similarity for ranking.
        """
        if not self.mock_storage:
            # Return demo data if storage is empty
            return self._get_demo_results()
        
        def cosine_similarity(a: List[float], b: List[float]) -> float:
            """Calculate cosine similarity between two vectors."""
            import math
            dot = sum(x * y for x, y in zip(a, b))
            norm_a = math.sqrt(sum(x * x for x in a))
            norm_b = math.sqrt(sum(x * x for x in b))
            if norm_a == 0 or norm_b == 0:
                return 0
            return dot / (norm_a * norm_b)
        
        # Calculate similarities
        scored = []
        for vector in self.mock_storage:
            sim = cosine_similarity(query_embedding, vector["values"])
            scored.append({
                "text": vector["metadata"]["source_text"],
                "author_wallet": vector["metadata"]["author_wallet"],
                "score": sim,
                "file_name": vector["metadata"].get("file_name", "unknown")
            })
        
        # Sort by score and return top_k
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]
    
    def _get_demo_results(self) -> List[Dict[str, Any]]:
        """
        Return demo results when no real data exists.
        
        This ensures the hackathon demo always shows something!
        """
        return [
            {
                "text": "Decentralized AI represents a paradigm shift where AI models and data are distributed across multiple nodes, ensuring no single entity controls the system.",
                "author_wallet": "0x742d35Cc6634C0532925a3b844Bc9e7595f5bE21",
                "score": 0.95,
                "file_name": "demo_knowledge.pdf"
            },
            {
                "text": "The x402 protocol enables micropayments for AI knowledge retrieval, compensating content creators fairly for their contributions to AI training.",
                "author_wallet": "0x8ba1f109551bD432803012645ac136c5E2C6bc29",
                "score": 0.88,
                "file_name": "demo_knowledge.pdf"
            },
            {
                "text": "Cronos EVM provides fast and low-cost transactions, making it ideal for micropayment use cases in decentralized applications.",
                "author_wallet": "0x1Cb45B3E8b0F2a9B2D6f07E3CfC19e50D2a7d3F1",
                "score": 0.82,
                "file_name": "demo_knowledge.pdf"
            }
        ]
    
    def get_stats(self) -> Dict[str, Any]:
        """Return statistics about the knowledge base."""
        if self.use_mock:
            return {
                "mode": "mock",
                "total_vectors": len(self.mock_storage),
                "pinecone_connected": False
            }
        else:
            try:
                stats = self.index.describe_index_stats()
                return {
                    "mode": "pinecone",
                    "total_vectors": stats.total_vector_count,
                    "pinecone_connected": True
                }
            except:
                return {
                    "mode": "unknown",
                    "total_vectors": 0,
                    "pinecone_connected": False
                }


# =============================================================================
# Quick test when running directly
# =============================================================================
if __name__ == "__main__":
    print("🧪 Testing RAG Engine...")
    engine = RAGEngine()
    
    # Test query
    results = engine.query("What is decentralized AI?")
    for r in results:
        print(f"\n📄 Score: {r['score']:.2f}")
        print(f"   Author: {r['author_wallet'][:20]}...")
        print(f"   Text: {r['text'][:100]}...")

