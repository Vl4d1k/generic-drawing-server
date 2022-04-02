import os
import uuid
from flask import Flask, request, jsonify

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/upload-image', methods=['POST'])
def upload_image():
    print(request.files)
    uploadedImage = request.files['image']
    if uploadedImage is None:
        return 'there is no image in form!'
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.mkdir(app.config['UPLOAD_FOLDER'])
    
    pid = uuid.uuid4()
    uploadedImage.filename = pid
    path = os.path.join(app.config['UPLOAD_FOLDER'], uploadedImage.filename)
    uploadedImage.save(path)
    
    return jsonify(pid=pid)
