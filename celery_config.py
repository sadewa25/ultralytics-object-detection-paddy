from celery import Celery
from time import sleep
# ultralytics
import ultralytics
from ultralytics import YOLO

import cv2

celery_app = Celery(
    'worker',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

@celery_app.task
def hello(info: str):
    sleep(30)
    return f'hello world: {info}'

@celery_app.task
def track_video(location: str, unique_filename: str):
    # Initialize the model (assuming you have a model variable)
    model = YOLO('best.onnx', task='detect')

    # Open the video source
    cap = cv2.VideoCapture(location)

    # Get video properties
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    # Define the codec and create VideoWriter object
    out = cv2.VideoWriter(f'results/{unique_filename}.avi', cv2.VideoWriter_fourcc(*'XVID'), fps, (frame_width, frame_height))

    # Run inference with stream=True
    results = model(source=location, stream=True)  # generator of Results objects

    # Process the results and save the bounding boxes to the video
    for r in results:
        ret, frame = cap.read()
        if not ret:
            break
        
        boxes = r.boxes  # Boxes object for bbox outputs
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            class_id = int(box.cls[0])  # Class ID
            class_name = model.names[class_id]  # Get class name from model
            confidence = box.conf[0]  # Confidence score
            label = f'{class_name} {confidence:.2f}'  # Label with class name and confidence score
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)  # Draw bounding box
            cv2.putText(frame, str(label), (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)  # Draw class name
        
        out.write(frame)  # Write the frame with bounding boxes to the video

    # Release everything if job is finished
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    return {"file_path": f'results/{unique_filename}.avi'}