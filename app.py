from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import numpy as np
from sqlalchemy.dialects.postgresql import ARRAY
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from torch import from_numpy
from numpy.linalg import norm
from openai import OpenAI
from pre_processing import pre_process_text
from post_processing import post_process_text
from flask import Flask, request, jsonify, session

client = OpenAI(
    api_key='sk-proj-AAAA'
)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost:5432/postgres'
db = SQLAlchemy(app)
model = SentenceTransformer('all-MiniLM-L6-v2')

class DataVector(db.Model):
    __tablename__ = 'datavector'
    id = db.Column(db.Integer, primary_key=True)
    vector = db.Column(ARRAY(db.Float), nullable=False)
    text = db.Column(db.Text, nullable=False)

    def __init__(self, vector, text):
        self.vector = vector
        self.text = text

def chunk_text(text, chunk_size, overlap_size):
    """
    Splits text into chunks with overlap.

    Parameters:
    text (str): The text to be chunked.
    chunk_size (int): The size of each chunk.
    overlap_size (int): The size of the overlap between chunks.

    Returns:
    list: A list of text chunks.
    """
    chunks = []
    i = 0
    while i < len(text):
        chunk = text[i:i + chunk_size]
        chunks.append(chunk)
        i += chunk_size - overlap_size

    return chunks


# Define a route to handle POST requests for adding text data and embedding into vectors
@app.route('/insert_and_embed', methods=['POST'])
def insert_and_embed():
    if not request.json or 'text' not in request.json:
        return jsonify({'error': 'Bad request'}), 400
    
    text = request.json['text']    
    segments = chunk_text(text, 200, 40)

    segment_vectors = [model.encode(segment.strip()).tolist() for segment in segments]
    
    for i, segment in enumerate(segments):
        emotion_analyst = pre_process_text(segment, True)
        new_vector = DataVector(text=segment.strip(), vector=segment_vectors[i])
        db.session.add(new_vector)
    
    db.session.commit()
    return jsonify({'status': 'Success'}), 201

# Define a route to handle POST requests for querying similar vectors
@app.route('/query_similar', methods=['POST'])
def query_similar():
    if not request.json or 'text' not in request.json:
        return jsonify({'error': 'Bad request'}), 400
    
    context = session.get('default_session')
    query_text = request.json['text']
    query_text = pre_process_text(query_text)
    query_vector = model.encode(query_text).reshape(1, -1)  # Reshape to match expected input for cosine_similarity
    
    # Retrieve all vectors from the database
    vectors = DataVector.query.all()
    if not vectors:
        return jsonify({'error': 'No vectors found in the database'}), 404
    
    # Extract vectors and ids
    vector_list = [np.array(v.vector).reshape(1, -1) for v in vectors]
    
    # Calculate cosine similarities
    similarities = [cosine_similarity(query_vector, v)[0][0] for v in vector_list]

    # Find index of highest similarity
    top_n_indices = np.argsort(similarities)[-5:][::-1]
    
    # Return the text and similarity score of the most similar vector

    top_n_results = [{'text': vectors[idx].text, 'similarity_score': similarities[idx]} for idx in top_n_indices]
    top_n_indices_str = ', '.join(map(str, top_n_results))
    
    prompt = f"""You are mata or Duc. Write a response in a personal style using singular first-person pronouns only,
    question: {query_text}
    top k results: {top_n_indices_str}
    coversation history: {context}"""

    response = post_process_text(prompt)
    
    return jsonify({'results': response}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(debug=True)
