from celery_config import celery_app
import os

@celery_app.task
def predict(file_path):
    # Add your prediction logic here
    # For example, load the model and make predictions
    # model = load_model()
    # result = model.predict(file_path)
    result = f"Predicted result for {file_path}"
    return result


@celery_app.task
def add(x, y):
    return x + y