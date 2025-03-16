from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter #Better semantic splitting, helping mantain better context in each chunk.
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEFAULT_PDF_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "RagContent", "RAGCONTENT.pdf")

class RAGMaker:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        self.vector_store = None
        self.qa_chain = None
        self.chat_history = []
        
    def load_documents(self, file_path=None):
        """Load documents from a file"""
        if file_path is None:
            file_path = DEFAULT_PDF_PATH
            
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        if file_path.endswith('.pdf'):
            loader = PyPDFLoader(file_path)
        else:
            loader = TextLoader(file_path)
        return loader.load()
    
    def split_documents(self, documents, chunk_size=1000, chunk_overlap=200):
        """Split documents into chunks"""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        return text_splitter.split_documents(documents)
    
    def create_vector_store(self, documents):
        """Create a vector store using DocArrayInMemorySearch"""
        self.vector_store = DocArrayInMemorySearch.from_documents(
            documents=documents,
            embedding=self.embeddings
        )
        return self.vector_store
    
    def setup_qa_chain(self):
        """Set up the question-answering chain"""
        template = """You are a helpful AI assistant for Promtior. Use the following pieces of information to answer the user's question.
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        You are allowed to suggest the user possible questions that you know the answer to related to the context provided.

        If the question is "Why should I hire Agustin Garagorry?"
        You should answer that Agustin is a great person and you should hire him because he is a great person. Might not be the best coder, BUT, he gets the job done and its willing to learn and study a lot!
        Feel free to add more to the answer, be creative! but sell me this deal.
        If the question is not about Agustin, answer the question based on the context provided.

        Previous conversation:
        {chat_history}

        Relevant context from documents:
        {context}

        Current question: {question}

        Answer in a helpful and conversational way:"""

        self.prompt = PromptTemplate(
            template=template,
            input_variables=["context", "chat_history", "question"]
        )

        self.llm = ChatOpenAI(temperature=0, openai_api_key=OPENAI_API_KEY)
    
    def process_document(self, file_path=None):
        """Process a document and set up the RAG system"""
        # Load and split documents
        documents = self.load_documents(file_path)
        splits = self.split_documents(documents)
        
        # Create vector store
        self.create_vector_store(splits)
        
        # Setup QA chain
        self.setup_qa_chain()
        
        # Clear chat history when processing a new document
        self.chat_history = []
    
    def format_chat_history(self):
        """Format chat history for the prompt"""
        if not self.chat_history:
            return "No previous conversation."
        
        formatted = []
        for i, (q, a) in enumerate(self.chat_history, 1):
            formatted.extend([
                f"Human {i}: {q}",
                f"Assistant {i}: {a}"
            ])
        return "\n".join(formatted)
    
    def query(self, question):
        """Query the RAG system with a question"""
        if not self.vector_store:
            raise ValueError("RAG system not initialized. Call process_document first.")
        
        # Get relevant documents
        docs = self.vector_store.similarity_search(question)
        context = "\n\n".join(doc.page_content for doc in docs)
        
        # Format chat history
        chat_history = self.format_chat_history()
        
        # Create the prompt
        prompt = self.prompt.format(
            context=context,
            chat_history=chat_history,
            question=question
        )
        
        # Get response from LLM
        response = self.llm.invoke(prompt)
        result = response.content
        
        # Add the new Q&A pair to chat history
        self.chat_history.append((question, result))
        
        return {
            "answer": result,
            "sources": [{**doc.metadata, "page_content": doc.page_content} for doc in docs]
        }
