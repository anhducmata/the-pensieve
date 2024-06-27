from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import numpy as np
from sqlalchemy.dialects.postgresql import ARRAY
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from torch import from_numpy
from numpy.linalg import norm
from openai import OpenAI

client = OpenAI(
    base_url='http://localhost:11434/v1',
    api_key='dolphin-llama3'
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

# Define a route to handle POST requests for adding text data and embedding into vectors
@app.route('/insert_and_embed', methods=['POST'])
def insert_and_embed():
    if not request.json or 'text' not in request.json:
        return jsonify({'error': 'Bad request'}), 400
    
    text = request.json['text']
    segments = text.split('.')
    segments = [segment for seg in segments for segment in seg.split(',') if segment]
    
    segment_vectors = [model.encode(segment.strip()).tolist() for segment in segments]
    
    for i, segment in enumerate(segments):
        new_vector = DataVector(text=segment.strip(), vector=segment_vectors[i])
        db.session.add(new_vector)
    
    db.session.commit()
    return jsonify({'status': 'Success'}), 201

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
    top_n_indices = np.argsort(similarities)[-2:][::-1]
    
    # Return the text and similarity score of the most similar vector
    top_n_results = [{'text': vectors[idx].text, 'similarity_score': similarities[idx]} for idx in top_n_indices]
    top_n_indices_str = ', '.join(map(str, top_n_results))
    prompt = f"SHORT ANWSER and When responding to user inquiries, please use first-person pronouns like I and me to create a more personal and conversational tone. Reference past conversations or information the user has shared to show continuity and understanding. Express empathy and emotion where appropriate. Avoid overly formal language and technical jargon. Here are some examples to follow: Example 1: Before: Based on the provided vector data, it seems that Guta Coffee is a popular choice. After: I noticed that Guta Coffee is a popular choice. I think it's a great spot for a daily caffeine fix! Example 2: Before: Your project has achieved a reduction in vulnerabilities, which is commendable. After: I saw that the project achieved a reduction in vulnerabilities. I think that is amazing!. This is vector data in text, please complete the sentence to the user, raw result: '{top_n_indices_str}'"
    checking_res = client.chat.completions.create(
        model='llama3',
        messages=[
            {"role": "system", "content": prompt},
        ]
    )
    return jsonify({'results': checking_res.choices[0].message.content}), 200

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
