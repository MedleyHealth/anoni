from flask import Flask, request, render_template, jsonify
from flask.json import load
from flask_restful import Resource, API
from flasgger import Swagger
from scrubber import deidentify

import json


app = Flask(__name__)
api = Api(app)
swagger = Swagger(app)

@app.route('/', methods=['GET', 'POST'])
def home():

    text = ''
    di = ''

    if request.method == 'POST':
        text = request.form['input_text']
        data = scrub(text)
        return jsonify(text=data['text'], scrubbed=data['scrubbed'])

    return render_template('homepage.html', text=text, scrubbed=di)


@app.route('/api/scrubbers', methods=['POST'])
def scrub():
    """Removes personal information from free text
    ---
    parameters:
      - name: input_text
        in: query
        type: string
        required: true
    """

    text = request.form['input_text']
    di = deidentify(text)

    return jsonify(text=text, scrubbed=di)

if __name__ == '__main__':

    app.run(host='0.0.0.0', port='5000')
