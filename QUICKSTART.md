# Quick Start Guide - Rescue Vision

## Installation (5 minutes)

### 1. Install Python Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

**Note**: Installing `dlib` and `face-recognition` may require system dependencies:
- **Ubuntu/Debian**: `sudo apt-get install cmake libopenblas-dev liblapack-dev`
- **macOS**: `brew install cmake`
- **Windows**: Usually works with pip directly

### 2. Setup Database

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 4. Run Server

```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000/

## First Steps

1. **Sign Up**: Create an account at `/signup/`
2. **Report Case**: Go to Dashboard → "Report Missing Person"
3. **Upload Images**: Add photos of the missing person
4. **View Cases**: Check your dashboard for all cases

## Testing the System

### Test Case Creation

1. Sign in to your account
2. Click "Report Missing Person"
3. Fill in:
   - Name: "John Doe"
   - Description: "Missing since yesterday"
   - Upload a clear face photo
4. Submit

### Test Frame Ingestion (Raspberry Pi)

The system is ready to receive frames from Raspberry Pi:

1. **Check Readiness**: 
   ```bash
   curl http://localhost:8000/api/frames/ready/
   ```

2. **Send Test Frame**:
   ```bash
   curl -X POST -F "image=@test_image.jpg" http://localhost:8000/api/frames/ingest/
   ```

### Test Notifications

When a match is detected:
1. Check `/notifications/` page
2. View matched image
3. Confirm or dismiss the detection

## API Testing

### Get Auth Token

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -d "username=your_username&password=your_password"
```

### Create Case

```bash
curl -X POST http://localhost:8000/api/cases/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -F "name=Test Case" \
  -F "description=Test description"
```

### Upload Image

```bash
curl -X POST http://localhost:8000/api/cases/CASE_ID/images/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -F "image=@photo.jpg"
```

## Troubleshooting

### face-recognition Installation Issues

If you get errors installing `face-recognition`:

**Linux**:
```bash
sudo apt-get update
sudo apt-get install cmake libopenblas-dev liblapack-dev
pip install face-recognition
```

**macOS**:
```bash
brew install cmake
pip install face-recognition
```

### No Face Detected

- Ensure images contain clear, front-facing faces
- Check image quality and lighting
- Try different images

### ML Service Not Working

- Check logs: `logs/rescue_vision.log`
- Verify `face-recognition` is installed: `python -c "import face_recognition; print('OK')"`
- Adjust similarity threshold in `settings.py` if needed

## Next Steps

- Read full documentation in `README.md`
- Review API endpoints in `README.md`
- Check Raspberry Pi client in `clients/` directory
- Customize UI in `templates/` directory
