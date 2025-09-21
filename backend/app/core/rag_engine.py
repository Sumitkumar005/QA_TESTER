import os
import logging
import numpy as np
import pickle
from typing import List, Dict, Any, Optional, Tuple
from sentence_transformers import SentenceTransformer
import faiss
from pathlib import Path

from app.config.settings import get_settings
from app.models.analysis import CodeIssue, AnalysisResult

logger = logging.getLogger(__name__)
settings = get_settings()

class RAGEngine:
    """Retrieval-Augmented Generation engine for code analysis"""
    
    def __init__(self):
        self.model = None
        self.index = None
        self.documents = []
        self.metadata = []
        self.initialized = False
        
    async def initialize(self):
        """Initialize the RAG engine"""
        try:
            # Load sentence transformer model
            self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
            
            # Create or load FAISS index
            index_path = Path(settings.FAISS_INDEX_PATH)
            if index_path.exists():
                await self._load_index()
            else:
                await self._create_index()
            
            self.initialized = True
            logger.info("RAG engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG engine: {str(e)}")
            self.initialized = False
    
    async def _create_index(self):
        """Create a new FAISS index"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(settings.FAISS_INDEX_PATH), exist_ok=True)
            
            # Initialize with a small dimension (will be resized when first documents are added)
            dimension = 384  # Default for all-MiniLM-L6-v2
            self.index = faiss.IndexFlatL2(dimension)
            
            logger.info("Created new FAISS index")
            
        except Exception as e:
            logger.error(f"Failed to create FAISS index: {str(e)}")
            raise
    
    async def _load_index(self):
        """Load existing FAISS index"""
        try:
            index_file = f"{settings.FAISS_INDEX_PATH}/index.faiss"
            metadata_file = f"{settings.FAISS_INDEX_PATH}/metadata.pkl"
            documents_file = f"{settings.FAISS_INDEX_PATH}/documents.pkl"
            
            if all(os.path.exists(f) for f in [index_file, metadata_file, documents_file]):
                self.index = faiss.read_index(index_file)
                
                with open(metadata_file, 'rb') as f:
                    self.metadata = pickle.load(f)
                
                with open(documents_file, 'rb') as f:
                    self.documents = pickle.load(f)
                
                logger.info(f"Loaded FAISS index with {len(self.documents)} documents")
            else:
                await self._create_index()
                
        except Exception as e:
            logger.error(f"Failed to load FAISS index: {str(e)}")
            await self._create_index()
    
    async def save_index(self):
        """Save FAISS index and metadata"""
        try:
            os.makedirs(os.path.dirname(settings.FAISS_INDEX_PATH), exist_ok=True)
            
            index_file = f"{settings.FAISS_INDEX_PATH}/index.faiss"
            metadata_file = f"{settings.FAISS_INDEX_PATH}/metadata.pkl"
            documents_file = f"{settings.FAISS_INDEX_PATH}/documents.pkl"
            
            faiss.write_index(self.index, index_file)
            
            with open(metadata_file, 'wb') as f:
                pickle.dump(self.metadata, f)
            
            with open(documents_file, 'wb') as f:
                pickle.dump(self.documents, f)
            
            logger.info("Saved FAISS index successfully")
            
        except Exception as e:
            logger.error(f"Failed to save FAISS index: {str(e)}")
    
    async def index_analysis_result(self, result: AnalysisResult):
        """Index an analysis result for RAG retrieval"""
        if not self.initialized:
            await self.initialize()
        
        if not self.initialized:
            logger.warning("RAG engine not initialized, skipping indexing")
            return
        
        try:
            documents = []
            metadata = []
            
            # Index repository-level information
            repo_doc = f"Repository analysis: {result.source_info.get('path', 'unknown')}\n"
            if result.metrics:
                repo_doc += f"Languages: {', '.join(result.metrics.languages.keys())}\n"
                repo_doc += f"Total files: {result.metrics.total_files}\n"
                repo_doc += f"Total lines: {result.metrics.total_lines}\n"
                repo_doc += f"Average complexity: {result.metrics.complexity_average:.2f}\n"
            
            documents.append(repo_doc)
            metadata.append({
                'type': 'repository',
                'report_id': result.report_id,
                'source_path': result.source_info.get('path', 'unknown')
            })
            
            # Index issues
            for issue in result.issues:
                issue_doc = f"Issue: {issue.title}\n"
                issue_doc += f"Category: {issue.category.value}\n"
                issue_doc += f"Severity: {issue.severity.value}\n"
                issue_doc += f"Description: {issue.description}\n"
                issue_doc += f"File: {issue.file_path}\n"
                if issue.code_snippet:
                    issue_doc += f"Code: {issue.code_snippet}\n"
                issue_doc += f"Suggestion: {issue.suggestion}\n"
                
                documents.append(issue_doc)
                metadata.append({
                    'type': 'issue',
                    'report_id': result.report_id,
                    'issue_id': issue.id,
                    'category': issue.category.value,
                    'severity': issue.severity.value,
                    'file_path': issue.file_path
                })
            
            # Index file metrics
            for file_metric in result.file_metrics:
                file_doc = f"File analysis: {file_metric.file_path}\n"
                file_doc += f"Language: {file_metric.language}\n"
                file_doc += f"Lines of code: {file_metric.lines_of_code}\n"
                file_doc += f"Complexity: {file_metric.complexity:.2f}\n"
                file_doc += f"Maintainability: {file_metric.maintainability_index:.2f}\n"
                file_doc += f"Issues count: {file_metric.issues_count}\n"
                
                documents.append(file_doc)
                metadata.append({
                    'type': 'file_metric',
                    'report_id': result.report_id,
                    'file_path': file_metric.file_path,
                    'language': file_metric.language
                })
            
            # Generate embeddings
            embeddings = self.model.encode(documents)
            
            # Add to FAISS index
            self.index.add(embeddings.astype('float32'))
            
            # Add to local storage
            self.documents.extend(documents)
            self.metadata.extend(metadata)
            
            # Save periodically
            if len(self.documents) % 100 == 0:
                await self.save_index()
            
            logger.info(f"Indexed {len(documents)} documents for report {result.report_id}")
            
        except Exception as e:
            logger.error(f"Failed to index analysis result: {str(e)}")
    
    async def search(self, query: str, k: int = 5, report_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for relevant documents using RAG"""
        if not self.initialized or not self.documents:
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.model.encode([query])
            
            # Search in FAISS index
            scores, indices = self.index.search(query_embedding.astype('float32'), min(k, len(self.documents)))
            
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.documents):
                    doc_metadata = self.metadata[idx]
                    
                    # Filter by report_id if specified
                    if report_id and doc_metadata.get('report_id') != report_id:
                        continue
                    
                    results.append({
                        'document': self.documents[idx],
                        'metadata': doc_metadata,
                        'score': float(score),
                        'similarity': 1.0 / (1.0 + score)  # Convert L2 distance to similarity
                    })
            
            # Sort by similarity (higher is better)
            results.sort(key=lambda x: x['similarity'], reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"RAG search failed: {str(e)}")
            return []
    
    async def get_relevant_context(self, query: str, report_id: Optional[str] = None) -> str:
        """Get relevant context for a query"""
        results = await self.search(query, k=3, report_id=report_id)
        
        if not results:
            return "No relevant information found."
        
        context_parts = []
        for result in results:
            if result['similarity'] > 0.5:  # Only include relevant results
                context_parts.append(result['document'])
        
        return "\n\n".join(context_parts[:3])  # Limit to top 3 results
    
    async def cleanup_old_data(self, max_reports: int = 1000):
        """Clean up old data to prevent unbounded growth"""
        if len(self.documents) <= max_reports:
            return
        
        try:
            # Keep only the most recent reports
            # This is a simplified cleanup - in production, you might want more sophisticated logic
            keep_count = max_reports // 2
            
            self.documents = self.documents[-keep_count:]
            self.metadata = self.metadata[-keep_count:]
            
            # Rebuild index with remaining documents
            if self.documents:
                embeddings = self.model.encode(self.documents)
                dimension = embeddings.shape[1]
                self.index = faiss.IndexFlatL2(dimension)
                self.index.add(embeddings.astype('float32'))
            else:
                await self._create_index()
            
            await self.save_index()
            logger.info(f"Cleaned up RAG data, kept {len(self.documents)} documents")
            
        except Exception as e:
            logger.error(f"Failed to cleanup RAG data: {str(e)}")

# Global RAG engine instance
rag_engine = RAGEngine()