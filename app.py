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

from datetime import datetime, timedelta

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

# --- 분석 로직 헬퍼 함수 (이전과 동일) ---
def get_skin_scores(filepath):
    """외부 스크립트를 실행하여 피부 점수를 계산합니다."""
    try:
        scores = {}
        moisture_script_path = os.path.join(os.path.dirname(__file__), '0812-moisture.py')
        moisture_result = subprocess.run([sys.executable, moisture_script_path, filepath], capture_output=True, text=True, check=True, encoding='utf-8')
        scores['moisture'] = float(moisture_result.stdout.strip())
        elasticity_script_path = os.path.join(os.path.dirname(__file__), '0808-test1.py')
        elasticity_result = subprocess.run([sys.executable, elasticity_script_path, filepath], capture_output=True, text=True, check=True, encoding='utf-8')
        scores['elasticity'] = float(elasticity_result.stdout.strip())
        scores['wrinkle'] = 65.0  # 임의의 값
        scores['skin_type_score'] = 50.0 # 임의의 값
        return scores
    except (subprocess.CalledProcessError, FileNotFoundError, ValueError) as e:
        print(f"점수 분석 스크립트 오류: {e}")
        return None

def generate_recommendations(scores, username):
    """점수를 기반으로 피부 타입, 고민, 추천 문구를 생성합니다."""
    # 피부타입 점수를 기반으로 피부 타입 결정 (임시 로직)
    skin_type_score = scores.get('skin_type_score', 50)
    if skin_type_score < 20:
        skin_type = "건성"
    elif skin_type_score < 40:
        skin_type = "수부지"
    elif skin_type_score < 60:
        skin_type = "복합성(임시)"
    elif skin_type_score < 80:
        skin_type = "중성"
    else:
        skin_type = "지성"

    # 피부타입 점수를 제외한 나머지 점수로 주요 고민 선정
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
    
    # Determine the introductory message based on concerns
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

    # Determine the specific product recommendation
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
        product_recommendation = "레티놀과 비타민 C가 들어간 주름 개선 제품으로 피부 재생을 돕고 탄력 있는 피부로 관리하세요."
    elif '탄력' in top_concerns_names:
        product_recommendation = "펩타이드와 콜라겐 성분이 함유된 제품으로 피부 결을 단단하게 하고 건강한 탄력을 되찾아 보세요."

    # Combine messages
    if intro_message: # If there are any concerns
        recommendation_text = intro_message + "<br>" + product_recommendation
    else: # No concerns
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
    # summary += "'추천 상품 보러가기' 버튼을 통해 나에게 맞는 화장품을 찾아보세요."
    
    return summary

# --- 웹페이지 라우팅 ---
@app.route('/')
def index(): return render_template('index.html')

@app.route('/analysis')
def analysis(): return render_template('analysis.html')

@app.route('/history')
def history():
    if 'user_id' not in session:
        flash('기록을 보려면 먼저 로그인해주세요.')
        return redirect(url_for('login'))

    db = get_db()
    # Fetch all analyses for the detailed list view
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

    # Aggregate data for the graph, ensuring all days in the range are present
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
                daily_scores[analysis_date_key]['wrinkle'].append(scores.get('wrinkle', 65.0)) # Default wrinkle score
            except (json.JSONDecodeError, TypeError):
                continue # Skip if scores_json is invalid

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
    session['skin_analysis_results'] = {'skin_type': reco_data['skin_type'], 'concerns': reco_data['concerns_for_template'], 'recommendation_text': reco_data['recommendation_text'], 'scores': scores}
    
    db = get_db()
    db.execute(
        'INSERT INTO analyses (user_id, skin_type, recommendation_text, scores_json, concerns_json, image_filename) VALUES (?, ?, ?, ?, ?, ?)',
        (session['user_id'], reco_data['skin_type'], reco_data['recommendation_text'], json.dumps(scores), json.dumps(reco_data['concerns_for_template']), filename)
    )
    db.commit()

    concern_scores = {k: v for k, v in scores.items() if k != 'skin_type_score'}
    main_score = sum(concern_scores.values()) / len(concern_scores)
    result_summary = generate_result_summary(session.get('username', '방문자'), main_score, reco_data['skin_type'], reco_data['top_concerns_names'])
    

    static_dir = os.path.join('static', 'uploads_temp')
    if not os.path.exists(static_dir): os.makedirs(static_dir)
    shutil.move(filepath, os.path.join(static_dir, filename))

    return render_template('result.html', main_score=main_score, scores=concern_scores, uploaded_image=url_for('static', filename=f'uploads_temp/{filename}'), result_summary=result_summary)

@app.route('/recommendations')
def recommendations():
    results = session.get('skin_analysis_results', None)
    if not results:
        return render_template('recommendations.html', skin_type="분석 전", concerns=[], recommendation_text='피부 분석을 먼저 진행해주세요. <a href="/analysis">분석 페이지로 이동</a>')
    return render_template('recommendations.html', skin_type=results.get('skin_type', 'N/A'), concerns=results.get('concerns', []), recommendation_text=results.get('recommendation_text', '오류가 발생했습니다.'), scores=results.get('scores', {}))

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
    app.run(debug=True)
