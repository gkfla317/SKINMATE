# app.py

import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import tensorflow as tf
import numpy as np
from PIL import Image

# --- Flask 애플리케이션 설정 ---
app = Flask(__name__)

# 업로드 폴더 및 허용 확장자 설정
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'supersecretkey' # 세션 관리를 위한 시크릿 키

# 모델 경로
MODEL_PATH = "filename.tflite"

# --- 모델 분석 함수 (0808-test1.py 기반) ---
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
        input_data = np.array(img, dtype=np.float32)
        input_data = input_data / 255.0
        input_data = np.expand_dims(input_data, axis=0)

        if input_type == np.uint8:
            input_data = np.array(np.expand_dims(img, axis=0), dtype=np.uint8)

    except Exception as e:
        print(f"이미지 처리 오류: {e}")
        return None

    try:
        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()
        output_data = interpreter.get_tensor(output_details[0]['index'])
    except Exception as e:
        print(f"모델 추론 오류: {e}")
        return None

    # 모델 출력(1.0 ~ 4.0)을 100점 만점으로 변환
    raw_score = output_data[0][0]
    final_score = ((raw_score - 1.0) / 3.0) * 100
    final_score = max(0, min(100, final_score))
    
    return final_score

# 허용된 파일 확장자인지 확인하는 함수
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- 웹페이지 라우팅 ---

# 1. 메인 페이지
@app.route('/')
def index():
    return render_template('index.html')

# 2. 분석 페이지 (GET 요청 시)
@app.route('/analysis')
def analysis():
    return render_template('analysis.html')

# 3. 분석 실행 (POST 요청 시)
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

        # 모델로 점수 분석
        score = get_elasticity_score(MODEL_PATH, filepath)

        if score is None:
            flash('피부 탄력 점수를 분석하는 데 실패했습니다.')
            return redirect(url_for('analysis'))

        # 분석 후 업로드된 파일의 경로를 static으로 전달하기 위함
        # (보안상 uploads 폴더는 직접 접근하지 않는 것이 좋음)
        # 여기서는 간단하게 구현하기 위해 임시 URL을 만듭니다.
        uploaded_image_url = url_for('static', filename=f'uploads_temp/{filename}')
        # 임시로 파일을 static 폴더에 복사
        if not os.path.exists('static/uploads_temp'):
            os.makedirs('static/uploads_temp')
        os.replace(filepath, f'static/uploads_temp/{filename}')

        # 결과 페이지(result.html)로 점수와 이미지 경로를 전달합니다.
        return render_template('result.html', score=score, uploaded_image=uploaded_image_url)
    else:
        flash('허용되지 않는 파일 형식입니다. (png, jpg, jpeg, gif)')
        return redirect(url_for('analysis'))

# 4. 추천 상품 페이지
@app.route('/recommendations')
def recommendations():
    return render_template('recommendations.html')

# --- 서버 실행 ---
if __name__ == '__main__':
    # uploads 폴더가 없으면 생성
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
