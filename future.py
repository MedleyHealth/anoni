from flask_restful import Resource, Api

api = Api(app)

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

    api.add_resource(Scrubber, '/api/scrub')
