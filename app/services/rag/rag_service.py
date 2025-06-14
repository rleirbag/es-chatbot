import logging
import chromadb
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config.settings import Settings

logger = logging.getLogger(__name__)


class RagService:
    def __init__(self):
        logger.info("Initializing RagService...")
        
        self.embedding_function = HuggingFaceEmbeddings(
            model_name='all-MiniLM-L6-v2'
        )
        
        self.client = chromadb.HttpClient(
            host=Settings().CHROMA_HOST,
            port=443,
            ssl=True
        )
        
        self.collection_name = Settings().CHROMA_COLLECTION
        
        try:
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name
            )
            logger.info(f"Collection '{self.collection_name}' ready.")
        except Exception as e:
            logger.error(f"Failed to initialize collection: {e}")
            raise e

    def process_document(self, file_path: str, original_filename: str, drive_link: str = None, g_file_id: str = None):
        """Process and store a document in the vector database."""
        logger.info(f"Processing document: {original_filename}")
        
        try:
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            logger.info(f"Loaded {len(documents)} pages from PDF")
            
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            chunks = text_splitter.split_documents(documents)
            logger.info(f"Split into {len(chunks)} chunks")
            
            ids = []
            texts = []
            metadatas = []
            
            for i, chunk in enumerate(chunks):
                ids.append(f"{original_filename}_{i}")
                texts.append(chunk.page_content)
                
                # Include Google Drive link and file ID in metadata
                metadata = {
                    "source": original_filename,
                    "chunk_id": i,
                    "page": chunk.metadata.get("page", 0)
                }
                
                if drive_link:
                    metadata["drive_link"] = drive_link
                    
                if g_file_id:
                    metadata["g_file_id"] = g_file_id
                    
                metadatas.append(metadata)
            
            # Generate embeddings
            embeddings = self.embedding_function.embed_documents(texts)
            logger.info("Generated embeddings")
            
            # Add to ChromaDB
            self.collection.add(
                ids=ids,
                documents=texts,
                metadatas=metadatas,
                embeddings=embeddings
            )
            
            logger.info(f"Successfully processed and stored {len(chunks)} chunks")
            return True
            
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            return False

    def search(self, query: str, k: int = 4):
        """Search for relevant documents."""
        logger.info(f"Searching for: '{query}'")
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_function.embed_query(query)
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=k
            )
            
            # Extract documents and metadata
            documents = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            logger.info(f"Found {len(documents)} relevant documents")
            
            # Return documents with their metadata
            search_results = []
            for doc, metadata in zip(documents, metadatas):
                search_results.append({
                    "content": doc,
                    "metadata": metadata
                })
            
            return search_results
            
        except Exception as e:
            logger.error(f"Error during search: {e}")
            return []

    def list_documents(self, limit: int = 100):
        """List all documents stored in the collection."""
        logger.info("Listing documents in collection...")
        
        try:
            # Get all documents (or up to limit)
            results = self.collection.get(limit=limit)
            
            documents = results.get("documents", [])
            metadatas = results.get("metadatas", [])
            ids = results.get("ids", [])
            
            logger.info(f"Found {len(documents)} documents in collection")
            
            # Return structured data
            doc_list = []
            for i, (doc_id, document, metadata) in enumerate(zip(ids, documents, metadatas)):
                doc_list.append({
                    "id": doc_id,
                    "content": document[:200] + "..." if len(document) > 200 else document,
                    "metadata": metadata,
                    "full_content": document
                })
            
            return doc_list
            
        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            return []

    def get_collection_info(self):
        """Get information about the collection."""
        try:
            count = self.collection.count()
            return {
                "collection_name": self.collection_name,
                "document_count": count,
                "status": "active"
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {"error": str(e)}

    def delete_by_g_file_id(self, g_file_id: str):
        """Delete all chunks of a document by its Google Drive file ID."""
        logger.info(f"Deleting document with g_file_id: {g_file_id}")
        
        try:
            # Get all documents to find those with matching g_file_id
            all_docs = self.collection.get()
            
            ids_to_delete = []
            metadatas = all_docs.get("metadatas", [])
            ids = all_docs.get("ids", [])
            
            for doc_id, metadata in zip(ids, metadatas):
                if metadata.get("g_file_id") == g_file_id:
                    ids_to_delete.append(doc_id)
            
            if ids_to_delete:
                self.collection.delete(ids=ids_to_delete)
                logger.info(f"Deleted {len(ids_to_delete)} chunks for g_file_id: {g_file_id}")
                return {"deleted_chunks": len(ids_to_delete), "g_file_id": g_file_id}
            else:
                logger.warning(f"No documents found with g_file_id: {g_file_id}")
                return {"deleted_chunks": 0, "g_file_id": g_file_id, "message": "No documents found"}
                
        except Exception as e:
            logger.error(f"Error deleting document by g_file_id: {e}")
            return {"error": str(e)}

    def delete_all_documents(self):
        """Delete all documents from the collection."""
        logger.warning("Deleting ALL documents from the collection")
        
        try:
            # Get count before deletion
            count_before = self.collection.count()
            
            # Delete the entire collection and recreate it
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(name=self.collection_name)
            
            logger.info(f"Deleted all documents. Count before: {count_before}")
            return {
                "message": "All documents deleted successfully",
                "deleted_count": count_before
            }
            
        except Exception as e:
            logger.error(f"Error deleting all documents: {e}")
            return {"error": str(e)} 