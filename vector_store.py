import os
import voyageai
from pinecone import Pinecone
from typing import List, Dict


class VectorStore:
    def __init__(self):
        # Initialize Voyage AI for embeddings
        self.voyage = voyageai.Client(api_key=os.getenv("VOYAGE_API_KEY"))

        # Initialize Pinecone
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.index = self.pc.Index(os.getenv("PINECONE_INDEX_NAME", "defects"))

    def get_embedding(self, text: str) -> List[float]:
        """Generate embedding using Voyage AI"""
        result = self.voyage.embed(
            texts=[text], model="voyage-2", input_type="document"
        )
        return result.embeddings[0]

    def store_defect(self, ticket_id: str, description: str, metadata: Dict):
        """Store defect embedding in Pinecone"""
        embedding = self.get_embedding(description)
        self.index.upsert(vectors=[(ticket_id, embedding, metadata)])

    def find_similar(self, query: str, top_k: int = 5) -> List[Dict]:
        """Find similar defects by semantic search"""
        query_embedding = self.get_embedding(query)
        results = self.index.query(
            vector=query_embedding, top_k=top_k, include_metadata=True
        )
        return results.matches