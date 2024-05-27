import random
from elasticsearch import Elasticsearch



# Define your OpenSearch endpoint
OPENSEARCH_ENDPOINT = "YOUR_OPENSEARCH_ENDPOINT"
# Define your OpenSearch index
INDEX_NAME = "vectors"



# Connect to OpenSearch
es = Elasticsearch([OPENSEARCH_ENDPOINT])



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
    num_vectors = 10  # Number of vectors to generate
    dim = 10  # Dimensionality of each vector
    store_vectors(num_vectors, dim)
    print(f"{num_vectors} random vectors stored in OpenSearch.")
