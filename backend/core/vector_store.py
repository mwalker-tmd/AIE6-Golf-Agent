from backend.core.vectordatabase import VectorDatabase
from backend.core.text_utils import PDFLoader, TextFileLoader, CharacterTextSplitter
from backend.core.logging_config import logger

class VectorStore:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VectorStore, cls).__new__(cls)
            cls._instance.vector_db = None
            cls._instance.splitter = CharacterTextSplitter()
        return cls._instance
    
    def __init__(self):
        # This will only run once due to the singleton pattern
        if not hasattr(self, 'vector_db'):
            self.vector_db = None
            self.splitter = CharacterTextSplitter()

    async def process_file(self, file_path: str, is_pdf: bool) -> int:
        """Process a file and store its chunks in the vector database"""
        loader = PDFLoader(file_path) if is_pdf else TextFileLoader(file_path)
        documents = loader.load_documents()
        chunks = self.splitter.split_texts(documents)

        self.vector_db = VectorDatabase()
        await self.vector_db.abuild_from_list(chunks)
        return len(chunks)

    def search(self, query: str, k: int = 4):
        """Search the vector database for relevant context"""
        if self.vector_db is None:
            return []
        
        try:
            # Get search results from the vector database
            results = self.vector_db.search_by_text(query, k=k)
            
            # Ensure we're returning a list of tuples with (text, score)
            processed_results = []
            for result in results:
                if isinstance(result, tuple) and len(result) == 2:
                    # If it's already a tuple with (document, score)
                    doc, score = result
                    processed_results.append((str(doc.page_content), score))
                else:
                    # If it's just a document or something else
                    processed_results.append((str(result), 1.0))
            
            return processed_results
        except Exception as e:
            logger.error(f"Error in vector store search: {e}", exc_info=True)
            return []

    @property
    def is_initialized(self) -> bool:
        """Check if the vector database has been initialized"""
        return self.vector_db is not None 