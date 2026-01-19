# Migration to OpenCV - Summary

## Overview

The Rescue Vision project has been migrated from `face-recognition`/`dlib` to **OpenCV Haar Cascade** for face detection. This migration was necessary due to compatibility issues with Raspberry Pi running Debian 13 (Python 3.13).

## Changes Made

### 1. ML Service (`ml_service/services.py`)

**Removed:**
- All imports of `face_recognition` and `dlib`
- Embedding extraction and cosine similarity matching
- TensorFlow dependencies

**Added:**
- OpenCV Haar Cascade face detection
- Face crop extraction and storage
- Histogram-based face comparison
- Robust cascade classifier loading with fallback paths

**Key Methods:**
- `detect_faces(image_path)` - Detects faces using Haar Cascade, returns bounding boxes
- `extract_face_crop(image_path, face_box)` - Extracts face region from image
- `compare_faces_histogram(face1, face2)` - Compares faces using histogram correlation
- `match_face_from_image(image_path)` - New method for matching faces in query images
- `extract_embedding()` - Maintained for backward compatibility (now returns bounding box)
- `match_embedding()` - Maintained for backward compatibility (returns None - use `match_face_from_image()` instead)

### 2. Media Ingestion (`media_ingest/views.py`)

**Changed:**
- Updated `process_frame_async()` to use `match_face_from_image()` instead of embedding-based matching
- Removed embedding extraction step
- Direct face detection and matching from frame images

### 3. Dependencies (`requirements.txt`)

**Removed:**
- `face-recognition>=1.3.0`
- `dlib>=19.24.0`
- `opencv-python>=4.8.0` (now installed via system package)

**Note:** OpenCV should be installed via system package on Raspberry Pi:
```bash
sudo apt-get install python3-opencv
```

### 4. Documentation

**Updated:**
- `README.md` - Replaced all face-recognition references with OpenCV
- `QUICKSTART.md` - Updated installation and troubleshooting sections
- Added OpenCV installation instructions for Raspberry Pi

## Technical Details

### Face Detection

Uses OpenCV's `CascadeClassifier` with `haarcascade_frontalface_default.xml`:
- **Method**: Haar Cascade (Viola-Jones algorithm)
- **Grayscale conversion**: Required for detection
- **Parameters**: `scaleFactor=1.1`, `minNeighbors=5`, `minSize=(30, 30)`
- **Output**: Bounding boxes `(x, y, w, h)` for detected faces

### Face Matching

Uses histogram correlation for face comparison:
- **Method**: Histogram comparison (`cv2.HISTCMP_CORREL`)
- **Process**: 
  1. Resize faces to 100x100
  2. Convert to grayscale
  3. Calculate histograms
  4. Compare using correlation
  5. Normalize to 0-1 range
- **Threshold**: Configurable in `settings.py` (default: 0.6)

### Storage

**Old System:**
- Stored face embeddings (128-dimensional vectors)
- Used pickle for serialization

**New System:**
- Stores face crop images (JPEG files)
- Organized by case ID: `media/embeddings/face_crops/{case_id}/face_*.jpg`
- Uses pickle for metadata cache only

## Backward Compatibility

The following methods are maintained for backward compatibility but have changed behavior:

1. **`extract_embedding(image_path)`**
   - **Old**: Returns 128-dimensional embedding vector
   - **New**: Returns first face bounding box `(x, y, w, h)` or `None`
   - **Note**: This is a breaking change if code expects embedding vector

2. **`match_embedding(query_embedding)`**
   - **Old**: Matches embedding against stored embeddings
   - **New**: Returns `None` (matching requires image path)
   - **Note**: Use `match_face_from_image()` instead

## Migration Notes

### For Developers

1. **Replace `extract_embedding()` calls:**
   ```python
   # Old
   embedding = ml_service.extract_embedding(image_path)
   
   # New
   face_boxes = ml_service.detect_faces(image_path)
   ```

2. **Replace `match_embedding()` calls:**
   ```python
   # Old
   matched_case = ml_service.match_embedding(embedding)
   
   # New
   matched_case = ml_service.match_face_from_image(image_path)
   ```

3. **Face detection returns bounding boxes:**
   ```python
   face_boxes = ml_service.detect_faces(image_path)
   # Returns: [(x, y, w, h), ...] or []
   ```

### Performance Considerations

- **Haar Cascade** is faster than deep learning models
- **Histogram comparison** is simpler but less accurate than embedding-based matching
- **Face crops** require more disk space than embeddings
- **Matching** may be less accurate - consider adjusting threshold

### Limitations

1. **No identity recognition**: System detects faces but matching is based on simple image comparison
2. **Accuracy**: Histogram comparison is less accurate than embedding-based methods
3. **Lighting sensitivity**: Performance may vary with lighting conditions
4. **Pose sensitivity**: Works best with front-facing faces

## Testing

### Verify OpenCV Installation

```bash
python3 -c "import cv2; print(cv2.__version__)"
```

### Test Face Detection

```python
from ml_service.services import MLService

ml_service = MLService()
face_boxes = ml_service.detect_faces('test_image.jpg')
print(f"Detected {len(face_boxes)} face(s)")
```

### Test Face Matching

```python
from ml_service.services import MLService

ml_service = MLService()
matched_case = ml_service.match_face_from_image('query_image.jpg')
if matched_case:
    print(f"Match found: {matched_case.name}")
```

## Future Improvements

Consider these enhancements for production:

1. **Better matching algorithm**: Upgrade to more sophisticated methods (e.g., LBPH, Eigenfaces)
2. **Face alignment**: Normalize face orientation before comparison
3. **Multiple face handling**: Handle multiple faces in single image
4. **Confidence scores**: Return confidence scores with matches
5. **Deep learning models**: Consider lightweight models (MobileNet, etc.) if performance allows

## Support

For issues related to:
- **OpenCV installation**: Check system package manager
- **Haar Cascade loading**: Verify OpenCV data directory
- **Face detection**: Check image quality and lighting
- **Matching accuracy**: Adjust similarity threshold in `settings.py`

## References

- [OpenCV Face Detection Documentation](https://docs.opencv.org/4.x/d7/d8b/tutorial_py_face_detection.html)
- [Haar Cascade Classifiers](https://docs.opencv.org/4.x/db/d28/tutorial_cascade_classifier.html)
- [Histogram Comparison](https://docs.opencv.org/4.x/d6/dc7/group__imgproc__hist.html)
