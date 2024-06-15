from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import numpy as np
from sqlalchemy.dialects.postgresql import ARRAY
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from torch import from_numpy
from numpy.linalg import norm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost:5432/postgres'
db = SQLAlchemy(app)

model = SentenceTransformer('all-MiniLM-L6-v2')

class DataVector(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vector = db.Column(ARRAY(db.Float), nullable=False)
    text = db.Column(db.String(255), nullable=False)

    def __init__(self, vector, text):
        self.vector = vector
        self.text = text

# Define a route to handle POST requests for adding text data and embedding into vectors
@app.route('/insert_and_embed', methods=['POST'])
def insert_and_embed():
    if not request.json or 'text' not in request.json:
        return jsonify({'error': 'Bad request'}), 400
    
    text = request.json['text']
    vector = model.encode(text).tolist()
    new_vector = DataVector(text=text, vector=vector)
    db.session.add(new_vector)
    db.session.commit()
    return jsonify({'id': new_vector.id}), 201

# Define a route to handle POST requests for querying similar vectors
@app.route('/query_similar', methods=['POST'])
def query_similar():
    if not request.json or 'text' not in request.json:
        return jsonify({'error': 'Bad request'}), 400
    
    query_text = request.json['text']
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
    most_similar_idx = np.argmax(similarities)
    
    # Return the text and similarity score of the most similar vector
    most_similar_text = vectors[most_similar_idx].text
    similarity_score = similarities[most_similar_idx]
    
    return jsonify({'most_similar_text': most_similar_text, 'similarity_score': similarity_score}), 200

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
