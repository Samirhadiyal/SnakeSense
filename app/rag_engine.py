import os
import chromadb
from sentence_transformers import SentenceTransformer

# 1. Initialize persistent ChromaDB client in root ./chroma_db folder
CHROMA_PATH = "./chroma_db"
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

# 2. Get or create collection for SnakeSense
collection = chroma_client.get_or_create_collection(name="snakesense_kb")

# 3. Load lightweight embedding model (HuggingFace)
print("⏳ Loading embedding model ('all-MiniLM-L6-v2')...")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
print("✅ Embedding model ready!")

def index_knowledge_base(kb_dir: str = "data/knowledge_base"):
    """
    Reads text files from kb_dir, chunks content by paragraphs,
    generates embeddings, and saves them to local ChromaDB.
    """
    if collection.count() > 0:
        print(f"ℹ️ Knowledge Base already indexed in ChromaDB ({collection.count()} chunks found). Skipping re-indexing.")
        return

    if not os.path.exists(kb_dir):
        print(f"⚠️ Directory '{kb_dir}' not found. Cannot index knowledge base.")
        return

    print("⏳ Indexing Knowledge Base into ChromaDB...")
    documents = []
    metadatas = []
    ids = []
    doc_id_counter = 0

    for file_name in os.listdir(kb_dir):
        if file_name.endswith(".txt"):
            file_path = os.path.join(kb_dir, file_name)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Split content by double newlines to form distinct paragraph chunks
            raw_chunks = content.split("\n\n")
            
            for chunk in raw_chunks:
                clean_chunk = chunk.strip()
                # Store meaningful chunks (longer than 40 characters)
                if len(clean_chunk) > 40:
                    documents.append(clean_chunk)
                    metadatas.append({"source": file_name})
                    ids.append(f"doc_{doc_id_counter}")
                    doc_id_counter += 1

    if documents:
        print(f"⏳ Generating embeddings for {len(documents)} document chunks...")
        embeddings = embedding_model.encode(documents).tolist()
        
        collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        print(f"✅ Successfully indexed {len(documents)} chunks into local ChromaDB!")
    else:
        print("⚠️ No valid text chunks found to index.")

def retrieve_relevant_context(query: str, top_k: int = 3) -> str:
    """
    Encodes user query, performs vector search in ChromaDB,
    and returns top_k matching context chunks joined as string.
    """
    if collection.count() == 0:
        index_knowledge_base()

    query_embedding = embedding_model.encode([query]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k
    )

    retrieved_chunks = results["documents"][0] if results.get("documents") else []
    
    # Format retrieved chunks for LLM context injection
    return "\n\n---\n\n".join(retrieved_chunks)

if __name__ == "__main__":
    # Test script standalone execution
    index_knowledge_base()
    
    test_query = "What should I do if bitten by a Common Krait at night?"
    print(f"\n🔍 Testing Vector Search Query: '{test_query}'\n")
    context = retrieve_relevant_context(test_query, top_k=2)
    print("--- RETRIEVED CONTEXT ---")
    print(context)