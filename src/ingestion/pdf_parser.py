import os
from pypdf import PdfReader
import chromadb

client = chromadb.PersistentClient(path="./data/chroma_db")
collection = client.get_or_create_collection(name="immigration_docs")

def process_pdfs():
    base_path = "./data/raw_pdfs"
    for category in ["policy_manual", "form_instr"]:
        folder_path = os.path.join(base_path, category)
        for filename in os.listdir(folder_path):
            if filename.endswith(".pdf"):
                print(f"Processing {filename}...")
                reader = PdfReader(os.path.join(folder_path, filename))
                for i, page in enumerate(reader.pages):
                    text = page.extract_text()
                    metadata = {"type": category, "source": filename, "page": i+1}
                    collection.add(
                        documents=[text],
                        metadatas=[metadata],
                        ids=[f"{filename}_{i}"]
                    )

if __name__ == "__main__":
    process_pdfs()