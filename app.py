from fastapi import FastAPI
import boto3

app = FastAPI()

@app.get("/s3/files/titles")
async def get_s3_files_titles(bucket_name: str):
    try:
        # Initialize S3 client
        s3 = boto3.client('s3')
        
        # List objects in the specified bucket
        response = s3.list_objects_v2(Bucket=bucket_name)
        
        # Check if objects were found in the bucket
        if 'Contents' in response:
            # Extract the titles from the file names (remove file extension)
            file_titles = [obj['Key'].split('/')[-1].split('.')[0] for obj in response['Contents']]
            return {"titles": file_titles}
        else:
            return {"message": "No objects found in the bucket."}
    except Exception as e:
        return {"error": f"Error accessing bucket {bucket_name}: {e}"}
