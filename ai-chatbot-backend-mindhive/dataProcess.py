import os
import json
from dotenv import load_dotenv
from uuid import uuid4
from langchain_pinecone import PineconeVectorStore, Pinecone
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from pinecone import Pinecone, ServerlessSpec

load_dotenv()
index_name  = "pinecone-chatbot"  

def pineconeConnect() :
    pinecone_api_key = os.environ["PINECONE_API_KEY"] 
    openai_api_key = os.environ["OPENAI_API_KEY"]  

    client = Pinecone(pinecone_api_key) 
    if not client.has_index(index_name):
        client.create_index(
            name=index_name,
            dimension=1536,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
    index = client.Index(index_name)
    return index

def load_docs(doc: str):
    with open(doc, "r", encoding="utf-8") as f:
        raw = f.read()
        data = json.loads(raw)
    return data["products"]

def format_chunk(product):
    lines = []
    lines.append(f"{product['product_name']}")
    lines.append("Variants:")

    for v in product["variants"]:
        availability = "Available" if v["available"] else "Not Available"
        lines.append(f"- {v['color']} – RM{v['price']} ({availability})")

    lines.append(f"Source: {product['source_url']}")
    return "\n".join(lines)
    
def preprocess_chunks(products):
    docs = []
    for p in products:
        chunk_text = format_chunk(p)

        doc = Document(
            page_content=chunk_text,
            metadata={
                "product_id": p["product_id"],
                "name": p["product_name"],
                "url": p["source_url"]
            }
        )
        docs.append(doc)
    return docs

def ingest_to_pinecone(docs):
    index = pineconeConnect()
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = PineconeVectorStore(
        index=index,
        embedding=embeddings
    )

    uuids = [str(uuid4()) for _ in range(len(docs))]

    print(f"[INFO] Uploading {len(docs)} documents into Pinecone…")
    vectorstore.add_documents(documents=docs, ids=uuids)
    print("[SUCCESS] Ingestion completed!")

def main():
    index = pineconeConnect()
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = PineconeVectorStore(
        index=index,
        embedding=embeddings
    )
    results = vectorstore.similarity_search(
        "most expensive tumblers",
        k=2
    )
    for res in results:
        print(f"* {res.page_content} [{res.metadata}]")

if __name__ == "__main__":
    #products = load_docs("zus_products_readable.txt")
    #data = preprocess_chunks(products)
    #ingest_to_pinecone(data)
    main()


    
