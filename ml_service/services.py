"""
ML Service for face recognition and matching.
Uses pre-trained models only - no training allowed.
"""
import os
import numpy as np
import pickle
from pathlib import Path
from django.conf import settings
from django.core.files.storage import default_storage
import logging

logger = logging.getLogger('ml_service')

# Try to import face recognition libraries
try:
    import cv2
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError as e:
    FACE_RECOGNITION_AVAILABLE = False
    logger.warning(f"face_recognition library not available: {str(e)}. Install with: pip install face-recognition")

try:
    from tensorflow import keras
    from tensorflow.keras.models import load_model
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    logger.warning("TensorFlow not available. Using face_recognition library fallback.")


class MLService:
    """
    ML Service for face recognition.
    Uses pre-trained models to extract embeddings and match faces.
    """
    
    def __init__(self):
        """Initialize ML service."""
        self.embeddings_dir = Path(settings.MEDIA_ROOT) / 'embeddings'
        self.embeddings_dir.mkdir(parents=True, exist_ok=True)
        
        self.similarity_threshold = settings.ML_SERVICE_CONFIG.get('SIMILARITY_THRESHOLD', 0.6)
        self.max_active_cases = settings.ML_SERVICE_CONFIG.get('MAX_ACTIVE_CASES', 20)
        
        # Load or initialize embeddings storage
        self.embeddings_cache = {}
        self._load_embeddings_cache()
    
    def _load_embeddings_cache(self):
        """Load embeddings cache from disk."""
        try:
            cache_file = self.embeddings_dir / 'embeddings_cache.pkl'
            if cache_file.exists():
                with open(cache_file, 'rb') as f:
                    self.embeddings_cache = pickle.load(f)
                logger.info(f"Loaded {len(self.embeddings_cache)} embeddings from cache")
        except Exception as e:
            logger.error(f"Error loading embeddings cache: {str(e)}")
            self.embeddings_cache = {}
    
    def _save_embeddings_cache(self):
        """Save embeddings cache to disk."""
        try:
            cache_file = self.embeddings_dir / 'embeddings_cache.pkl'
            with open(cache_file, 'wb') as f:
                pickle.dump(self.embeddings_cache, f)
        except Exception as e:
            logger.error(f"Error saving embeddings cache: {str(e)}")
    
    def extract_embedding(self, image_path):
        """
        Extract face embedding from an image.
        
        Args:
            image_path: Path to image file
            
        Returns:
            numpy array of face embedding or None if no face detected
        """
        if not FACE_RECOGNITION_AVAILABLE:
            logger.error("face_recognition library not available")
            return None
        
        try:
            if not os.path.exists(image_path):
                logger.error(f"Image file not found: {image_path}")
                return None
            
            # Load image
            image = face_recognition.load_image_file(image_path)
            
            # Detect faces and extract embeddings
            face_encodings = face_recognition.face_encodings(image)
            
            if len(face_encodings) == 0:
                logger.warning(f"No face detected in image: {image_path}")
                return None
            
            # Use the first face found
            embedding = face_encodings[0]
            
            return embedding
        
        except Exception as e:
            logger.error(f"Error extracting embedding from {image_path}: {str(e)}")
            return None
    
    def process_missing_person_image(self, image_path, case_id):
        """
        Process a missing person image and store its embedding.
        
        Args:
            image_path: Path to image file
            case_id: UUID of missing person case
            
        Returns:
            Embedding reference string
        """
        embedding = self.extract_embedding(image_path)
        
        if embedding is None:
            raise ValueError("No face detected in image")
        
        # Store embedding with case ID as key
        if case_id not in self.embeddings_cache:
            self.embeddings_cache[case_id] = []
        
        self.embeddings_cache[case_id].append(embedding)
        self._save_embeddings_cache()
        
        # Return reference
        embedding_ref = f"{case_id}_{len(self.embeddings_cache[case_id])}"
        logger.info(f"Processed image for case {case_id}, embedding reference: {embedding_ref}")
        
        return embedding_ref
    
    def match_embedding(self, query_embedding):
        """
        Match a query embedding against stored missing person embeddings.
        
        Args:
            query_embedding: numpy array of face embedding to match
            
        Returns:
            MissingPerson instance if match found, None otherwise
        """
        from cases.models import MissingPerson
        
        if query_embedding is None:
            return None
        
        best_match = None
        best_similarity = 0.0
        
        # Get all active cases
        active_cases = MissingPerson.objects.filter(status='ACTIVE')
        
        for case in active_cases:
            case_id = str(case.id)
            
            if case_id not in self.embeddings_cache:
                continue
            
            # Compare against all embeddings for this case
            for stored_embedding in self.embeddings_cache[case_id]:
                # Calculate cosine similarity
                similarity = self._cosine_similarity(query_embedding, stored_embedding)
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = case
        
        # Check if similarity exceeds threshold
        if best_similarity >= self.similarity_threshold:
            logger.info(f"Match found: Case {best_match.id} with similarity {best_similarity:.3f}")
            return best_match
        
        logger.debug(f"Best similarity: {best_similarity:.3f}, threshold: {self.similarity_threshold}")
        return None
    
    def _cosine_similarity(self, vec1, vec2):
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Cosine similarity score (0-1)
        """
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        # Normalize to 0-1 range (cosine similarity is -1 to 1)
        return (similarity + 1) / 2
    
    def remove_case_embeddings(self, case_id):
        """
        Remove embeddings for a closed case.
        
        Args:
            case_id: UUID of case to remove
        """
        case_id_str = str(case_id)
        if case_id_str in self.embeddings_cache:
            del self.embeddings_cache[case_id_str]
            self._save_embeddings_cache()
            logger.info(f"Removed embeddings for case {case_id}")
