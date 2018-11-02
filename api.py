from flask import Flask, request, render_template, jsonify
from flask.json import load
from flask_restful import Resource, Api
from flasgger import Swagger
from scrubber import deidentify

import json


app = Flask(__name__)
api = Api(app)
api.add_resource(Scrubber, '/api/scrub')
swagger = Swagger(app)

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


class Scrubber(Resource):
    """Removes personal information from free text
    ---
    parameters:
      - name: input_text
        in: query
        type: string
        required: true
    """

    def post(self):
        data = request.get_json()
        text = data['text']
        scrubbed = deidentify(text)

        return jsonify(text=text, scrubbed=scrubbed)

if __name__ == '__main__':

    app.run(host='0.0.0.0', port='5000')
