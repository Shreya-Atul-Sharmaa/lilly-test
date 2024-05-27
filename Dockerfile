FROM python:3.8

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY generate_and_store_vectors.py .

CMD ["python", "generate_and_store_vectors.py"]

