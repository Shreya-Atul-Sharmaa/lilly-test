import os
import random
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

# Define your OpenSearch endpoint
OPENSEARCH_ENDPOINT = "https://search-opensearch-for-vectors-poc-5fqfu5hcbglmswud5kcngko4ae.us-east-1.es.amazonaws.com"
# Define your OpenSearch index
INDEX_NAME = "vectors"

# AWS
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
REGION = os.getenv('AWS_REGION')

awsauth = AWS4Auth(AWS_ACCESS_KEY, AWS_SECRET_KEY, REGION, 'es')

# Connect to OpenSearch
es = Elasticsearch(
    hosts=[{'host': OPENSEARCH_ENDPOINT, 'port': 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)

# Function to generate random vectors
def generate_random_vector(dim):
    return [random.random() for _ in range(dim)]

# Function to store vectors in OpenSearch
def store_vectors(num_vectors, dim):
    for i in range(num_vectors):
        vector = generate_random_vector(dim)
        doc = {"vector": vector}
        es.index(index=INDEX_NAME, body=doc)

# Example usage
if __name__ == "__main__":
    num_vectors = 10  # Number of vectors to generate
    dim = 10  # Dimensionality of each vector
    store_vectors(num_vectors, dim)
    print(f"{num_vectors} random vectors stored in OpenSearch.")
