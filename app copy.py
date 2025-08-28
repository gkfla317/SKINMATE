import os
import sys
import cv2
import sqlite3
import json
import shutil
import subprocess
import click
from flask import Flask, render_template, request, redirect, url_for, flash, session, g, jsonify
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

import base64
from google.cloud import aiplatform
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value

from datetime import datetime, timedelta

load_dotenv()


# TensorFlow 경고 메시지 숨기기
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# --- Vertex AI 설정 ---
PROJECT_ID = os.environ.get("PROJECT_ID")
ENDPOINT_ID = os.environ.get("ENDPOINT_ID")
REGION = os.environ.get("REGION")
CREDENTIALS_PATH = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

def predict_skin_type_from_vertex_ai(image_filepath):
    """Vertex AI 엔드포인트에 이미지 분류 예측을 요청하고 피부 타입 문자열을 반환합니다."""
    try:
        import google.oauth2.service_account

        credentials = google.oauth2.service_account.Credentials.from_service_account_file(CREDENTIALS_PATH)
        
        api_endpoint = f"{REGION}-aiplatform.googleapis.com"
        client_options = {"api_endpoint": api_endpoint}
        client = aiplatform.gapic.PredictionServiceClient(client_options=client_options, credentials=credentials)

        with open(image_filepath, "rb") as f:
            file_content = f.read()
        encoded_content = base64.b64encode(file_content).decode("utf-8")
        
        instance = json_format.ParseDict({"content": encoded_content}, Value())
        instances = [instance]
        
        endpoint_path = client.endpoint_path(
            project=PROJECT_ID, location=REGION, endpoint=ENDPOINT_ID
        )
        
        response = client.predict(endpoint=endpoint_path, instances=instances)
        
        if response.predictions:
            top_prediction = dict(response.predictions[0])
            display_names = top_prediction['displayNames']
            confidences = top_prediction['confidences']
            
            max_confidence = max(confidences)
            max_index = confidences.index(max_confidence)
            
            predicted_class = display_names[max_index]
            print(f"Vertex AI 예측 결과: {predicted_class} (신뢰도: {max_confidence:.2%})")
            return predicted_class
        else:
            print("Vertex AI 예측 결과를 받지 못했습니다.")
            return "알 수 없음" # Fallback
    except Exception as e:
        print(f"Vertex AI 예측 오류: {e}")
        return "알 수 없음" # Fallback


# --- Flask 애플리케이션 설정 ---
app = Flask(__name__)
app.config.from_mapping(
    SECRET_KEY='supersecretkey', # 세션 관리를 위한 비밀 키
    DATABASE=os.path.join(app.instance_path, 'skinmate.sqlite'),
    UPLOAD_FOLDER = 'uploads'
)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# --- 커스텀 템플릿 필터 ---
def fromjson(json_string):
    if json_string is None:
        return []
    return json.loads(json_string)

app.jinja_env.filters['fromjson'] = fromjson

def get_face_icon_for_score(score):
    if score is None:
        return 'default-face.png' # Or handle as appropriate
    score = float(score) # Ensure score is a float for comparison
    if 0 <= score <= 19:
        return 'face5.png'
    elif 20 <= score <= 49:
        return 'face4.png'
    elif 50 <= score <= 60:
        return 'face3.png'
    elif 61 <= score <= 90:
        return 'face2.png'
    elif 91 <= score <= 100:
        return 'face1.png'
    else:
        return 'default-face.png' # For scores outside 0-100 range

app.jinja_env.globals['get_face_icon'] = get_face_icon_for_score

# --- 데이터베이스 설정 및 헬퍼 함수 ---
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    with app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

app.teardown_appcontext(close_db)
app.cli.add_command(init_db_command)

# --- 얼굴 감지 및 파일 유효성 검사 함수 ---
def is_face_image(image_path):
    """이미지에 얼굴이 포함되어 있는지 확인합니다."""
    try:
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_alt2.xml")
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=8)
        return len(faces) > 0
    except Exception as e:
        print(f"얼굴 감지 오류: {e}")
        return False

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- 분석 로직 헬퍼 함수 (XGBoost 모델 사용) ---
def get_skin_scores(filepath):
    """Vertex AI API를 사용하여 피부 타입을 예측하고, 수분/주름/탄력은 임시 값을 반환합니다."""
    try:
        skin_type_from_api = predict_skin_type_from_vertex_ai(filepath)

      
        # 임시 점수 (API 개발 중이므로)
        scores = {
            'moisture': 50.0,
            'elasticity': 50.0,
            'wrinkle': 65.0,
            'skin_type': skin_type_from_api # 피부 타입은 API에서 직접 받은 문자열
        }
        return scores

    except Exception as e:
        print(f"피부 분석 중 예상치 못한 오류 발생: {e}")
        return {
            'moisture': 50.0,
            'elasticity': 50.0,
            'wrinkle': 65.0,
            'skin_type': '알 수 없음'
        }

