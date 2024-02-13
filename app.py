from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import DirectoryLoader
from InstructorEmbedding import INSTRUCTOR
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from transformers import AutoTokenizer, AutoModelForCausalLM
import pickle
import faiss
from langchain_community.vectorstores import FAISS
from pprint import  pprint
import textwrap
import os
from dotenv import load_dotenv
from langchain_community.llms import HuggingFaceHub

# load env
load_dotenv()

# load pdf from a directory
loader = DirectoryLoader(f'./Documents/', glob="./*.pdf", loader_cls=PyPDFLoader)
documents = loader.load()

# chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
texts = text_splitter.split_documents(documents)

def store_embeddings(docs, embeddings, sotre_name, path):
    vectorStore = FAISS.from_documents(docs, embeddings)
    with open(f"{path}/faiss_{sotre_name}.pkl", "wb") as f:
        pickle.dump(vectorStore, f)

def load_embeddings(sotre_name, path):
    with open(f"{path}/faiss_{sotre_name}.pkl", "rb") as f:
        VectorStore = pickle.load(f)
    return VectorStore

instructor_embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-xl")
Embedding_store_path = f"./Embedding_store"

# store_embeddings(texts, instructor_embeddings, sotre_name='instructEmbeddings', path=Embedding_store_path)
# db_instructEmbedd = load_embeddings(sotre_name='instructEmbeddings', path=Embedding_store_path)

db_instructEmbedd = FAISS.from_documents(texts, instructor_embeddings)
retriever = db_instructEmbedd.as_retriever(search_kwargs={"k": 3})
retriever.search_type
retriever.search_kwargs
docs = retriever.get_relevant_documents("What is Operating System?")
# pprint(docs[0])
# pprint(docs[1])
# pprint(docs[2])

# Initialize the model 

# Smaug-72B
# model_smaug = ollama.Model("smaug-72b")

# falcon-7b

os.environ["HUGGINGFACEHUB_API_TOKEN"]
llm=HuggingFaceHub(repo_id="tiiuae/falcon-7b-instruct", model_kwargs={"temperature":0.1 ,"max_length":512})


# create the chain to answer questions 
qa_chain_instrucEmbed = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=True)

## Cite sources
def wrap_text_preserve_newlines(text, width=110):
    # Split the input text into lines based on newline characters
    lines = text.split('\n')
    # Wrap each line individually
    wrapped_lines = [textwrap.fill(line, width=width) for line in lines]
    # Join the wrapped lines back together using newline characters
    wrapped_text = '\n'.join(wrapped_lines)
    return wrapped_text

def process_llm_response(llm_response):
    print(wrap_text_preserve_newlines(llm_response['result']))
    print('\nSources:')
    for source in llm_response["source_documents"]:
        print(source.metadata['source'])

query = 'What is operating system?'

# print('-------------------Instructor Embeddings------------------\n')
llm_response = qa_chain_instrucEmbed(query)
process_llm_response(llm_response)