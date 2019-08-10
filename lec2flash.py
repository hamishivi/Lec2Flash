from flask import Flask
app = Flask(__name__)

@app.route('/')
def index() -> str:
    return "Welcome to Lec2Flash"

@app.route('/process-file', method=['POST'])
def process_file():
    pass
