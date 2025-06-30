from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Dict, Any


class RAGSourceType(Enum):
    """Enumeration of supported RAG source types."""
    NONE = "none"
    VECTORIZE = "vectorize"
    PINECONE = "pinecone"


class RAGSourceBase(ABC):
    """
    Abstract base class for RAG (Retrieval-Augmented Generation) sources.
    
    This defines the interface that all RAG source implementations must follow.
    """
    
    @abstractmethod
    def retrieve_documents(self, question: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents based on the question.
        
        Args:
            question (str): The question to search for
            num_results (int): Number of documents to retrieve
            
        Returns:
            List[Dict[str, Any]]: List of retrieved documents with metadata
        """
        pass
    
    @abstractmethod
    def get_required_env_vars(self) -> List[str]:
        """
        Get the list of required environment variables for this RAG source.
        
        Returns:
            List[str]: List of required environment variable names
        """
        pass 