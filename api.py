from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from celery_config import celery_app, track_video
import uuid
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/results", StaticFiles(directory="results"), name="results")

# Configure CORS
origins = [
    "*"
    # Add other origins as needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "/root/ultralytics/ultralytics-object-detection-paddy/files"
# UPLOAD_DIR = "/Users/sadewawicak/Project/JagoPadi/ultralytics-object-detection-paddy/files"

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_location = os.path.join(UPLOAD_DIR, unique_filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    task = track_video.delay(file_location, unique_filename)
    # task = add.delay(4, 6)
    
    # return {"token": task.id}
    return {"token": task.id, "filename": unique_filename}


@app.get("/result/{task_id}")
async def get_result(task_id: str):
    task_result = celery_app.AsyncResult(task_id)
    if task_result.state == 'PENDING':
        return {"task_id": task_id, "status": task_result.state, "result": None}
    elif task_result.state != 'FAILURE':
        return {"task_id": task_id, "status": task_result.state, "result": task_result.result}
    else:
        # something went wrong in the background job
        return {"task_id": task_id, "status": task_result.state, "result": str(task_result.info)}

# To run the FastAPI app, use the command: uvicorn api:app --reload --host 0.0.0.0
# celery -A celery_config.celery_app flower
# celery -A celery_config.celery_app worker --loglevel=info
# celery -A celery_config.celery_app worker --concurrency=1
# celery --broker=redis://localhost:6379/0 flower
# /////
# celery -A  celery_config.celery_app worker --loglevel=info --concurrency=1
# celery -A  celery_config.celery_app flower --host 0.0.0.0 --loglevel=info
# 192.168.1.20:8000/results/c29fac9b-e633-45e9-a942-5270615a3c6e_My Video.mp4.avi
# http://103.16.117.163:5555/tasks
# http://103.16.117.163:8000/results/80ca3475-0cd7-4f1f-81fd-17375e511b1e_My%20Video.mp4.avi
# track-uvicorn.service