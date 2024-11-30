from celery import Celery
from time import sleep
# ultralytics
from ultralytics import YOLO
import tensorflow as tf
import numpy as np
from PIL import Image

import cv2

celery_app = Celery(
    'worker',
    # broker='redis://localhost:6379/0',
    # backend='redis://localhost:6379/0'
    broker='redis://localhost:6380/0',
    backend='redis://localhost:6380/0'
)

@celery_app.task
def hello(info: str):
    sleep(30)
    return f'hello world: {info}'

@celery_app.task
def track_img(location: str):
    img = Image.open(location)
    img = img.convert("L")
    img = img.resize((224, 224), Image.Resampling.NEAREST)
    img_array = np.asarray(img)
    XTest = np.expand_dims(img_array, axis=0)  # Add batch dimension
    XTest = np.expand_dims(XTest, axis=-1) 

    res = []
    if len(XTest.shape) == 4:
        interpreter = tf.lite.Interpreter(model_path="modelVgg.tflite")
        interpreter.allocate_tensors()

        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        input_data = np.array(XTest, dtype=np.float32)
        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()
        output_data = interpreter.get_tensor(output_details[0]['index'])

        index_of_max_value = np.argmax(output_data)

        # Define the labels
        name_label = [
            'Hama Kutu Putih', 
            'Hama Wereng', 
            'Hama Weleng Sangit', 
            'Hama Penggerek Batang', 
            'Hama Tikus', 
            'Hama Burung', 
            'Hawar Daun', 
            'Leaf Blast',
            'Brown Leaf Spot', 
            'Striped Leaf', 
            'Tungro'
        ]

        # Get the label corresponding to the maximum value
        predicted_label = name_label[index_of_max_value]
        res = predicted_label
    else:
        res = "Terjadi Kesalahan Gambar"

    return {"file_path": f'{res}'}

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