import asyncio
import os
import re
from docx import Document
from io import BytesIO
from langchain.docstore.document import Document as Langdoc
import boto3

# Initialize S3 client
s3 = boto3.client('s3')

chunkid = 1  # Global variable to track chunk number

# Function which only retains ascii characters
def filter_text(text):
    pattern = r'[^\x00-\x7F]+'
    filtered_text = re.sub(pattern, '', text)
    return filtered_text

# Function to chunk DOCX file contents
def chunk_docx_sections(doc_content):
    doc = Document(BytesIO(doc_content))
    chunks = []

    current_heading = ""
    current_subheading = ""
    current_chunk = []

    for paragraph in doc.paragraphs:
        style_name = paragraph.style.name
        text = ""
        for run in paragraph.runs:
            if "\n" in run.text:
                text += run.text.replace("\n", "\\n")
            else:
                text += run.text
        if style_name == 'Heading 1':
            if current_chunk:
                chunk_text = filter_text(" ".join(current_chunk))
                if current_heading:
                    if current_subheading:
                        chunks.append(f'{current_heading}:{current_subheading}:-{chunk_text}')
                    else:
                        chunks.append(f'{current_heading}:-{chunk_text}')
                else:
                    chunks.append(chunk_text)
                current_chunk = []
            current_heading = filter_text(text)

        elif style_name == 'Heading 2':
            if current_chunk:
                chunk_text = filter_text(" ".join(current_chunk))
                if current_heading:
                    if current_subheading:
                        chunks.append(f'{current_heading}:{current_subheading}:-{chunk_text}')
                    else:
                        chunks.append(f'{current_heading}:-{chunk_text}')
                else:
                    chunks.append(chunk_text)
                current_chunk = []

            current_subheading = filter_text(text)

        else:
            if current_heading or current_subheading:
                current_chunk.append(text)
            if '\n' in text:
                current_chunk.append('\n')

    if current_chunk:
        chunk_text = filter_text(" ".join(current_chunk))
        if current_heading:
            if current_subheading:
                chunks.append(f'{current_heading}:{current_subheading}:-{chunk_text}')
            else:
                chunks.append(f'{current_heading}:-{chunk_text}')
        elif current_subheading:
            chunks.append(f':{current_subheading}:-{chunk_text}')
        else:
            chunks.append(f'::{chunk_text}')
    return chunks

# Function to process a DOCX file content and create Langchain objects
async def process_docx_file(doc_content, file_title):
    global chunkid
    chunks = chunk_docx_sections(doc_content)
    langchain_objects = []
    for chunk in chunks:
        docobj = Langdoc(page_content=chunk, metadata={"filename": file_title, "filepath": None, "chunkid": chunkid})
        langchain_objects.append(docobj)
        chunkid += 1
    return langchain_objects

# Main function to process folder contents
async def process_folder(bucket_name):
    files_contents = {}
    response = s3.list_objects_v2(Bucket=bucket_name)
    for obj in response.get('Contents', []):
        object_key = obj['Key']
        response = s3.get_object(Bucket=bucket_name, Key=object_key)
        file_content = response['Body'].read()
        files_contents[object_key] = file_content

    tasks = []
    for file_title, file_content in files_contents.items():
        task = process_docx_file(file_content, file_title)
        tasks.append(task)
    langchain_objects = await asyncio.gather(*tasks)
    return [obj for sublist in langchain_objects for obj in sublist]

# Function to iterate through Langchain objects
def iterate_langchain_objects(langchain_objects):
    for obj in langchain_objects:
        print("File Title:", obj.metadata["filename"])
        print("Chunk ID:", obj.metadata["chunkid"])
        print("Page Content:", obj.page_content)
        print("\n")

# ASGI application entry point
async def app(scope, receive, send):
    # Extract the bucket name from the scope
    query_params = scope['query_string']
    bucket_name = query_params.decode().split('=')[-1]

    langchain_objects = await process_folder(bucket_name)
    iterate_langchain_objects(langchain_objects)

    await send({
        'type': 'http.response.start',
        'status': 200,
        'headers': [
            [b'content-type', b'text/plain'],
        ]
    })
    await send({
        'type': 'http.response.body',
        'body': b'Processing complete',
    })

# Entry point for uvicorn
async def main():
    await app({}, None, None)

# Example usage:
# asyncio.run(main())  # Uncomment this line if running locally

# Comment out the following line if running locally
# (uvicorn will handle calling `main` instead)
# asyncio.run(main())