def generate_recommendations(scores, username):
    """점수와 API에서 받은 피부 타입 문자열을 기반으로 피부 타입, 고민, 추천 문구를 생성합니다."""
    # scores 딕셔너리에서 skin_type을 직접 사용
    skin_type = scores.get('skin_type', '알 수 없음')

    # 기존 skin_type_score를 사용하던 로직은 제거

    concern_scores = {k: v for k, v in scores.items() if k != 'skin_type_score'}
    all_scores_korean = {
        '수분': concern_scores.get('moisture'),
        '탄력': concern_scores.get('elasticity'),
        '주름': concern_scores.get('wrinkle')
    }
    
    top_concerns_names = [name for name, score in all_scores_korean.items() if score <= 40]

    concern_icon_map = {
        '수분': 'water-icon.png',
        '탄력': 'elasticity-icon.png',
        '주름': 'wrinkle-icon.png'
    }
    
    concerns_for_template = [{'name': name, 'icon': concern_icon_map.get(name, 'default-icon.png')} for name in top_concerns_names]
    
    intro_message = ""
    if '수분' in top_concerns_names and '탄력' in top_concerns_names and '주름' in top_concerns_names:
        intro_message = "전반적인 피부 컨디션이 떨어져 있습니다."
    elif '수분' in top_concerns_names and '탄력' in top_concerns_names:
        intro_message = "피부 속 수분이 줄고 탄력이 떨어져 생기가 없어 보입니다."
    elif '수분' in top_concerns_names and '주름' in top_concerns_names:
        intro_message = "촉촉함이 사라지면서 잔주름이 더 도드라져 보입니다."
    elif '탄력' in top_concerns_names and '주름' in top_concerns_names:
        intro_message = "피부가 탄력을 잃고 주름이 점점 깊어지고 있습니다."
    elif '수분' in top_concerns_names:
        intro_message = "피부에 수분이 부족해 건조함이 느껴집니다."
    elif '탄력' in top_concerns_names:
        intro_message = "피부에 탄력이 떨어져 탄탄함이 부족합니다."
    elif '주름' in top_concerns_names:
        intro_message = "잔주름과 굵은 주름이 깊어지고 있습니다."

    product_recommendation = ""
    if '수분' in top_concerns_names and '탄력' in top_concerns_names and '주름' in top_concerns_names:
        product_recommendation = "종합적인 안티에이징 솔루션을 고려해보세요.<br>히알루론산과 글리세린의 수분 강화 성분과 펩타이드, 콜라겐의 탄력 강화 성분, 레티놀 또는 비타민 C 등의 주름 개선 성분이 포함된 제품을 조합해 꾸준히 관리해 주세요."
    elif '수분' in top_concerns_names and '탄력' in top_concerns_names:
        product_recommendation = "히알루론산과 글리세린으로 촉촉함을 보충하고, 펩타이드와 콜라겐이 함유된 탄력 강화 제품을 함께 사용해 보세요."
    elif '수분' in top_concerns_names and '주름' in top_concerns_names:
        product_recommendation = "수분 공급 성분인 히알루론산과 주름 개선에 효과적인 레티놀, 비타민 C가 포함된 제품으로 집중 관리하세요."
    elif '탄력' in top_concerns_names and '주름' in top_concerns_names:
        product_recommendation = "펩타이드와 콜라겐으로 탄력을 높이고, 레티놀과 토코페롤(비타민 E)이 들어간 제품으로 주름 완화와 피부 재생을 지원하세요."
    elif '수분' in top_concerns_names:
        product_recommendation = "히알루론산과 글리세린 같은 뛰어난 보습 성분이 포함된 제품으로 피부 깊숙이 수분을 채워주세요."
    elif '주름' in top_concerns_names:
        product_recommendation = "레티놀과 비타민 C가 들어간 주름 개선 제품으로 피부 재생을 돕고 생기 있는 피부로 관리하세요."
    elif '탄력' in top_concerns_names:
        product_recommendation = "펩타이드와 콜라겐 성분이 함유된 제품으로 피부 결을 단단하게 하고 건강한 탄력을 되찾아 보세요."

    if intro_message:
        recommendation_text = intro_message + "<br>" + product_recommendation
    else:
        recommendation_text = f"{username}님의 피부는 현재 특별한 관리가 필요하지 않은 좋은 상태입니다.<br>현재 루틴을 유지하세요<br>"

    return {'skin_type': skin_type, 'top_concerns_names': top_concerns_names, 'concerns_for_template': concerns_for_template, 'recommendation_text': recommendation_text}

def generate_result_summary(username, main_score, skin_type, top_concerns_names):
    """결과 페이지에 표시될 요약 텍스트를 생성합니다."""
    main_score_int = round(main_score)
    summary = f"{username}님, 오늘 피부 종합 점수는 {main_score_int}점입니다.<br>"
    if top_concerns_names:
        concerns_str = "', '".join(top_concerns_names)
        summary += f"진단 결과, 현재 피부는 '{skin_type}' 타입으로 판단되며, '{concerns_str}'에 대한 집중 케어가 필요합니다.<br>{username}님의 피부 고민을 해결해 줄 추천 제품을 확인해 보세요!"
    else:
        summary += f"현재 피부는 '{skin_type}' 타입이며, 전반적으로 균형 잡힌 건강한 피부 상태입니다.<br>피부 관리를 정말 잘하고 계시네요!<br>지금의 피부 컨디션을 유지하기 위해, 피부 장벽을 보호하고 수분과 영양을 적절히 공급해주는 제품을 꾸준히 사용하시는 것을 권장해드립니다."
    
    return summary

# --- 웹페이지 라우팅 ---
@app.route('/')
def index(): return render_template('index.html')

@app.route('/introduction')
def introduction(): return render_template('introduction.html')

@app.route('/analysis')
def analysis(): return render_template('analysis.html')

@app.route('/history')
def history():
    if 'user_id' not in session:
        flash('기록을 보려면 먼저 로그인해주세요.')
        return redirect(url_for('login'))

    db = get_db()
    all_analyses = db.execute(
        'SELECT * FROM analyses WHERE user_id = ? ORDER BY analysis_timestamp DESC',
        (session['user_id'],)
    ).fetchall()
    
    return render_template('history.html', analyses=all_analyses)

@app.route('/skin_diary')
def skin_diary():
    if 'user_id' not in session:
        flash('피부 일지를 보려면 먼저 로그인해주세요.')
        return redirect(url_for('login'))
    return render_template('skin_diary.html')

@app.route('/delete_analysis/<int:analysis_id>', methods=['POST'])
def delete_analysis(analysis_id):
    if 'user_id' not in session:
        flash('권한이 없습니다.', 'danger')
        return redirect(url_for('login'))

    db = get_db()
    analysis = db.execute(
        'SELECT * FROM analyses WHERE id = ? AND user_id = ?', (analysis_id, session['user_id'])
    ).fetchone()

    if analysis is None:
        flash('존재하지 않는 분석 기록입니다.', 'danger')
        return redirect(url_for('history'))

    db.execute('DELETE FROM analyses WHERE id = ?', (analysis_id,))
    db.commit()
    flash('분석 기록이 성공적으로 삭제되었습니다.', 'success')
    return redirect(url_for('history'))

@app.route('/delete_selected_analyses', methods=['POST'])
def delete_selected_analyses():
    if 'user_id' not in session:
        flash('권한이 없습니다.', 'danger')
        return redirect(url_for('login'))

    analysis_ids_to_delete = request.form.getlist('analysis_ids')
    if not analysis_ids_to_delete:
        flash('삭제할 기록을 선택해주세요.', 'info')
        return redirect(url_for('history'))

    db = get_db()
    placeholders = ','.join('?' for _ in analysis_ids_to_delete)
    query = f'DELETE FROM analyses WHERE id IN ({placeholders}) AND user_id = ?'
    
    params = analysis_ids_to_delete + [session['user_id']]
    db.execute(query, params)
    db.commit()
    
    flash('선택한 분석 기록이 성공적으로 삭제되었습니다.', 'success')
    return redirect(url_for('history'))

