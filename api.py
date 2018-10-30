from flask import Flask, request, render_template
from flasgger import Swagger

from scrubber import deidentify


app = Flask(__name__)
swagger = Swagger(app)

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/scrubbers', methods=['POST'])
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

    return render_template('home.html', text=text, scrubbed=di)

if __name__ == '__main__':

    app.run(host='0.0.0.0', port='5000')
