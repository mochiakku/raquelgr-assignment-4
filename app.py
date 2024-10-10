from flask import Flask, render_template, request, jsonify
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords', quiet=True)

app = Flask(__name__)

newsgroups = fetch_20newsgroups(subset='all')
stop_words = list(set(stopwords.words('english'))) 
vectorizer = TfidfVectorizer(stop_words=stop_words)
X = vectorizer.fit_transform(newsgroups.data)

n_components = 100
lsa = TruncatedSVD(n_components=n_components, random_state=42)
X_lsa = lsa.fit_transform(X)

def search_engine(query):
    """
    Function to search for top 5 similar documents given a query
    Input: query (str)
    Output: documents (list), similarities (list), indices (list)
    """
    query_vec = vectorizer.transform([query])
    query_lsa = lsa.transform(query_vec)
    
    similarities = cosine_similarity(query_lsa, X_lsa).flatten()
    top_indices = similarities.argsort()[-5:][::-1]
    
    documents = [newsgroups.data[i] for i in top_indices]
    top_similarities = similarities[top_indices]
    
    return documents, top_similarities.tolist(), top_indices.tolist()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    documents, similarities, indices = search_engine(query)
    return jsonify({'documents': documents, 'similarities': similarities, 'indices': indices}) 

if __name__ == '__main__':
    app.run(debug=True)