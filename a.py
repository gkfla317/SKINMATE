import os
import cv2
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import tensorflow as tf
import numpy as np
from PIL import Image

# --- Flask 애플리케이션 설정 ---
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'supersecretkey'

MODEL_PATH = "filename.tflite"

# ✅ 얼굴인지 판별하는 함수
def is_face_image(image_path):
    try:
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

        return len(faces) > 0
    except Exception as e:
        print(f"얼굴 감지 오류: {e}")
        return False

# --- 모델 분석 함수 ---
def get_elasticity_score(model_path, image_path):
    try:
        interpreter = tf.lite.Interpreter(model_path=model_path)
        interpreter.allocate_tensors()
    except Exception as e:
        print(f"모델 로드 실패: {e}")
        return None

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    try:
        _, height, width, _ = input_details[0]['shape']
        input_type = input_details[0]['dtype']
    except Exception as e:
        print(f"모델 입력 형태 확인 실패: {e}")
        return None

    try:
        img = Image.open(image_path).convert('RGB')
        img = img.resize((width, height))

        if input_type == np.uint8:
            input_data = np.expand_dims(np.array(img, dtype=np.uint8), axis=0)
        else:
            input_data = np.array(img, dtype=np.float32) / 255.0
            input_data = np.expand_dims(input_data, axis=0)

    except Exception as e:
        print(f"이미지 처리 오류: {e}")
        return None

    try:
        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()
        output_data = interpreter.get_tensor(output_details[0]['index'])

        print(f"모델 원본 출력 값: {output_data}")
        predicted_class = int(np.argmax(output_data[0]))

        class_to_score_map = {
            0: 1.0, 1: 1.5, 2: 2.0, 3: 2.5, 4: 3.0, 5: 3.5, 6: 4.0
        }
        final_score = class_to_score_map.get(predicted_class, 0.0)

        return final_score

    except Exception as e:
        print(f"모델 추론 오류: {e}")
        return None

# --- 파일 확장자 검사 함수 ---
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- 웹페이지 라우팅 ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analysis')
def analysis():
    return render_template('analysis.html')

@app.route('/analyze', methods=['POST'])
def analyze_image():
    if 'image' not in request.files:
        flash('파일이 없습니다.')
        return redirect(request.url)

    file = request.files['image']

    if file.filename == '':
        flash('선택된 파일이 없습니다.')
        return redirect(url_for('analysis'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # ✅ 얼굴이 없으면 예외 처리
        if not is_face_image(filepath):
            flash("얼굴이 인식되지 않습니다. 얼굴이 보이는 사진을 업로드해주세요.")
            os.remove(filepath)
            return redirect(url_for('analysis'))

        # 모델 분석
        score = get_elasticity_score(MODEL_PATH, filepath)
        if score is None:
            flash('피부 탄력 점수를 분석하는 데 실패했습니다.')
            return redirect(url_for('analysis'))

        uploaded_image_url = url_for('static', filename=f'uploads_temp/{filename}')
        if not os.path.exists('static/uploads_temp'):
            os.makedirs('static/uploads_temp')
        os.replace(filepath, f'static/uploads_temp/{filename}')

        return render_template('result.html', score=score, uploaded_image=uploaded_image_url)
    else:
        flash('허용되지 않는 파일 형식입니다. (png, jpg, jpeg, gif)')
        return redirect(url_for('analysis'))

@app.route('/recommendations')
def recommendations():
    return render_template('recommendations.html')

# --- 서버 실행 ---
if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
