from flask import Flask, flash, request, redirect, url_for, render_template
import os
from werkzeug.utils import secure_filename
import cv2
import numpy as np
from ultralytics import YOLO

from flask import jsonify
UPLOAD_FOLDER = 'static/uploads/'
app = Flask(__name__)
app.secret_key = 'your_secret_key4242'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@app.route('/')
def upload_form():
    return render_template('upload.html')
@app.route('/', methods=['POST'])


def upload_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    else:
        flash('Allowed image types are -> png, jpg, jpeg, gif')
        return redirect(request.url)
    img = cv2.imread(file_path)
    #cv2.imshow("Uploaded Image", img)
    #cv2.waitKey(0)
    bbox_path = detect_license_plate(file_path, filename)
    #return render_template('upload.html', filenames=filename)
    print(bbox_path)
    if(bbox_path==0):
        flash("Anh khong co chua bien so !")
        return  redirect(request.url)
    return render_template('upload.html', filenames=bbox_path)

# Dung yolo phat hien vung bien so
@app.route('/detect_license_plate/<file_path>')
def detect_license_plate(file_path, filename):
    model = YOLO("runs/detect/train2/weights/best.pt")
    results = model(file_path)
    if results:
        for result in results:
            boxes = result.cpu().boxes.numpy()
            for box in boxes:
                box = boxes.xyxy
                x_min = box[0, 0]
                y_min = box[0, 1]
                x_max = box[0, 2]
                y_max = box[0, 3]

                # Đọc ảnh gốc
                image = cv2.imread(file_path)

                # Chuyển đổi tọa độ thành số nguyên
                x_min, y_min, x_max, y_max = map(int, [x_min, y_min, x_max, y_max])

                # Vẽ bounding box lên ảnh gốc
                cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)

                # Tạo tên cho ảnh đã vẽ bounding box
                bbox_filename = 'bbox_' + filename
                # Lưu ảnh đã vẽ bounding box
                cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'], 'bbox_' + filename), image)

                return bbox_filename

    # Trả về 0 nếu không có bounding box nào được phát hiện
    return 0
@app.route('/display/<bbox_path>')
def display_image(bbox_path):
    print(bbox_path)
    return redirect(url_for('static', filename='uploads/' + bbox_path), code=301)
if __name__ == "__main__":
    app.run()