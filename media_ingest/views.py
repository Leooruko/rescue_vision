"""
Views for media_ingest app.
"""
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.conf import settings
from .models import Frame
from .serializers import FrameSerializer, FrameIngestSerializer
from ml_service.services import MLService
from cases.models import MissingPerson
from notifications.models import Notification
import logging

logger = logging.getLogger('ml_service')


@api_view(['GET'])
@permission_classes([permissions.AllowAny])  # Allow Raspberry Pi to check readiness
def ready_view(request):
    """
    Check if backend is ready to receive frames.
    Raspberry Pi should poll this endpoint before sending frames.
    """
    # Check if we have active cases
    active_cases_count = MissingPerson.objects.filter(status='ACTIVE').count()
    
    # Check if we're at capacity
    max_cases = settings.ML_SERVICE_CONFIG.get('MAX_ACTIVE_CASES', 20)
    
    is_ready = active_cases_count > 0 and active_cases_count <= max_cases
    
    return Response({
        'ready': is_ready,
        'active_cases': active_cases_count,
        'max_cases': max_cases
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])  # Allow Raspberry Pi to send frames
def ingest_view(request):
    """
    Ingest a frame from Raspberry Pi.
    This endpoint processes frames asynchronously.
    """
    serializer = FrameIngestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    # Create frame instance
    frame = serializer.save()
    
    # Process frame asynchronously (in production, use Celery)
    # For now, process in background thread
    import threading
    thread = threading.Thread(
        target=process_frame_async,
        args=(frame.id,),
        daemon=True
    )
    thread.start()
    
    return Response({
        'frame_id': frame.id,
        'message': 'Frame received and queued for processing'
    }, status=status.HTTP_202_ACCEPTED)


def process_frame_async(frame_id):
    """
    Process frame asynchronously.
    Detect faces and match against missing persons using OpenCV.
    """
    try:
        frame = Frame.objects.get(id=frame_id)
        
        # Initialize ML service
        ml_service = MLService()
        
        # Match faces in frame against stored missing person faces
        # Uses OpenCV-based face detection and histogram comparison
        matched_case = ml_service.match_face_from_image(frame.image.path)
        
        if matched_case:
            # Update frame with match
            frame.matched_case_id = str(matched_case.id)
            frame.processed = True
            frame.save()
            
            # Create notification
            Notification.objects.create(
                user=matched_case.reporter,
                missing_person=matched_case,
                message=f"Potential match detected for {matched_case.name}",
                matched_image=frame.image,
                detection_timestamp=frame.timestamp
            )
            
            logger.info(f"Match detected: Frame {frame_id} matched with case {matched_case.id}")
        else:
            frame.processed = True
            frame.save()
            logger.debug(f"No match found for frame {frame_id}")
    
    except Exception as e:
        logger.error(f"Error processing frame {frame_id}: {str(e)}")
        try:
            frame = Frame.objects.get(id=frame_id)
            frame.processed = True
            frame.save()
        except:
            pass
