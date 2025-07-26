import os
import time
import re
import concurrent.futures
from pinecone import Pinecone, ServerlessSpec
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from tqdm import tqdm
from dotenv import load_dotenv

# Load API keys from .env
load_dotenv()

# Initialize embedding model
embed_model = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key="AIzaSyDyoAA9MRyZvBSLD45vp9xJdsuyJff3xDo"
)


# Initialize Pinecone
pc = Pinecone(api_key="pcsk_5dpELm_NtvrjntzjQt2by64KzgA8hDvm9gY6vSHDXdRA4CsL6G2wgMn6srfUAudeFznf4P")
index_name = 'sti-teenage-preg'  # Changed from 'hiv' to reflect new topic

# Create index if it doesn't exist
existing_indexes = pc.list_indexes()
existing_index_names = [index.name for index in existing_indexes.indexes]

if index_name not in existing_index_names:
    pc.create_index(
        name=index_name,
        dimension=768,
        metric='cosine',
        spec=ServerlessSpec(cloud='aws', region='us-east-1')
    )
    print(f"Created Pinecone index: {index_name}")
    time.sleep(60)  # Allow index to initialize

pinecone_index = pc.Index(index_name)

# Load PDFs from folder
pdf_folder_path = '../MyPadi/STI_TEENAGE_PREG'
documents = []

for filename in os.listdir(pdf_folder_path):
    if filename.endswith(".pdf"):
        loader = PyPDFLoader(os.path.join(pdf_folder_path, filename))
        documents.extend(loader.load())


print(f"\nLoaded {len(documents)} pages from {pdf_folder_path}\n")

# Split documents into chunks
def split_docs(documents, chunk_size=1500, chunk_overlap=100):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splitter.split_documents(documents)

docs = split_docs(documents)
print(f"Split into {len(docs)} chunks.\n")

# Retry helper for rate-limited requests
def parse_retry_wait_time(error):
    if hasattr(error, 'response') and error.response is not None:
        retry_after = error.response.headers.get('Retry-After')
        if retry_after:
            return int(retry_after)
    match = re.search(r'(\d+)s', str(error))
    return int(match.group(1)) if match else 20

# Embedding with retry logic
def embed_batch_with_retry(embed_model, batch_contents, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            return embed_model.embed_documents(batch_contents)
        except Exception as e:
            print(f"Error on attempt {attempt+1}: {e}")
            wait_time = parse_retry_wait_time(e)
            print(f"Waiting {wait_time}s before retrying...\n")
            time.sleep(wait_time)
            if attempt == max_attempts - 1:
                raise

# Embed concurrently
def concurrent_embed_documents(embed_model, documents, batch_size=50, max_workers=4):
    all_embeddings = []
    all_contents = []
    futures = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i+batch_size]
            batch_contents = [doc.page_content for doc in batch]
            futures.append((executor.submit(embed_batch_with_retry, embed_model, batch_contents), batch_contents))

        for future, contents in tqdm(futures, total=len(futures), desc="Embedding batches"):
            try:
                batch_embeddings = future.result()
                all_embeddings.extend(batch_embeddings)
                all_contents.extend(contents)
            except Exception as e:
                print(f"Error in embedding batch: {e}")

    return all_embeddings, all_contents

print("Generating embeddings...\n")
all_embeddings, all_batch_content = concurrent_embed_documents(embed_model, docs)
print(f"Generated {len(all_embeddings)} embeddings.\n")

# Prepare for upsert
vectors_to_upsert = [
    (str(idx), embedding, {"text": content})
    for idx, (embedding, content) in enumerate(zip(all_embeddings, all_batch_content))
]

# Batch upload to Pinecone
def batch_upsert(index, vectors, batch_size=100):
    batches = [vectors[i:i+batch_size] for i in range(0, len(vectors), batch_size)]
    for batch_number, batch in enumerate(tqdm(batches, desc="Upserting batches", total=len(batches))):
        for attempt in range(3):
            try:
                index.upsert(vectors=batch)
                break
            except Exception as e:
                print(f"Upsert error in batch {batch_number+1}, attempt {attempt+1}: {e}")
                if attempt < 2:
                    wait_time = 10 * (attempt + 1)
                    print(f"Retrying in {wait_time}s...\n")
                    time.sleep(wait_time)
                else:
                    print(f"Batch {batch_number+1} failed after 3 attempts.")
                    raise e

print("Uploading vectors to Pinecone...\n")
batch_upsert(pinecone_index, vectors_to_upsert)
print("\n✅ Pinecone vector storage complete!")
