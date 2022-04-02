import os.path
import uuid
from flask import Flask, request, jsonify

from GeneratorThread import *

UPLOAD_FOLDER = 'storage/uploads'
GENERATE_FOLDER = 'storage/generated'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
threadsPool = []

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['GENERATE_FOLDER'] = GENERATE_FOLDER

@app.route('/upload-image', methods=['POST'])
def upload_image():
    uploadedImage = request.files['image']
    if uploadedImage is None:
        return 'there is no image in form!'
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.mkdir(app.config['UPLOAD_FOLDER'])
    
    pid = str(uuid.uuid4())
    uploadedImage.filename = f'{pid}.png'
    path = os.path.join(app.config['UPLOAD_FOLDER'], uploadedImage.filename)
    uploadedImage.save(path)

    th = GeneratorThread(pid)
    threadsPool.append(th)
    th.start()
    
    return jsonify(pid=pid)

@app.route('/images/preview', methods=['GET'])
def images_preview():
    dir = os.scandir(app.config['UPLOAD_FOLDER'])
    result = []

    for file in dir:
        if not file.is_file() or file.name == '.gitkeep':
            continue
        uid = os.path.splitext(file.name)[0]
        result.append({
            "image": f'img/uploads/{uid}',
            "id": uid
        })

    return jsonify(result)

@app.route('/images/<string:uuid>', methods=['GET'])
def images_get(uuid):
    dir = os.scandir(os.path.join(app.config['GENERATE_FOLDER'], uuid))
    result = []

    for file in dir:
        if not file.is_file():
            continue
        fileName = os.path.splitext(file.name)[0]
        result.append(int(fileName))

    result = sorted(result)

    return jsonify(list(map(lambda name: f'img/generated/{uuid}/{name}', result)))
