from flask import Flask, request, render_template, jsonify, make_response
from flask.json import load
from flasgger import Swagger
from scrubber import deidentify

import json

app = Flask(__name__)
swagger = Swagger(app)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/demo')
def demo():
    with open('static/txt/identified_demo.txt') as f:
        text = f.read()

    with open('static/txt/deidentified_demo.txt') as f:
        scrubbed = f.read()

    return render_template('home.html', text=text, scrubbed=scrubbed)


@app.route('/api/scrub', methods=['POST'])
def scrub():
    """Removes personal information from free text
    ---
    parameters:
      - name: input_text
        in: query
        type: string
        required: true
    """

    data = request.get_json()
    text = data['text']
    document = deidentify(text)

    return jsonify(document=document)


if __name__ == '__main__':
    
    app.run(host='0.0.0.0', port='5000')
