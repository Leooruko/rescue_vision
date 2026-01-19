"""
ML Service for face detection using OpenCV.
Uses OpenCV Haar Cascade for face detection - optimized for Raspberry Pi.
"""
import os
import numpy as np
import pickle
import cv2
from pathlib import Path
from django.conf import settings
from django.core.files.storage import default_storage
import logging

logger = logging.getLogger('ml_service')

# OpenCV is required - assume it's installed via system package (python3-opencv)
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    logger.error("OpenCV (cv2) not available. Install via: sudo apt-get install python3-opencv")


class MLService:
    """
    ML Service for face detection using OpenCV Haar Cascade.
    Uses OpenCV for face detection - optimized for Raspberry Pi compatibility.
    """
    
    def __init__(self):
        """Initialize ML service with OpenCV Haar Cascade."""
        if not OPENCV_AVAILABLE:
            raise RuntimeError("OpenCV is required but not available")
        
        self.embeddings_dir = Path(settings.MEDIA_ROOT) / 'embeddings'
        self.embeddings_dir.mkdir(parents=True, exist_ok=True)
        
        self.similarity_threshold = settings.ML_SERVICE_CONFIG.get('SIMILARITY_THRESHOLD', 0.6)
        self.max_active_cases = settings.ML_SERVICE_CONFIG.get('MAX_ACTIVE_CASES', 20)
        
        # Load Haar Cascade classifier for face detection
        # OpenCV includes this cascade file - use cv2.data.haarcascades for reliable path
        try:
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            
            if self.face_cascade.empty():
                # Try alternative paths if default doesn't work
                cascade_paths = [
                    '/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml',
                    '/usr/local/share/opencv4/haarcascades/haarcascade_frontalface_default.xml',
                    '/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml',
                ]
                
                for path in cascade_paths:
                    if os.path.exists(path):
                        self.face_cascade = cv2.CascadeClassifier(path)
                        if not self.face_cascade.empty():
                            logger.info(f"Loaded Haar Cascade from: {path}")
                            break
                
                if self.face_cascade.empty():
                    raise RuntimeError("Failed to load Haar Cascade classifier from any path")
            else:
                logger.info(f"Loaded Haar Cascade from: {cascade_path}")
        except Exception as e:
            logger.error(f"Failed to load Haar Cascade: {str(e)}")
            raise RuntimeError("Haar Cascade classifier not available. Ensure OpenCV is properly installed.")
        
        # Store face crops/images instead of embeddings
        # Format: {case_id: [list of face_image_paths]}
        self.face_images_cache = {}
        self._load_face_images_cache()
    
    def _load_face_images_cache(self):
        """Load face images cache from disk."""
        try:
            cache_file = self.embeddings_dir / 'face_images_cache.pkl'
            if cache_file.exists():
                with open(cache_file, 'rb') as f:
                    self.face_images_cache = pickle.load(f)
                logger.info(f"Loaded {len(self.face_images_cache)} face image caches")
        except Exception as e:
            logger.error(f"Error loading face images cache: {str(e)}")
            self.face_images_cache = {}
    
    def _save_face_images_cache(self):
        """Save face images cache to disk."""
        try:
            cache_file = self.embeddings_dir / 'face_images_cache.pkl'
            with open(cache_file, 'wb') as f:
                pickle.dump(self.face_images_cache, f)
        except Exception as e:
            logger.error(f"Error saving face images cache: {str(e)}")
    
    def detect_faces(self, image_path):
        """
        Detect faces in an image using OpenCV Haar Cascade.
        
        Args:
            image_path: Path to image file
            
        Returns:
            List of face bounding boxes [(x, y, w, h), ...] or empty list if no faces detected
        """
        if not OPENCV_AVAILABLE or self.face_cascade is None:
            logger.error("OpenCV or Haar Cascade not available")
            return []
        
        try:
            if not os.path.exists(image_path):
                logger.error(f"Image file not found: {image_path}")
                return []
            
            # Read image using OpenCV
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"Failed to read image: {image_path}")
                return []
            
            # Convert to grayscale for face detection (Haar Cascade requires grayscale)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect faces using Haar Cascade
            # Parameters: scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30),
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            # Convert numpy array to list of tuples
            face_boxes = [(int(x), int(y), int(w), int(h)) for (x, y, w, h) in faces]
            
            if len(face_boxes) == 0:
                logger.debug(f"No faces detected in image: {image_path}")
            else:
                logger.debug(f"Detected {len(face_boxes)} face(s) in image: {image_path}")
            
            return face_boxes
        
        except Exception as e:
            logger.error(f"Error detecting faces in {image_path}: {str(e)}")
            return []
    
    def extract_face_crop(self, image_path, face_box):
        """
        Extract face crop from image given bounding box.
        
        Args:
            image_path: Path to image file
            face_box: Tuple (x, y, w, h) representing face bounding box
            
        Returns:
            Cropped face image (numpy array) or None
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                return None
            
            x, y, w, h = face_box
            # Ensure coordinates are within image bounds
            x = max(0, x)
            y = max(0, y)
            w = min(w, image.shape[1] - x)
            h = min(h, image.shape[0] - y)
            
            face_crop = image[y:y+h, x:x+w]
            return face_crop
        
        except Exception as e:
            logger.error(f"Error extracting face crop: {str(e)}")
            return None
    
    def compare_faces_histogram(self, face1, face2):
        """
        Compare two face images using histogram comparison.
        Simple method for face matching without embeddings.
        
        Args:
            face1: First face image (numpy array)
            face2: Second face image (numpy array)
            
        Returns:
            Similarity score (0-1), higher is more similar
        """
        try:
            # Resize faces to same size for comparison
            face1_resized = cv2.resize(face1, (100, 100))
            face2_resized = cv2.resize(face2, (100, 100))
            
            # Convert to grayscale
            face1_gray = cv2.cvtColor(face1_resized, cv2.COLOR_BGR2GRAY)
            face2_gray = cv2.cvtColor(face2_resized, cv2.COLOR_BGR2GRAY)
            
            # Calculate histogram
            hist1 = cv2.calcHist([face1_gray], [0], None, [256], [0, 256])
            hist2 = cv2.calcHist([face2_gray], [0], None, [256], [0, 256])
            
            # Compare histograms using correlation
            correlation = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
            
            # Normalize to 0-1 range (correlation is -1 to 1)
            similarity = (correlation + 1) / 2
            
            return similarity
        
        except Exception as e:
            logger.error(f"Error comparing faces: {str(e)}")
            return 0.0
    
    def extract_embedding(self, image_path):
        """
        Extract face detection result from an image.
        Maintains backward compatibility with existing code.
        
        Note: This function now returns face bounding boxes instead of embeddings.
        For actual matching, use detect_faces() and compare_faces_histogram().
        
        Args:
            image_path: Path to image file
            
        Returns:
            First face bounding box (x, y, w, h) as tuple or None if no face detected
        """
        face_boxes = self.detect_faces(image_path)
        
        if len(face_boxes) == 0:
            return None
        
        # Return first face bounding box for backward compatibility
        # Note: This is a bounding box, not an embedding
        return face_boxes[0]
    
    def process_missing_person_image(self, image_path, case_id):
        """
        Process a missing person image and store face crops for matching.
        
        Args:
            image_path: Path to image file
            case_id: UUID of missing person case
            
        Returns:
            Reference string (for backward compatibility)
        """
        # Detect faces in the image
        face_boxes = self.detect_faces(image_path)
        
        if len(face_boxes) == 0:
            raise ValueError("No face detected in image")
        
        # Extract and store face crops
        case_id_str = str(case_id)
        if case_id_str not in self.face_images_cache:
            self.face_images_cache[case_id_str] = []
        
        # Save face crops to disk
        face_crops_dir = self.embeddings_dir / 'face_crops' / case_id_str
        face_crops_dir.mkdir(parents=True, exist_ok=True)
        
        for idx, face_box in enumerate(face_boxes):
            face_crop = self.extract_face_crop(image_path, face_box)
            if face_crop is not None:
                # Save face crop as image
                crop_filename = f"face_{len(self.face_images_cache[case_id_str]) + idx}.jpg"
                crop_path = face_crops_dir / crop_filename
                cv2.imwrite(str(crop_path), face_crop)
                
                # Store reference
                self.face_images_cache[case_id_str].append(str(crop_path))
        
        self._save_face_images_cache()
        
        # Return reference for backward compatibility
        ref = f"{case_id_str}_{len(self.face_images_cache[case_id_str])}"
        logger.info(f"Processed image for case {case_id_str}, stored {len(face_boxes)} face(s)")
        
        return ref
    
    def match_embedding(self, query_face_data):
        """
        Match a detected face against stored missing person face crops.
        Maintains backward compatibility with existing code.
        
        Args:
            query_face_data: Can be bounding box tuple (x, y, w, h) or image path
                            For backward compatibility, accepts bounding box from extract_embedding()
            
        Returns:
            MissingPerson instance if match found, None otherwise
        """
        from cases.models import MissingPerson
        
        if query_face_data is None:
            return None
        
        # This function is called with a bounding box from extract_embedding()
        # We need the original image path to extract the face crop
        # For now, we'll need to modify the calling code to pass image path
        # But for backward compatibility, we'll handle both cases
        
        # If it's a tuple (bounding box), we can't match without the original image
        # This is a limitation - we'll need to modify the calling code
        # For now, return None to indicate no match (since we don't have the image)
        logger.warning("match_embedding called with bounding box - matching requires image path")
        return None
    
    def match_face_from_image(self, image_path):
        """
        Match faces detected in an image against stored missing person face crops.
        This is the new recommended method for face matching.
        
        Args:
            image_path: Path to query image file
            
        Returns:
            MissingPerson instance if match found, None otherwise
        """
        from cases.models import MissingPerson
        
        # Detect faces in query image
        face_boxes = self.detect_faces(image_path)
        
        if len(face_boxes) == 0:
            logger.debug(f"No faces detected in query image: {image_path}")
            return None
        
        # Extract first face crop from query image
        query_face_crop = self.extract_face_crop(image_path, face_boxes[0])
        if query_face_crop is None:
            return None
        
        best_match = None
        best_similarity = 0.0
        
        # Get all active cases
        active_cases = MissingPerson.objects.filter(status='ACTIVE')
        
        for case in active_cases:
            case_id_str = str(case.id)
            
            if case_id_str not in self.face_images_cache:
                continue
            
            # Compare against all stored face crops for this case
            for stored_face_path in self.face_images_cache[case_id_str]:
                if not os.path.exists(stored_face_path):
                    continue
                
                stored_face = cv2.imread(stored_face_path)
                if stored_face is None:
                    continue
                
                # Compare faces using histogram
                similarity = self.compare_faces_histogram(query_face_crop, stored_face)
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = case
        
        # Check if similarity exceeds threshold
        if best_similarity >= self.similarity_threshold:
            logger.info(f"Match found: Case {best_match.id} with similarity {best_similarity:.3f}")
            return best_match
        
        logger.debug(f"Best similarity: {best_similarity:.3f}, threshold: {self.similarity_threshold}")
        return None
    
    def remove_case_embeddings(self, case_id):
        """
        Remove face crops for a closed case.
        Maintains backward compatibility with existing code.
        
        Args:
            case_id: UUID of case to remove
        """
        case_id_str = str(case_id)
        if case_id_str in self.face_images_cache:
            # Delete face crop files
            face_crops_dir = self.embeddings_dir / 'face_crops' / case_id_str
            if face_crops_dir.exists():
                import shutil
                try:
                    shutil.rmtree(face_crops_dir)
                except Exception as e:
                    logger.error(f"Error deleting face crops directory: {str(e)}")
            
            del self.face_images_cache[case_id_str]
            self._save_face_images_cache()
            logger.info(f"Removed face crops for case {case_id}")
