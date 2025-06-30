import os
from typing import List, Dict, Any
import vectorize_client as v
from rag_source_base import RAGSourceBase


class VectorizeWrapper(RAGSourceBase):
    """
    Vectorize.io RAG source implementation.
    
    This class handles document retrieval using Vectorize.io's API.
    """
    
    def __init__(self):
        """Initialize the Vectorize client with credentials from environment variables."""
        self.org_id = os.getenv("VECTORIZE_ORGANIZATION_ID")
        self.access_token = os.getenv("VECTORIZE_PIPELINE_ACCESS_TOKEN")
        self.pipeline_id = os.getenv("VECTORIZE_PIPELINE_ID")
        
        if not all([self.org_id, self.access_token, self.pipeline_id]):
            raise ValueError("Missing required Vectorize environment variables")
        
        # Initialize the Vectorize API client
        self.api = v.ApiClient(v.Configuration(access_token=self.access_token))
        self.pipelines_api = v.PipelinesApi(self.api)
    
    def retrieve_documents(self, question: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve documents from Vectorize based on the question.
        
        Args:
            question (str): The question to search for
            num_results (int): Number of documents to retrieve
            
        Returns:
            List[Dict[str, Any]]: List of retrieved documents with content and metadata
        """
        try:
            # Use Vectorize API to retrieve documents
            response = self.pipelines_api.retrieve_documents(
                self.org_id, 
                self.pipeline_id, 
                v.RetrieveDocumentsRequest(
                    question=question,
                    num_results=num_results,
                )
            )
            
            # Format the response for consistent interface
            documents = []
            for doc in response.documents:
                formatted_doc = {
                    "content": doc.text,
                    "metadata": {
                        "score": getattr(doc, 'score', None),
                        "source": "vectorize",
                        **getattr(doc, 'metadata', {})
                    }
                }
                documents.append(formatted_doc)
            
            return documents
            
        except Exception as e:
            print(f"Error retrieving documents from Vectorize: {e}")
            return []
    
    def get_required_env_vars(self) -> List[str]:
        """
        Get the list of required environment variables for Vectorize.
        
        Returns:
            List[str]: List of required environment variable names
        """
        return [
            "OPENAI_API_KEY",
            "VECTORIZE_ORGANIZATION_ID",
            "VECTORIZE_PIPELINE_ACCESS_TOKEN", 
            "VECTORIZE_PIPELINE_ID"
        ] 