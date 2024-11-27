import os
import requests
from langchain.text_splitter import RecursiveCharacterTextSplitter
from tqdm import tqdm

def main():
	docs_path = "docs"
	url = "http://0.0.0.0:8001/add_to_rag_db/"
	headers = {"Authorization": os.getenv("YOUR_TOKEN")}
	chunk_size = 1200
	chunk_overlap = 50

	text_splitter = RecursiveCharacterTextSplitter(
		chunk_size=chunk_size, chunk_overlap=chunk_overlap, length_function=len)

	for doc in tqdm(os.listdir(docs_path)):
		doc_path = os.path.join(docs_path, doc)
		if os.path.isfile(doc_path):
			with open(doc_path, "r", encoding="utf-8") as file:
				text = file.read()
			chunks = text_splitter.split_text(text)

			for i, chunk in enumerate(chunks):
				resp = requests.post(
					url,
					json={"text": chunk},
					headers=headers
				)
				if resp.status_code == 200:
					print(f"Uploaded chunk {i+1} of document {doc}")
				else:
					print(f"Error uploading chunk {i+1} of document {doc}: {resp.status_code} {resp.text}")

if __name__ == "__main__":
	main()