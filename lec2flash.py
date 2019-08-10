from flask import Flask

from flask import render_template, request

app = Flask(__name__)

@app.route('/')
def index() -> str:
    return render_template('form.html')

@app.route('/process-file', methods=['POST'])
def process_file() -> str:
    string = request.files['file'].stream.read().decode('utf-8')
    print(string)
    return render_template('output.html', string=string)
