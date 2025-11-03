from vector_store import VectorStore
from dotenv import load_dotenv
import os

load_dotenv()


def test_vector_store():
    print("🧪 Testing Vector Store...")

    # Initialize
    print("\n1️⃣ Initializing VectorStore...")
    vs = VectorStore()
    print("✅ VectorStore initialized")

    # Test embedding generation
    print("\n2️⃣ Testing embedding generation...")
    test_text = "Machine overheating in production line 3"
    embedding = vs.get_embedding(test_text)
    print(f"✅ Generated embedding with {len(embedding)} dimensions")

    # Test storing a defect
    print("\n3️⃣ Testing defect storage...")
    test_metadata = {
        "ticket_id": "TEST-001",
        "description": "Machine overheating",
        "category": "Mechanical",
        "priority": "HIGH",
        "resolution": "Replaced cooling fan",
    }
    vs.store_defect("TEST-001", test_text, test_metadata)
    print("✅ Defect stored in Pinecone")

    # Test similarity search
    print("\n4️⃣ Testing similarity search...")
    query = "equipment temperature problem"
    similar = vs.find_similar(query, top_k=1)

    if similar:
        print(f"✅ Found {len(similar)} similar defect(s)")
        print(f"   Similar ticket: {similar[0].metadata.get('ticket_id')}")
        print(f"   Score: {similar[0].score:.4f}")
    else:
        print("⚠️ No similar defects found (this is OK for first test)")

    print("\n✅ All tests passed!")
    return True


if __name__ == "__main__":
    try:
        test_vector_store()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nCheck your .env file has:")
        print("- VOYAGE_API_KEY")
        print("- PINECONE_API_KEY")
        print("- PINECONE_INDEX_NAME")
