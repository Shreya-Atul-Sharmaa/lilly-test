from flask import Flask, request, jsonify
import boto3

app = Flask(__name__)

@app.route('/list_bucket_objects', methods=['POST'])
def list_bucket_objects():
    # Initialize S3 client
    s3 = boto3.client('s3')

    # Extract the bucket name from the request
    bucket_name = request.json['bucket_name']

    try:
        # List objects in the specified bucket
        response = s3.list_objects_v2(Bucket=bucket_name)
    except Exception as e:
        return jsonify({
            'statusCode': 500,
            'body': f"Error accessing bucket {bucket_name}: {str(e)}"
        })

    # Check if objects were found in the bucket
    if 'Contents' in response:
        # Extract the titles from the file names (remove file extension)
        file_titles = [obj['Key'].split('/')[-1].split('.')[0] for obj in response['Contents']]
        return jsonify({
            'statusCode': 200,
            'body': file_titles
        })
    else:
        return jsonify({
            'statusCode': 200,
            'body': "No objects found in the bucket."
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
