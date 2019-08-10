import io
import os
from flask import Flask
import numpy as np
import cv2
from werkzeug import secure_filename

from flask import render_template, request
from entity_extraction import get_relations
from ocr import ocr_core

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

@app.route('/')
def index() -> str:
    return render_template('form.html')

@app.route('/process-file', methods=['POST'])
def process_file() -> str:
    string = request.files['file'].stream.read().decode('utf-8')
    relations = get_relations(string, string.split("\n"))
    return render_template('output.html', string="\n".join([" - ".join(r) for r in relations]))

@app.route('/process-image', methods=['POST'])
def process_image() -> str:
    image = request.files['photo']
    if image:
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    text = ocr_core(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return render_template('output.html', string=text)
