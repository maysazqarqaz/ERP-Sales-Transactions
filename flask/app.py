import pickle
import numpy as np
from flask import Flask,request,jsonify
from Project.flask.utils import *

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <!doctype html>
    <html>
        <head>
            <title>ERP Sales Transactions</title>
        </head>
        <body>
            <h1>ERP Sales Transactions</h1>
            <form action="/generate_sql_query" method="get">
                <label for="question">Enter your question:</label><br>
                <input type="text" id="question" name="question" required><br><br>
                <button type="submit">Generate SQL Query</button>
            </form>
            <br>
            <form action="/answer_question" method="get">
                <label for="question">Enter your question:</label><br>
                <input type="text" id="question" name="question" required><br><br>
                <button type="submit">Answer Question</button>
            </form>
        </body>
    </html>
    '''

with open('linear_regression_pipeline.pkl', 'rb') as f:
    reg_pipeline = pickle.load(f)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    features = np.array(data['features']).reshape(1, -1)
    prediction = reg_pipeline.predict(features)
    return jsonify({'prediction': prediction.tolist()})

@app.route('/generate_sql_query', methods=['GET'])
def sql_query():
    question = request.args.get('question')
    query = generate_sql_query(question,tables_info)
    return jsonify({"query":query})

@app.route('/answer_question', methods=['GET'])
def answer_question():
    question = request.args.get('question')
    answer = answer_question_flow(question)

    return jsonify({'answer':answer})

if __name__ == '__main__':    
    app.run()