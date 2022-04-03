import os.path
import uuid
from flask import Flask, request, jsonify, send_file
import shelve
from PIL import Image
from pygifsicle import optimize

from GeneratorThread import *

db = shelve.open('db')

UPLOAD_FOLDER = 'storage/uploads'
GENERATE_FOLDER = 'storage/generated'
GIF_FOLDER = 'storage/gif'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
threadsPool = []

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['GENERATE_FOLDER'] = GENERATE_FOLDER
app.config['GIF_FOLDER'] = GIF_FOLDER

@app.route('/img/generated/<string:upload_img_uuid>/<int:img_id>', methods=['GET'])
def get_image(upload_img_uuid, img_id):
    img_path = f'storage/generated/{upload_img_uuid}/{img_id}.png'
    return send_file(img_path, mimetype='image/jpg')

@app.route('/img/uploads/<string:upload_img_uuid>', methods=['GET'])
def get_image_(upload_img_uuid):
    img_path = f'storage/uploads/{upload_img_uuid}.png'
    return send_file(img_path, mimetype='image/jpg')

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

    db[pid] = request.form['title']

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
            "id": uid,
            "title": db.get(uid)
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

    result = result[0: len(result): 10]

    return jsonify({
        "title": db[uuid],
        "images": list(map(lambda name: f'img/generated/{uuid}/{name}', result))
    })

@app.route('/gif/<string:uuid>', methods=['GET'])
def gif_get(uuid):
    path = f"{app.config['GIF_FOLDER']}/{uuid}.gif"
    dir = os.scandir(os.path.join(app.config["GENERATE_FOLDER"], uuid))
    frames = []

    if os.path.exists(path):
        return path

    for file in dir:
        if not file.is_file():
            continue
        fileName = os.path.splitext(file.name)[0]
        frames.append(int(fileName))

    frames = sorted(frames)
    frames = list(map(lambda name: Image.open(f'{app.config["GENERATE_FOLDER"]}/{uuid}/{name}.png'), frames))

    frames[0].save(
        path,
        save_all=True,
        append_images=frames[1:],
        optimize=True,
        duration=100,
        loop=1,
        quality=5
    )

    optimize(path)

    return path

@app.route("/")
def hello():
    return "<h1 style='color:blue'>Hello There!</h1>"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
