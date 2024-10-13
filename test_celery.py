from tasks import add

if __name__ == "__main__":
    # Enqueue the task
    result = add.delay(4, 6)
    
    # Wait for the result
    print("Task enqueued, waiting for result...")
    result_value = result.get(timeout=10)
    
    # Print the result
    print(f"Task result: {result_value}")