@app.route('/api/history')
def api_history():
    if 'user_id' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    try:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
    except (ValueError, TypeError):
        end_date = datetime.now().replace(hour=23, minute=59, second=59)

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
    except (ValueError, TypeError):
        start_date = end_date - timedelta(days=6)
        start_date = start_date.replace(hour=0, minute=0, second=0)

    if start_date > end_date:
        return jsonify({'error': 'Start date cannot be after end date.'}), 400

    db = get_db()
    analyses = db.execute(
        'SELECT analysis_timestamp, scores_json FROM analyses WHERE user_id = ? AND analysis_timestamp BETWEEN ? AND ? ORDER BY analysis_timestamp ASC',
        (session['user_id'], start_date, end_date)
    ).fetchall()

    daily_scores = {}
    current_date = start_date.date()
    while current_date <= end_date.date():
        date_key = current_date.strftime('%Y-%m-%d')
        daily_scores[date_key] = {'moisture': [], 'elasticity': [], 'wrinkle': []}
        current_date += timedelta(days=1)

    for analysis in analyses:
        analysis_date_key = analysis['analysis_timestamp'].strftime('%Y-%m-%d')
        if analysis_date_key in daily_scores:
            try:
                scores = json.loads(analysis['scores_json'])
                daily_scores[analysis_date_key]['moisture'].append(scores.get('moisture', 0))
                daily_scores[analysis_date_key]['elasticity'].append(scores.get('elasticity', 0))
                daily_scores[analysis_date_key]['wrinkle'].append(scores.get('wrinkle', 65.0))
            except (json.JSONDecodeError, TypeError):
                continue

    graph_dates = []
    graph_moisture = []
    graph_elasticity = []
    graph_wrinkle = []

    for date_key, scores_list in sorted(daily_scores.items()):
        graph_dates.append(datetime.strptime(date_key, '%Y-%m-%d').strftime('%m-%d'))
        graph_moisture.append(round(sum(scores_list['moisture']) / len(scores_list['moisture']), 1) if scores_list['moisture'] else 0)
        graph_elasticity.append(round(sum(scores_list['elasticity']) / len(scores_list['elasticity']), 1) if scores_list['elasticity'] else 0)
        graph_wrinkle.append(round(sum(scores_list['wrinkle']) / len(scores_list['wrinkle']), 1) if scores_list['wrinkle'] else 0)

    return jsonify(
        graph_dates=graph_dates,
        graph_moisture=graph_moisture,
        graph_elasticity=graph_elasticity,
        graph_wrinkle=graph_wrinkle
    )

