import chromadb
client = chromadb.PersistentClient(path="./data/chroma_db")
collection = client.get_collection(name="immigration_docs")

def get_context(query):
    # Route logic: Use keywords to pick metadata filter
    instr_keywords = ["fee", "mail", "send", "address", "photo", "sign"]
    source_type = "form_instr" if any(k in query.lower() for k in instr_keywords) else "policy_manual"
    
    results = collection.query(
        query_texts=[query],
        n_results=3,
        where={"type": source_type}
    )
    return results['documents'][0], results['metadatas'][0]