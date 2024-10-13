from fastapi import FastAPI, File, UploadFile
import shutil
import os
from tasks import predict

app = FastAPI()

UPLOAD_DIR = "/root/ultralytics/ultralytics-object-detection-paddy/files"

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # task = predict.delay(file_location)
    task = add.delay(4, 6)
    return {"info": f"file '{file.filename}' saved at '{file_location}'"}

# To run the FastAPI app, use the command: uvicorn main:app --reload