def resize_image_if_needed(filepath, max_size_mb=1.5):
    """이미지 파일이 최대 크기를 초과하면 용량을 줄입니다."""
    max_size_bytes = max_size_mb * 1024 * 1024
    if os.path.getsize(filepath) > max_size_bytes:
        try:
            img = cv2.imread(filepath)
            if img is None:
                print(f"이미지 파일을 읽을 수 없습니다: {filepath}")
                return

            quality = 90
            
            while os.path.getsize(filepath) > max_size_bytes and quality > 10:
                ext = os.path.splitext(filepath)[1].lower()
                if ext in ['.jpg', '.jpeg']:
                    params = [cv2.IMWRITE_JPEG_QUALITY, quality]
                elif ext == '.png':
                    params = [cv2.IMWRITE_PNG_COMPRESSION, max(0, 9 - (90 - quality) // 10)]
                else:
                    params = []
                
                cv2.imwrite(filepath, img, params)
                quality -= 5

            print(f"이미지 용량 조정 완료: {filepath}")

        except Exception as e:
            print(f"이미지 리사이징 중 오류 발생: {e}")

@app.route('/analyze', methods=['POST'])
def analyze_image():
    if 'user_id' not in session:
        flash('분석을 진행하려면 먼저 로그인해주세요.')
        return redirect(url_for('login'))
    if 'image' not in request.files or request.files['image'].filename == '':
        flash('파일이 선택되지 않았습니다.')
        return redirect(request.url)

    file = request.files['image']
    if not (file and allowed_file(file.filename)):
        flash('허용되지 않는 파일 형식입니다.')
        return redirect(url_for('analysis'))

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # 이미지 용량 조절 함수 호출
    # Base64 인코딩 시 크기가 약 33% 증가하므로, API 제한(1.5MB)을 고려하여 파일 크기 제한을 1.0MB로 낮춥니다.
    resize_image_if_needed(filepath, max_size_mb=1.0)

    if not is_face_image(filepath):
        flash("얼굴이 인식되지 않습니다. 얼굴이 보이는 사진을 업로드해주세요.")
        os.remove(filepath)
        return redirect(url_for('analysis'))

    scores = get_skin_scores(filepath)
    if scores is None:
        flash('피부 점수 분석 중 오류가 발생했습니다.')
        os.remove(filepath)
        return redirect(url_for('analysis'))

    reco_data = generate_recommendations(scores, session.get('username', '방문자'))
    
    # scores 딕셔너리에서 skin_type을 직접 가져옴
    skin_type = scores.get('skin_type', '알 수 없음')

    # scores_serializable에 skin_type을 포함시키고, 기존 점수들은 float으로 변환
    scores_serializable = {
        'moisture': float(scores.get('moisture', 50.0)),
        'elasticity': float(scores.get('elasticity', 50.0)),
        'wrinkle': float(scores.get('wrinkle', 65.0)),
        'skin_type': skin_type # 문자열 그대로 저장
    }
    
    # --- Prepare data for the recommendations part ---
    db = get_db()
    concerns = reco_data['concerns_for_template']
    current_season = get_current_season()
    makeup = 'no' # Assuming default, or get from form if available

    morning_routine = get_morning_routine_structure(db, skin_type, concerns, current_season, makeup)
    night_routine = get_night_routine_structure(db, skin_type, concerns, current_season, makeup)
    
    now = datetime.now()
    user_info = {
        "username": session.get('username', '방문자'),
        "date_info": {"year": now.year, "month": now.month, "day": now.day},
        "skin_type": skin_type,
        "concerns": concerns,
        "season": current_season,
        "makeup": makeup
    }
    
    recommendations_data = {
        "user_info": user_info,
        "morning_routine": morning_routine,
        "night_routine": night_routine
    }

    # Store recommendations in session for the new routines page
    session['recommendations_data'] = recommendations_data

    # Save analysis to DB
    db.execute(
        'INSERT INTO analyses (user_id, skin_type, recommendation_text, scores_json, concerns_json, image_filename) VALUES (?, ?, ?, ?, ?, ?)',
        (session['user_id'], skin_type, reco_data['recommendation_text'], json.dumps(scores_serializable), json.dumps(concerns), filename)
    )
    db.commit()

    # Prepare data for the result part
    # main_score 계산 시 skin_type은 제외
    concern_scores = {k: v for k, v in scores.items() if k not in ['skin_type']}
    main_score = sum(concern_scores.values()) / len(concern_scores) if concern_scores else 0
    result_summary = generate_result_summary(session.get('username', '방문자'), main_score, skin_type, reco_data['top_concerns_names'])
    
    # Move file
    static_dir = os.path.join('static', 'uploads_temp')
    if not os.path.exists(static_dir): os.makedirs(static_dir)
    shutil.move(filepath, os.path.join(static_dir, filename))

    # Render the combined result.html with all data
    return render_template(
        'result.html', 
        main_score=main_score, 
        scores=concern_scores, 
        uploaded_image=url_for('static', filename=f'uploads_temp/{filename}'), 
        result_summary=result_summary,
        recommendations=recommendations_data,
        skin_type=skin_type,
        # Pass original full scores dict for face icons if needed
        original_scores=scores_serializable
    )

@app.route('/routines')
def routines():
    recommendations = session.get('recommendations_data', None)
    if not recommendations:
        flash('먼저 피부 분석을 진행해주세요.', 'info')
        return redirect(url_for('analysis'))
    return render_template('routines.html', recommendations=recommendations)

@app.route('/recommendations')
def recommendations():
    results = session.get('skin_analysis_results', None)
    if not results:
        return render_template('recommendations.html', skin_type="분석 전", concerns=[], recommendation_text='피부 분석을 먼저 진행해주세요. <a href="/analysis">분석 페이지로 이동</a>', products=[], current_season='N/A', recommendations={})
    
    # 피부 타입과 고민에 따른 제품 추천
    skin_type = results.get('skin_type', 'N/A')
    concerns = results.get('concerns', [])
    scores = results.get('scores', {})
    current_season = get_current_season()
    makeup = results.get('makeup', 'no')  # 메이크업 여부 (기본값: no)
    
    # 새로운 구조화된 추천 시스템
    db = get_db()
    morning_routine = get_morning_routine_structure(db, skin_type, concerns, current_season, makeup)
    night_routine = get_night_routine_structure(db, skin_type, concerns, current_season, makeup)
    
    # 사용자 정보
    now = datetime.now()
    user_info = {
        "username": session.get('username', '방문자'),
        "date_info": {
            "year": now.year,
            "month": now.month,
            "day": now.day
        },
        "skin_type": skin_type,
        "concerns": concerns,
        "season": current_season,
        "makeup": makeup
    }
    
    # 최종 추천 구조
    recommendations = {
        "user_info": user_info,
        "morning_routine": morning_routine,
        "night_routine": night_routine
    }
    
    return render_template('recommendations.html', 
                         skin_type=skin_type, 
                         concerns=concerns, 
                         recommendation_text=results.get('recommendation_text', '오류가 발생했습니다.'), 
                         scores=scores,
                         current_season=current_season,
                         makeup=makeup,
                         recommendations=recommendations)

def get_current_season():
    """현실적인 기후 변화를 반영하여 현재 계절을 반환합니다."""
    month = datetime.now().month
    
    # 여름: 5월 ~ 9월 (길어진 여름)
    if month in [5, 6, 7, 8, 9]:
        return 'summer'
    # 겨울: 12월, 1월, 2월 (짧아진 겨울)
    elif month in [12, 1, 2]:
        return 'winter'
    # 환절기 (봄, 가을): 3월, 4월, 10월, 11월
    else:
        return 'spring_fall'

def get_recommended_moisturizer(skin_type, season):
    """계절별 최적화된 보습제를 추천합니다."""
    try:
        db = get_db()
        
        if season == 'summer':
            # 여름: 가벼운 제형 선호
            query = """
                SELECT * FROM products 
                WHERE main_category = '크림' 
                AND sub_category IN ('수분', '진정', '모공')
                ORDER BY 
                    CASE
                        WHEN name LIKE '%젤%' OR name LIKE '%gel%' THEN 0
                        WHEN name LIKE '%플루이드%' OR name LIKE '%fluid%' THEN 0
                        WHEN name LIKE '%수딩%' OR name LIKE '%soothing%' THEN 1
                        WHEN name LIKE '%워터%' OR name LIKE '%water%' THEN 1
                        ELSE 2
                    END, rank ASC
                LIMIT 3
            """
        elif season == 'winter':
            # 겨울: 리치한 제형 선호
            query = """
                SELECT * FROM products 
                WHERE main_category = '크림' 
                AND sub_category IN ('보습', '안티에이징')
                ORDER BY 
                    CASE
                        WHEN name LIKE '%밤%' OR name LIKE '%balm%' THEN 0
                        WHEN name LIKE '%리치%' OR name LIKE '%rich%' THEN 0
                        WHEN name LIKE '%인텐스%' OR name LIKE '%intense%' THEN 0
                        WHEN name LIKE '%장벽%' OR name LIKE '%barrier%' THEN 0
                        WHEN name LIKE '%시카%' OR name LIKE '%cica%' THEN 1
                        ELSE 2
                    END, rank ASC
                LIMIT 3
            """
        else:
            # 환절기: 중간 제형
            query = """
                SELECT * FROM products 
                WHERE main_category = '크림' 
                AND sub_category IN ('수분', '보습', '진정')
                ORDER BY rank ASC
                LIMIT 3
            """
        
        cursor = db.execute(query)
        products = cursor.fetchall()
        return [dict(product) for product in products]
        
    except Exception as e:
        print(f"보습제 추천 중 오류: {e}")
        return []

def get_hyper_personalized_cleanser(skin_type, makeup, concerns):
    """초개인화 클렌저 추천 함수"""
    try:
        db = get_db()
        
        # 클렌저 그룹 정의
        first_step_cleansers = ['클렌징오일', '클렌징밤', '클렌징워터', '클렌징로션/크림', '립/아이리무버']
        second_step_cleansers = ['클렌징폼', '클렌징젤', '클렌징비누', '클렌징파우더']
        
        # 피부 타입별 클렌저 타입 매핑
        skin_type_cleanser_mapping = {
            '건성': {
                'first': ['클렌징오일', '클렌징밤', '클렌징워터'],
                'second': ['클렌징폼', '클렌징젤']
            },
            '지성': {
                'first': ['클렌징오일', '클렌징워터'],
                'second': ['클렌징폼', '클렌징젤', '클렌징비누']
            },
            '민감성': {
                'first': ['클렌징밤', '클렌징워터'],
                'second': ['클렌징폼', '클렌징젤']
            },
            '복합성': {
                'first': ['클렌징오일', '클렌징워터'],
                'second': ['클렌징폼', '클렌징젤']
            }
        }
        
        # 메이크업 여부에 따른 클렌저 타입 결정
        if makeup == 'yes':
            # 메이크업 사용 시: 1차 + 2차 세안
            first_step_type = skin_type_cleanser_mapping.get(skin_type, {}).get('first', ['클렌징오일'])[0]
            second_step_type = skin_type_cleanser_mapping.get(skin_type, {}).get('second', ['클렌징폼'])[0]
        else:
            # 메이크업 미사용 시: 2차 세안만
            first_step_type = None
            second_step_type = skin_type_cleanser_mapping.get(skin_type, {}).get('second', ['클렌징폼'])[0]
        
        recommended_cleansers = []
        
        # 1차 세안제 추천 (메이크업 사용 시)
        if first_step_type and makeup == 'yes':
            first_cleanser = get_cleanser_by_type_and_concerns(db, first_step_type, concerns, 'first')
            if first_cleanser:
                recommended_cleansers.append(first_cleanser)
        
        # 2차 세안제 추천
        second_cleanser = get_cleanser_by_type_and_concerns(db, second_step_type, concerns, 'second')
        if second_cleanser:
            recommended_cleansers.append(second_cleanser)
        
        return recommended_cleansers
        
    except Exception as e:
        print(f"클렌저 추천 중 오류: {e}")
        return []

def get_cleanser_by_type_and_concerns(db, cleanser_type, concerns, step):
    """특정 타입의 클렌저 중 고민과 일치하는 제품을 찾습니다."""
    try:
        # 고민을 sub_category로 매핑
        concern_mapping = {
            '수분 부족': '수분',
            '민감성': '진정',
            '주름': '안티에이징',
            '색소침착': '브라이트닝',
            '모공': '모공',
            '트러블': '트러블',
            '각질': '각질'
        }
        
        # 사용자의 고민을 sub_category로 변환
        target_sub_categories = []
        for concern in concerns:
            if concern in concern_mapping:
                target_sub_categories.append(concern_mapping[concern])
        
        # 고민이 없으면 기본값
        if not target_sub_categories:
            target_sub_categories = ['수분', '진정']
        
        # 1순위: 고민과 정확히 일치하는 제품 검색
        query = """
            SELECT * FROM products 
            WHERE main_category = '클렌징' 
            AND middle_category = ? 
            AND sub_category IN ({})
            ORDER BY rank ASC 
            LIMIT 1
        """.format(','.join(['?'] * len(target_sub_categories)))
        
        cursor = db.execute(query, [cleanser_type] + target_sub_categories)
        product = cursor.fetchone()
        
        if product:
            return dict(product)
        
        # 2순위: 고민 필터 없이 해당 타입의 랭킹 1위 제품
        fallback_query = """
            SELECT * FROM products 
            WHERE main_category = '클렌징' 
            AND middle_category = ? 
            ORDER BY rank ASC 
            LIMIT 1
        """
        
        cursor = db.execute(fallback_query, (cleanser_type,))
        product = cursor.fetchone()
        
        if product:
            return dict(product)
        
        return None
        
    except Exception as e:
        print(f"클렌저 검색 중 오류: {e}")
        return None



def get_products_by_query(db, query, params=()):
    """Helper function to fetch products and format them."""
    products = db.execute(query, params).fetchall()
    if not products:
        return None, []
    
    primary = dict(products[0])
    alternatives = [dict(p) for p in products[1:3]]
    return primary, alternatives

def get_morning_routine_structure(db, skin_type, concerns, current_season, makeup='no'):
    """5가지 피부 타입과 주요 고민에 따른 아침 루틴을 구조화하여 추천합니다."""
    steps = []
    user_concerns = {c['name'] for c in concerns if c.get('name')}

    # ------------------- 공통 로직: STEP 2 (집중 케어) -------------------
    step2_query, step2_params, step2_desc = None, [], ""
    has_wrinkle_elasticity_concern = '주름' in user_concerns or '탄력' in user_concerns
    has_moisture_concern = '수분' in user_concerns
    has_wrinkle_elasticity_moisture_concern = '주름' in user_concerns or '탄력' in user_concerns and '수분' in user_concerns

    if has_wrinkle_elasticity_moisture_concern:
        step2_desc = "아침에도 가볍게 사용하는 안티에이징 제품으로 주름과 탄력을 관리하고, 피부에 촉촉한 수분감을 더하세요."
        step2_query = """SELECT * FROM products 
                         WHERE main_category = '스킨케어' AND middle_category = '에센스/앰플/세럼' 
                         AND sub_category IN ('안티에이징', '리페어', '수분', '보습') 
                         AND name NOT LIKE '%나이트%' AND name NOT LIKE '%리치%' 
                         AND name LIKE '%펩타이드%' OR name LIKE '%아데노신%' OR name LIKE '%비타민%' OR name LIKE '%나이아신%' OR name LIKE '%레티놀%'
                         ORDER BY rank ASC LIMIT 3"""
        step3_desc = "이제 무거운 사용감 걱정 없이 산뜻한 안티에이징으로 하루를 시작하고, 빈틈없이 촉촉한 피부를 느껴보세요."
        step3_query = """SELECT * FROM products 
                         WHERE main_category = '스킨케어' AND middle_category = '크림' 
                         AND sub_category IN ('안티에이징', '리페어', '수분', '보습') 
                         AND name NOT LIKE '%나이트%' AND name NOT LIKE '%리치%' 
                         AND name LIKE '%펩타이드%' OR name LIKE '%아데노신%' OR name LIKE '%비타민%' OR name LIKE '%나이아신%' OR name LIKE '%레티놀%'                    
                         ORDER BY rank ASC LIMIT 3"""  
                                                
    elif has_wrinkle_elasticity_concern:
        step2_desc = "아침에도 부담 없는 텍스처로 주름과 탄력을 동시에 관리하세요."
        step2_query = """SELECT * FROM products 
                         WHERE main_category = '스킨케어' AND middle_category = '에센스/앰플/세럼' 
                         AND sub_category IN ('안티에이징', '리페어') 
                         AND name NOT LIKE '%나이트%' AND name NOT LIKE '%리치%' 
                         ORDER BY rank ASC LIMIT 3"""
        step3_desc = "주름 개선과 탄력 강화에 효과적인 크림으로 피부에 힘을 불어넣어 주세요"
        step3_query = """SELECT * FROM products 
                         WHERE main_category = '스킨케어' AND middle_category = '크림' 
                         AND sub_category IN ('안티에이징', '리페어') 
                         AND name NOT LIKE '%나이트%' AND name NOT LIKE '%리치%' 
                         AND name LIKE '%펩타이드%' OR OR name LIKE '%아데노신%' OR name LIKE '%콜라겐%' OR name LIKE '%비타민%'
                         ORDER BY rank ASC LIMIT 3"""  
                         
    elif has_moisture_concern:
        step2_desc = "수분감이 풍부한 제품으로 피부 속부터 촉촉함을 채워주세요."
        step2_query = """SELECT * FROM products 
                         WHERE main_category = '스킨케어' AND middle_category = '에센스/앰플/세럼' 
                         AND sub_category IN ('수분', '보습') 
                         AND name LIKE '%비타민%' OR OR name LIKE '%펩타이드%' OR name LIKE '%나이아신%' OR name LIKE '%히알루론산%'
                         ORDER BY rank ASC LIMIT 3"""       
        step3_desc = "하루 종일 촉촉한 피부를 위해 가벼우면서도 보습력 있는 크림을 선택하세요."
        step3_query = """SELECT * FROM products 
                         WHERE main_category = '스킨케어' AND middle_category = '크림' 
                         AND sub_category IN ('안티에이징', '리페어') 
                         AND name NOT LIKE '%나이트%' AND name NOT LIKE '%리치%' 
                         AND name LIKE '%세라마이드%' OR OR name LIKE '%코엔자임%' OR name LIKE '%스쿠알란%' OR name LIKE '%촉촉%' OR name LIKE '%히알루론산%'
                         ORDER BY rank ASC LIMIT 3"""                    
                         

    # ------------------- 💧 건성 (Dry) -------------------
    if skin_type == 'Dry':
        # 1단계: 아침 세안
        q1 = "SELECT * FROM products WHERE main_category = '클렌징' AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' AND (name LIKE '%밀크%' OR name LIKE '%로션%' OR name LIKE '%폼%' OR name LIKE '%젤%' OR name LIKE '%워터%') AND (name LIKE '%히알루론산%' OR name LIKE '%촉촉%' OR name LIKE '%수분%' OR name LIKE '%약산성%') ORDER BY rank ASC LIMIT 3"
        p1, a1 = get_products_by_query(db, q1)
        steps.append({"step_title": "STEP 1. 아침 세안", "step_description": "순한 약산성 클렌저로 자극없이 부드럽게 세안하세요.", "primary_recommendation": p1, "alternatives": a1})

        # 2단계: 수분 충전 (고민에 따라 분기)
        if not step2_query: # 특정 고민이 없을 경우
            step2_desc = "점성이 있는 에센스나 앰플로 깊은 수분감을 채워주세요."
            step2_query = "SELECT * FROM products WHERE main_category = '스킨케어' AND middle_category = '에센스/앰플/세럼' AND sub_category IN ('보습', '수분', '진정') AND (name LIKE '%히알루론산%' OR name LIKE '%판테놀%' OR name LIKE '%글리세린%' OR name LIKE '%수분%') ORDER BY rank ASC LIMIT 3"
        p2, a2 = get_products_by_query(db, step2_query, step2_params)
        steps.append({"step_title": "STEP 2. 집중 케어", "step_description": step2_desc, "primary_recommendation": p2, "alternatives": a2})

        # 3단계: 보습 & 보호
        if not step3_query:
            step3_desc="꾸덕한 보습 크림으로 수분 보호막을 만들어주세요."
            step2_query= "SELECT * FROM products WHERE main_category = '스킨케어' AND middle_category = '크림' AND sub_category In ('보습', '수분', '진정') AND (name LIKE '%밤%' OR name LIKE '%리치%' OR name LIKE '%세라마이드%' OR name LIKE '%시어버터%' OR name LIKE '%스쿠알렌%') ORDER BY rank ASC LIMIT 3"
        p3, a3 = get_products_by_query(db, q3)
        steps.append({"step_title": "STEP 3. 보습 & 보호", "step_description": step3_desc, "primary_recommendation": p3, "alternatives": a3})

    # ------------------- ✨ 지성 (Oily) -------------------
    elif skin_type == 'Oily':
        q1 = "SELECT * FROM products WHERE main_category = '클렌징' AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' AND (name LIKE '%폼%' OR name LIKE '%젤%') AND (name LIKE '%티트리%' OR name LIKE '%어성초%' OR name LIKE '%약산성%') ORDER BY rank ASC LIMIT 3"
        p1, a1 = get_products_by_query(db, q1)
        steps.append({"step_title": "STEP 1. 아침 세안", "step_description": "클렌저로 밤새 쌓인 유분을 꼼꼼히 씻어내요.", "primary_recommendation": p1, "alternatives": a1})

        if not step2_query:
            step2_desc = "산뜻한 토너로 피부결을 정돈하고 수분을 공급하세요.<br>부드러운 화장솜으로 닦아내면 밤사이 쌓인 각질 제거에도 도움이 됩니다."
            step2_query = "SELECT * FROM products WHERE main_category = '스킨케어' AND middle_category = '스킨/토너' AND (name LIKE '%워터%' OR name LIKE '%토너%' OR name LIKE '%스킨%') AND (name LIKE '%티트리%' OR name LIKE '%어성초%' OR name LIKE '%나이아신%') ORDER BY rank ASC LIMIT 3"
        p2, a2 = get_products_by_query(db, step2_query, step2_params)
        steps.append({"step_title": "STEP 2. 수분 충전", "step_description": step2_desc, "primary_recommendation": p2, "alternatives": a2})

        if not step3_query:
            step3_desc="끈적이지 않는 크림으로 가볍게 마무리하세요."
            step2_query="SELECT * FROM products WHERE main_category = '스킨케어' AND middle_category = '크림' AND (name LIKE '%수분%' OR name LIKE '%젤%' OR name LIKE '%로션%'  OR name LIKE '%티트리%'  OR name LIKE '%나이아신%') ORDER BY rank ASC LIMIT 3"
        p3, a3 = get_products_by_query(db, q3)
        steps.append({"step_title": "STEP 3. 보습 & 보호", "step_description": step3_desc, "primary_recommendation": p3, "alternatives": a3})

    # ------------------- ⚖️ 중성 (Normal) -------------------
    elif skin_type == 'Normal':
        q1 = "SELECT * FROM products WHERE main_category = '스킨케어' AND middle_category = '스킨/토너' AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' AND (name LIKE '%세럼%' OR name LIKE '%토너%' OR name LIKE '%스킨%') AND (name LIKE '%수분%' OR name LIKE '%히알루론산%') ORDER BY rank ASC LIMIT 3"
        p1, a1 = get_products_by_query(db, q1)
        steps.append({"step_title": "STEP 1. 아침 세안", "step_description": "유수분 밸런스가 깨지지 않도록 가볍게 물세안 또는 순한 클렌저 사용을 추천드립니다.", "primary_recommendation": p1, "alternatives": a1})

        if not step2_query:
            step2_desc = "수분 토너나 가벼운 세럼으로 피부의 유수분 밸런스를 맞춰주세요."
            step2_query = "SELECT * FROM products WHERE main_category = '스킨케어' AND middle_category IN ('스킨/토너', '에센스/앰플/세럼') AND (name LIKE '%수분%' OR name LIKE '%히알루론산%') ORDER BY rank ASC LIMIT 3"
        p2, a2 = get_products_by_query(db, step2_query, step2_params)
        steps.append({"step_title": "STEP 2. 수분 충전", "step_description": step2_desc, "primary_recommendation": p2, "alternatives": a2})

        if not step3_query:
            step3_desc="가벼운 제형의 로션이나 수분크림으로 피부 균형을 유지하세요."
            step2_query="SELECT * FROM products WHERE main_category = '스킨케어' AND middle_category = '크림' AND (name LIKE '%로션%' OR sub_category = '수분') ORDER BY rank ASC LIMIT 3"
        p3, a3 = get_products_by_query(db, q3)
        steps.append({"step_title": "STEP 3. 보습 & 보호", "step_description": step3_desc, "primary_recommendation": p3, "alternatives": a3})

    # ------------------- 복합 건성 (CombinationDry) -------------------
    elif skin_type == 'CombinationDry':
        q1 = "SELECT * FROM products WHERE main_category = '클렌징' AND (name LIKE '%밀크%' OR name LIKE '%젤%') AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' ORDER BY rank ASC LIMIT 3"
        p1, a1 = get_products_by_query(db, q1)
        steps.append({"step_title": "STEP 1. 아침 세안", "step_description": "U존은 미온수로, 유분이 많은 T존은 클렌저로 부드럽게 롤링하며 세안하세요.", "primary_recommendation": p1, "alternatives": a1})

        if not step2_query:
            step2_desc = "수분감이 풍부한 토너를 얼굴 전체에 바른 뒤, 건조한 U존에 한번 더 레이어링합니다."
            step2_query = "SELECT * FROM products WHERE main_category = '스킨케어' AND middle_category = '스킨/토너' AND sub_category = '수분' ORDER BY rank ASC LIMIT 3"
        p2, a2 = get_products_by_query(db, step2_query, step2_params)
        steps.append({"step_title": "STEP 2. 수분 충전", "step_description": step2_desc, "primary_recommendation": p2, "alternatives": a2})

        if not step3_query:
            step3_desc = "가벼운 크림을 얼굴 전체에 바르고, 건조함이 U존에 한번 더 얇게 덧발라요."
            step3_query = "SELECT * FROM products WHERE main_category = '스킨케어' AND middle_category = '크림' AND (name LIKE '%히알루론산%' OR name LIKE '%플루이드%' OR sub_category = '수분') ORDER BY rank ASC LIMIT 3"
        p3, a3 = get_products_by_query(db, step3_query, step3_desc)
        steps.append({"step_title": "STEP 3. 보습 & 보호", "step_description": step3_desc, "primary_recommendation": p3, "alternatives": a3})

    # ------------------- 복합 지성 (CombinationOily) -------------------
    elif skin_type == 'CombinationOily':
        q1 = "SELECT * FROM products WHERE main_category = '클렌징' AND (name LIKE '%폼%' OR name LIKE '%젤%') AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' ORDER BY rank ASC LIMIT 3"
        p1, a1 = get_products_by_query(db, q1)
        steps.append({"step_title": "STEP 1. 아침 세안", "step_description": "미온수로 얼굴을 적신 뒤, T존 중심으로 순한 클렌저를 사용하여 피지와 노폐물을 꼼꼼히 세안하세요.", "primary_recommendation": p1, "alternatives": a1})

        if not step2_query:
            step2_desc = "산뜻한 토너를 화장솜에 묻혀 T존을 중심으로 닦아내고, 나머지 양으로 U존을 가볍게 정돈합니다."
            step2_query = "SELECT * FROM products WHERE main_category = '스킨케어' AND middle_category = '스킨/토너' AND sub_category = '수분' AND name LIKE '%토너' ORDER BY rank ASC LIMIT 3"
        p2, a2 = get_products_by_query(db, step2_query, step2_params)
        steps.append({"step_title": "STEP 2. 수분 충전", "step_description": step2_desc, "primary_recommendation": p2, "alternatives": a2})

        if not step3_query:
            step3_desc="가벼운 젤이나 플루이드 타입의 보습제를 사용하세요."
            step2_query="SELECT * FROM products WHERE main_category = '스킨케어' AND middle_category = '크림' AND (name LIKE '%젤%' OR name LIKE '%플루이드%' OR sub_category = '수분') ORDER BY rank ASC LIMIT 3"
        p3, a3 = get_products_by_query(db, q3)
        steps.append({"step_title": "STEP 3. 보습 & 보호", "step_description": step3_desc, "primary_recommendation": p3, "alternatives": a3})

    # ------------------- 기본 (Fallback) -------------------
    else:
        # 중성 피부 루틴을 기본값으로 사용
        q1 = "SELECT * FROM products WHERE main_category = '클렌징' AND (name LIKE '%폼%' OR name LIKE '%워터%' OR name LIKE '%젤%') AND name LIKE '%약산성%' AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' ORDER BY rank ASC LIMIT 3"
        p1, a1 = get_products_by_query(db, q1)
        steps.append({"step_title": "STEP 1. 아침 세안", "step_description": "약산성 폼 클렌저로 부드럽게 세안하세요.", "primary_recommendation": p1, "alternatives": a1})
     
        q2 = "SELECT * FROM products WHERE main_category = '스킨케어' AND middle_category IN ('스킨/토너', '에센스/앰플/세럼') AND (name LIKE '%수분%' OR name LIKE '%히알루론산%') ORDER BY rank ASC LIMIT 3"
        p2, a2 = get_products_by_query(db, q2)
        steps.append({"step_title": "STEP 2. 수분 충전", "step_description": "수분 토너나 가벼운 세럼으로 피부의 유수분 밸런스를 맞춰주세요.", "primary_recommendation": p2, "alternatives": a2})
    
        q3 = "SELECT * FROM products WHERE main_category = '스킨케어' AND middle_category = '크림' AND (name LIKE '%로션%' OR sub_category = '수분') ORDER BY rank ASC LIMIT 3"
        p3, a3 = get_products_by_query(db, q3)
        steps.append({"step_title": "STEP 3. 보습 & 보호", "step_description": "가벼운 제형의 로션이나 수분크림으로 피부 균형을 유지하세요.", "primary_recommendation": p3, "alternatives": a3})

    return {
        "title": '" Morning "',
        "description": "피부 타입과 고민에 맞춘 아침 스킨케어로 산뜻한 하루를 시작해요.",
        "steps": steps
    }


# ------------------- 나이트루틴 (night routine) -------------------
def get_night_routine_structure(db, skin_type, concerns, current_season, makeup='no'):
    """나이트 루틴 구조화된 추천"""
    steps = []
    user_concerns = {c['name'] for c in concerns if c.get('name')}
    
    # ------------------- 공통 로직 -------------------
    
    # ------------------- STEP 1: 이중 세안 -------------------
    step1 = {
        "step_title": "STEP 1. 꼼꼼한 이중 세안",
        "step_description": "하루 동안 쌓인 노폐물을 씻어내요.",
        "primary_recommendation": None,
        "alternatives": []
    }
    
    if makeup == 'yes':
        # 메이크업 제거용 클렌저
        cleanser_query = """
            SELECT * FROM products 
            WHERE main_category = '클렌징' 
            AND (name LIKE '%오일%' OR name LIKE '%밤%' OR name LIKE '%폼%')
            ORDER BY rank ASC
            LIMIT 3
        """
        step1["step_description"] = "메이크업과 노폐물을 깨끗하게 제거해요."
    else:
        # 일반 클렌저
        cleanser_query = """
            SELECT * FROM products 
            WHERE main_category = '클렌징' 
            AND (name LIKE '%폼%' OR name LIKE '%젤%' OR name LIKE '%워터%')
            ORDER BY rank ASC
            LIMIT 3
        """
    
    cleansers = db.execute(cleanser_query).fetchall()
    if cleansers:
        primary = dict(cleansers[0])
        step1["primary_recommendation"] = primary
        
        # 대안 제품들
        alternatives = []
        for i in range(1, min(3, len(cleansers))):
            alt = dict(cleansers[i])
            alternatives.append(alt)
        step1["alternatives"] = alternatives
    
    steps.append(step1)
    
    # ------------------- STEP 2: 집중 케어 (세럼) -------------------
    serum_query = """
        SELECT * FROM products 
        WHERE main_category = '스킨케어' AND middle_category = '에센스/앰플/세럼'
        AND sub_category IN ('보습', '리페어', '안티에이징')
        ORDER BY rank ASC
        LIMIT 3
    """
    serums = db.execute(serum_query).fetchall()
    
    step2 = {
        "step_title": "STEP 2. 집중 케어",
        "step_description": "피부 깊숙이 영양을 공급해요.",
        "primary_recommendation": None,
        "alternatives": []
    }
    
    if serums:
        primary = dict(serums[0])
        step2["primary_recommendation"] = primary
        
        # 대안 제품들
        alternatives = []
        for i in range(1, min(3, len(serums))):
            alt = dict(serums[i])
            alternatives.append(alt)
        step2["alternatives"] = alternatives
    
    steps.append(step2)
    
    # ------------------- STEP 3: 마무리 보습 (크림) -------------------
    cream_query = """
        SELECT * FROM products 
        WHERE main_category = '스킨케어' AND middle_category = '크림'
        AND (name LIKE '%밤%' OR name LIKE '%크림%' OR sub_category = '보습')
        ORDER BY rank ASC
        LIMIT 3
    """
    creams = db.execute(cream_query).fetchall()
    
    step3 = {
        "step_title": "STEP 3. 마무리 보습",
        "step_description": "피부 장벽을 강화하고 수분을 잠가요.",
        "primary_recommendation": None,
        "alternatives": []
    }
    
    if creams:
        primary = dict(creams[0])
        step3["primary_recommendation"] = primary
        
        # 대안 제품들
        alternatives = []
        for i in range(1, min(3, len(creams))):
            alt = dict(creams[i])
            alternatives.append(alt)
        step3["alternatives"] = alternatives
    
    steps.append(step3)
    
    return {
        "title": '" Night "',
        "description": "하루 동안 쌓인 노폐물을 씻어내고 피부 깊숙이 영양을 공급해요.",
        "steps": steps
    }

def get_recommended_products(skin_type, concerns, scores, makeup='no'):
    """기존 호환성을 위한 래퍼 함수"""
    try:
        db = get_db()
        current_season = get_current_season()
        
        # 새로운 구조화된 추천 시스템 사용
        morning_routine = get_morning_routine_structure(db, skin_type, concerns, current_season, makeup)
        night_routine = get_night_routine_structure(db, skin_type, concerns, current_season, makeup)
        
        # 모든 제품을 하나의 리스트로 통합
        all_products = []
        
        # 모닝 루틴에서 제품 추출
        for step in morning_routine['steps']:
            if step['primary_recommendation']:
                all_products.append(step['primary_recommendation'])
            all_products.extend(step['alternatives'])
        
        # 나이트 루틴에서 제품 추출
        for step in night_routine['steps']:
            if step['primary_recommendation']:
                all_products.append(step['primary_recommendation'])
            all_products.extend(step['alternatives'])
        
        # 랭킹 순으로 정렬하고 상위 15개만 반환
        all_products.sort(key=lambda x: x.get('rank', 999))
        return all_products[:15]
        
    except Exception as e:
        print(f"제품 추천 중 오류: {e}")
        return []

# --- 사용자 인증 라우팅 ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        error = None
        if not username: error = 'Username is required.'
        elif not password: error = 'Password is required.'
        elif not email: error = 'Email is required.'

        if error is None:
            try:
                db.execute("INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)", (username, email, generate_password_hash(password)))
                db.commit()
            except db.IntegrityError:
                error = f"Email {email} is already registered."
            else:
                flash('회원가입 성공! 로그인해주세요.', 'success')
                return redirect(url_for("login"))
        flash(error, 'danger')
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()

        if user is None or not check_password_hash(user['password_hash'], password):
            error = '잘못된 이메일 또는 비밀번호입니다.'
        
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('로그인 성공!', 'success')
            return redirect(url_for('index'))
        flash(error, 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('로그아웃되었습니다.', 'info')
    return redirect(url_for('index'))

# --- 서버 실행 ---
if __name__ == '__main__':
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True, port=5001)
