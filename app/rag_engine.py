import os
import chromadb
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from groq import Groq

# Load environment variables from .env file
load_dotenv()

# 1. Initialize persistent ChromaDB client in root ./chroma_db folder
CHROMA_PATH = "./chroma_db"
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

# 2. Get or create collection for SnakeSense
collection = chroma_client.get_or_create_collection(name="snakesense_kb")

# 3. Load lightweight embedding model
print("⏳ Loading embedding model ('all-MiniLM-L6-v2')...")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
print("✅ Embedding model ready!")

# 4. Initialize Groq LLM Client
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

def index_knowledge_base(kb_dir: str = "data/knowledge_base"):
    """
    Reads text files from kb_dir, chunks content by paragraphs,
    generates embeddings, and saves them to local ChromaDB.
    """
    if collection.count() > 0:
        return

    if not os.path.exists(kb_dir):
        print(f"⚠️ Directory '{kb_dir}' not found.")
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

            raw_chunks = content.split("\n\n")
            for chunk in raw_chunks:
                clean_chunk = chunk.strip()
                if len(clean_chunk) > 40:
                    documents.append(clean_chunk)
                    metadatas.append({"source": file_name})
                    ids.append(f"doc_{doc_id_counter}")
                    doc_id_counter += 1

    if documents:
        embeddings = embedding_model.encode(documents).tolist()
        collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        print(f"✅ Successfully indexed {len(documents)} chunks into local ChromaDB!")

def retrieve_relevant_context(query: str, top_k: int = 3) -> str:
    """Encodes query and retrieves top_k matching chunks from ChromaDB."""
    if collection.count() == 0:
        index_knowledge_base()

    query_embedding = embedding_model.encode([query]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k
    )

    retrieved_chunks = results["documents"][0] if results.get("documents") else []
    return "\n\n---\n\n".join(retrieved_chunks)

def generate_rag_answer(user_query: str, species_context: str = "", language: str = "English") -> str:
    """
    Retrieves vector search context and generates a grounded, safe LLM answer.
    """
    if not groq_client:
        return "⚠️ GROQ_API_KEY is not set in your .env file. Please add your API key to proceed."

    # Retrieve matching WHO/NCDC and species chunks
    retrieved_kb = retrieve_relevant_context(user_query, top_k=3)

    system_prompt = f"""
You are SnakeSense AI, an expert decision support assistant for Indian herpetology and snakebite emergency guidance.

CRITICAL INSTRUCTIONS:
1. Ground your answer STRICTLY in the provided Clinical Knowledge Base and Vision Model Context.
2. NEVER invent medical or first-aid procedures. If medical advice is requested, ALWAYS emphasize urgent transport to a hospital with Polyvalent ASV.
3. If the retrieved context does not contain enough detail to answer, state clearly what is known and advise caution.
4. Respond in {language}.

CLINICAL & HERPETOLOGICAL KNOWLEDGE BASE (RETRIEVED FACTS):
{retrieved_kb}

VISION MODEL PREDICTION CONTEXT:
{species_context if species_context else "No active snake image uploaded in current session."}
"""

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            temperature=0.2 # Low temperature to enforce factual precision
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error communicating with LLM service: {str(e)}"

if __name__ == "__main__":
    index_knowledge_base()
    
    test_q = "Is a Common Krait active during the day or night, and what is its venom type?"
    print(f"\n🔍 Testing Full RAG + LLM Query: '{test_q}'\n")
    ans = generate_rag_answer(test_q)
    print("--- LLM ANSWER ---")
    print(ans)