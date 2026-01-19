# Rescue Vision - Smart Missing Person Facial Detection System

A complete Django-based web application for reporting and detecting missing persons using facial recognition technology.

## Features

- **User Authentication**: Sign up, sign in, and manage user accounts
- **Case Management**: Report missing persons, upload images, and manage cases
- **Facial Recognition**: Pre-trained ML models for face detection and matching
- **Real-time Detection**: Integration with Raspberry Pi camera for live detection
- **Notifications**: Alert system for potential matches
- **Modern UI**: Beautiful, responsive web interface built with Tailwind CSS

## Technology Stack

- **Backend**: Django 4.2+, Django REST Framework
- **Database**: SQLite (default), PostgreSQL (production)
- **ML**: OpenCV Haar Cascade (face detection) - optimized for Raspberry Pi
- **Frontend**: Django Templates + Tailwind CSS
- **Integration**: RESTful APIs for Raspberry Pi C client

## Installation

### Prerequisites

- Python 3.8+
- pip
- Virtual environment (recommended)

### Setup Steps

1. **Clone the repository**
   ```bash
   cd rescue_vision
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

   **Note**: OpenCV should be installed via system package on Raspberry Pi:
   - **Raspberry Pi (Debian)**: `sudo apt-get install python3-opencv`
   - **Ubuntu/Debian**: `sudo apt-get install python3-opencv`
   - **macOS**: `brew install opencv-python` or use pip: `pip install opencv-python`
   - **Windows**: `pip install opencv-python`

4. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser** (optional, for admin access)
   ```bash
   python manage.py createsuperuser
   ```

6. **Run development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Web UI: http://127.0.0.1:8000/
   - Admin Panel: http://127.0.0.1:8000/admin/
   - API Root: http://127.0.0.1:8000/api/

## Project Structure

```
rescue_vision/
├── accounts/          # User authentication and management
├── cases/             # Missing person case management
├── media_ingest/      # Frame ingestion from Raspberry Pi
├── ml_service/        # Face recognition ML service
├── notifications/     # Detection notifications
├── ui/                # Frontend views and templates
├── core/              # Core utilities
├── templates/         # HTML templates
├── media/             # Uploaded media files
├── static/            # Static files (CSS, JS)
└── rescue_vision/     # Django project settings
```

## API Endpoints

### Authentication
- `POST /api/auth/signup/` - User registration
- `POST /api/auth/login/` - User login
- `GET /api/auth/me/` - Get current user

### Cases
- `GET /api/cases/` - List all cases
- `POST /api/cases/` - Create new case
- `GET /api/cases/my/` - Get user's cases
- `GET /api/cases/{id}/` - Get case details
- `PUT /api/cases/{id}/` - Update case
- `POST /api/cases/{id}/close/` - Close case
- `POST /api/cases/{id}/images/` - Upload case image

### Frame Ingestion (Raspberry Pi)
- `GET /api/frames/ready/` - Check if backend is ready
- `POST /api/frames/ingest/` - Send frame for processing

### Notifications
- `GET /api/notifications/` - List user notifications
- `POST /api/notifications/{id}/confirm/` - Confirm detection
- `POST /api/notifications/{id}/dismiss/` - Dismiss detection

## Raspberry Pi Integration

The system is designed to work with a C program running on Raspberry Pi that captures frames from a camera.

### C Client Example

A sample C client (`raspberry_pi_client.c`) is provided in the `clients/` directory. The client:

1. Polls `/api/frames/ready/` to check backend readiness
2. Captures frames from camera
3. Sends frames to `/api/frames/ingest/` via HTTP POST
4. Implements backpressure handling

### Integration Flow

1. **Backend Readiness Check**: C client polls `/api/frames/ready/` endpoint
2. **Frame Capture**: When ready, capture frame from camera
3. **Frame Upload**: POST frame image to `/api/frames/ingest/`
4. **Async Processing**: Backend processes frame asynchronously
5. **Notification**: On match, notification is created and user is alerted

## ML Service Configuration

The ML service uses OpenCV Haar Cascade for face detection. Configuration is in `settings.py`:

```python
ML_SERVICE_CONFIG = {
    'MAX_ACTIVE_CASES': 20,
    'SIMILARITY_THRESHOLD': 0.6,  # Histogram similarity threshold (0-1)
}
```

### How It Works

1. **Image Upload**: When a missing person image is uploaded, faces are detected using Haar Cascade
2. **Face Crop Storage**: Face crops are extracted and stored on disk for matching
3. **Frame Processing**: Incoming frames are processed to detect faces using Haar Cascade
4. **Matching**: Histogram comparison is used to match detected faces against stored face crops
5. **Threshold Check**: If similarity exceeds threshold, match is detected
6. **Notification**: User is notified of potential match

**Note**: This system uses face detection and simple image comparison. For production use, consider upgrading to more advanced face recognition methods.

## Usage Guide

### For Users

1. **Sign Up**: Create an account at `/signup/`
2. **Report Case**: Go to Dashboard → "Report Missing Person"
3. **Upload Images**: Add multiple photos of the missing person
4. **Monitor**: Check notifications page for detection alerts
5. **Confirm/Dismiss**: Review detection matches and confirm or dismiss

### For Administrators

- Access admin panel at `/admin/`
- Manage users, cases, and notifications
- Monitor system activity

## Security Considerations

- Authentication required for case management
- CSRF protection enabled
- Input validation on all endpoints
- Image file validation
- Rate limiting recommended for production

## Production Deployment

For production deployment:

1. Set `DEBUG = False` in `settings.py`
2. Change `SECRET_KEY` to a secure random value
3. Use PostgreSQL instead of SQLite
4. Configure proper static file serving
5. Set up Celery for async task processing
6. Use Redis for caching and message broker
7. Configure HTTPS
8. Set up proper logging and monitoring

## Troubleshooting

### OpenCV Installation Issues

If you encounter issues with OpenCV:

- **Raspberry Pi (Debian)**: Install via system package: `sudo apt-get install python3-opencv`
- **Linux**: `sudo apt-get install python3-opencv` or `pip install opencv-python`
- **macOS**: `brew install opencv-python` or `pip install opencv-python`
- **Windows**: `pip install opencv-python`

### ML Service Not Working

- Ensure OpenCV is installed: `python3 -c "import cv2; print(cv2.__version__)"`
- Check logs: `logs/rescue_vision.log`
- Verify Haar Cascade classifier is loaded (check logs)
- Ensure images contain clear, front-facing faces
- Adjust similarity threshold in `settings.py` if needed

## License

This project is for academic and educational purposes.

## Contributing

This is an academic project. For improvements or bug fixes, please follow standard Django best practices.

## Support

For issues or questions, please refer to the Django documentation or OpenCV documentation.
