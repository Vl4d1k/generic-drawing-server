import uuid
from flask import Flask, request, jsonify

from GeneratorThread import *

UPLOAD_FOLDER = 'storage/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
threadsPool = []

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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

@app.route("/")
def hello():
    return "<h1 style='color:blue'>Hello There!</h1>"

if __name__ == "__main__":
    app.run(host='0.0.0.0')
