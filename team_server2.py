from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask import send_from_directory
from sqlalchemy import LargeBinary
from datetime import datetime, timedelta
import json
from dateutil import parser
from flask_migrate import Migrate
 


# Flask 애플리케이션 생성
app = Flask(__name__)
 
# CORS(Cross-Origin Resource Sharing) 설정 업데이트
CORS(app, origins="*")

# 데이터베이스 설정
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['JWT_SECRET_KEY'] = '아무거나넣어주세요'  # 여기에 비밀 키를 넣어주세요
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)  # 토큰 만료 시간 (1일로 설정)


db = SQLAlchemy(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)

# # 파일 업로드를 위한 설정
UPLOAD_FOLDER1 = 'C:/flask_team/uploads'  # Windows 경로는 이렇게 설정합니다.
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER1'] = UPLOAD_FOLDER1

# 업로드 설정
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# 사용자 모델 정의
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

# 조완우가 만든 프로젝트 모델 정의
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    image_path = db.Column(db.String(200))  # 이미지 파일 경로

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# GuestbookEntry 모델
class GuestbookEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    views = db.Column(db.Integer, default=0)
    message = db.Column(db.String(500), nullable=False)

# FormData 모델
class FormData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_files = db.Column(db.String(500), nullable=False)
    project_name = db.Column(db.String(100), nullable=False)
    number_of_people = db.Column(db.String(50), nullable=False)
    goals = db.Column(db.String(500), nullable=False)
    what_learned = db.Column(db.String(500), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    your_stake = db.Column(db.String(50), nullable=False)

# AboutMe모델
class AboutMeEdit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    oneline = db.Column(db.String(255),nullable=False)
    tools = db.Column(db.String(255),nullable=False)
    skills = db.Column(db.String(255),nullable=False)
    certificate = db.Column(db.String(255),nullable=False)
    contact = db.Column(db.String(255),nullable=False)
    education = db.Column(db.String(255),nullable=False)
    image_path = db.Column(db.String(255),nullable=False)


# 회원가입 엔드포인트
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': '아이디와 비밀번호를 입력하세요'}), 400

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'message': '이미 존재하는 사용자입니다'}), 409

    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': '회원가입 성공!'})

# 로그인 엔드포인트
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': '아이디와 비밀번호를 입력하세요'}), 400

    user = User.query.filter_by(username=username).first()
    if user and user.password == password:
        access_token = create_access_token(identity=user.id)
        return jsonify({'message': '로그인 성공!', 'access_token': access_token}), 200
    
    return jsonify({'message': '로그인 실패! 아이디 혹은 비밀번호가 일치하지 않습니다.'}), 401

# 보호된 엔드포인트 예제
@app.route('/protected', methods=['GET'])
@jwt_required()  # 이 엔드포인트는 유효한 액세스 토큰이 필요합니다
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


# `create_project()` 엔드포인트
@app.route('/project', methods=['POST'])
def create_project():
 title = request.form['title']
 description = request.form['description']
 image = request.files['image']

 if image and allowed_file(image.filename):
  filename = secure_filename(image.filename)
  # `image_path` 값을 수정합니다.
  image_path = os.path.join(app.config['UPLOAD_FOLDER1'], filename)
  image.save(image_path)

  new_project = Project(title=title, description=description, image_path=os.path.basename(image_path))
  db.session.add(new_project)
  db.session.commit()

  # 클라이언트에 반환할 응답 데이터에 이미지 경로와 ID를 포함합니다.
  return jsonify({
   'id': new_project.id,
   'title': new_project.title,
   'description': new_project.description,
   'image_path': os.path.basename(image_path),
   'message': '프로젝트가 생성되었습니다.'
  }), 201
 else:
  return jsonify({'message': '허용되지 않는 파일 형식입니다.'}), 400

# 프로젝트 목록을 불러오는 엔드포인트
@app.route('/project', methods=['GET'])
def get_projects():
    projects = Project.query.all()
    project_list = [{
        'id': project.id,
        'title': project.title,
        'description': project.description,
        'image_path': project.image_path
    } for project in projects]

    # 이미지 경로를 서버 URL과 결합하여 전달합니다.
    for project in project_list:
        if project['image_path']:
            project['image_url'] = f"http://localhost:9998/uploads/{project['image_path'].split('/')[-1]}"

    return jsonify(project_list), 200

@app.route('/uploads/<filename>')
def uploaded_file1(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER1'], filename)

# 이미지 업로드 라우트
@app.route('/form/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# 프로젝트 삭제 엔드포인트
@app.route('/project/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    try:
        project = Project.query.get_or_404(project_id)
        db.session.delete(project)
        db.session.commit()
        return jsonify({'message': '프로젝트가 삭제되었습니다.'}), 200
    except Exception as e:
        logging.error(f'Error deleting project: {e}')
        return jsonify({'message': '프로젝트 삭제 중 오류가 발생했습니다.'}), 500

# 방명록 항목 생성 라우트
@app.route('/Visitors', methods=['POST'])
def create_guestbook_entry():
    data = request.json
    title = data.get('title')
    name = data.get('name')
    message = data.get('message')
    date_str = data.get('date')
    if date_str:
        # 날짜 형식 변환
        date_str = date_str.replace('오후', 'PM').replace('오전', 'AM')
        date = datetime.strptime(date_str, '%Y. %m. %d. %p %I:%M:%S')
    else:
        date = datetime.utcnow()

    new_entry = GuestbookEntry(
        title=title,
        name=name,
        message=message,
        date=date,
        views=0
    )
    
    db.session.add(new_entry)
    db.session.commit()
    
    return jsonify({'message': '방명록 항목이 생성되었습니다.'}), 201


# 방명록 조회수 증가 라우트
@app.route('/Visitors/increase-views/<int:entry_id>', methods=['POST'])
def increase_views(entry_id):
    entry = GuestbookEntry.query.get(entry_id)
    if entry:
        entry.views += 1
        db.session.commit()
        return jsonify({'message': '조회수가 증가되었습니다.'}), 200
    else:
        return jsonify({'message': '방명록 항목을 찾을 수 없습니다.'}), 404

# 방명록 조회 라우트
@app.route('/Visitors', methods=['GET'])
def get_guestbook_entries():
    entries = GuestbookEntry.query.all()
    entries_list = [{
        'id': entry.id,
        'title': entry.title,
        'name': entry.name,
        'date': entry.date.strftime('%Y-%m-%d %H:%M:%S'),
        'views': entry.views,
        'message': entry.message
    } for entry in entries]
    return jsonify(entries_list), 200

# 방명록 삭제 라우트
@app.route('/Visitors/<int:entry_id>', methods=['DELETE'])
def delete_guestbook_entry(entry_id):
    entry = GuestbookEntry.query.get(entry_id)
    if entry:
        db.session.delete(entry)
        db.session.commit()
        return jsonify({'message': '방명록 항목이 삭제되었습니다.'}), 200
    else:
        return jsonify({'message': '방명록 항목을 찾을 수 없습니다.'}), 404

# 방명록 수정 라우트
@app.route('/Visitors/<int:entry_id>', methods=['PUT'])
def update_guestbook_entry(entry_id):
    data = request.json
    entry = GuestbookEntry.query.get(entry_id)
    if entry:
        entry.title = data.get('title', entry.title)
        entry.name = data.get('name', entry.name)
        entry.message = data.get('message', entry.message)
        db.session.commit()
        return jsonify({'message': '방명록 항목이 수정되었습니다.'}), 200
    else:
        return jsonify({'message': '방명록 항목을 찾을 수 없습니다.'}), 404


# 양식 제출 라우트
@app.route('/form/submit_form', methods=['POST'])
def submit_form():
    try:
        # 기타 양식 데이터 가져오기
        data = request.form.to_dict()

        # 이미지 파일 저장 및 경로 가져오기
        saved_image_paths = []
        for i in range(3):
            file_key = f'imageFiles[{i}][file]'
            file = request.files.getlist(file_key)[0]
            if file:
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                saved_image_paths.append(file_path)

        new_form_data = FormData(
            image_files=json.dumps(saved_image_paths),
            project_name=data.get('projectName'),
            number_of_people=data.get('numberOfPeople'),
            goals=data.get('goals'),
            what_learned=data.get('whatLearned'),
            role=data.get('role'),
            your_stake=data.get('yourStake')
        )

        db.session.add(new_form_data)
        db.session.commit()

        print(f"양식 데이터가 데이터베이스에 저장되었습니다: {new_form_data}")

        # 이미지 경로를 JSON 응답으로 반환
        return jsonify({'message': '양식이 성공적으로 제출되었습니다', 'image_paths': saved_image_paths})
    except Exception as e:
        print(f"양식 제출 오류: {str(e)}")
        return jsonify({'error': '양식 제출 실패'}), 500

# 양식 가져오기 라우트
@app.route('/form/get_forms', methods=['GET'])
def get_forms():
    forms = FormData.query.all()
    form_list = []
    for form in forms:
        form_list.append({
            'id': form.id,
            'imageFiles': json.loads(form.image_files),
            'projectName': form.project_name,
            'numberOfPeople': form.number_of_people,
            'goals': form.goals,
            'whatLearned': form.what_learned,
            'role': form.role,
            'yourStake': form.your_stake,
        })

    return jsonify({'forms': form_list})

# 양식 업데이트 라우트
@app.route('/form/update_form/<int:form_id>', methods=['PUT'])
def update_form(form_id):
    try:
        # 기존 양식 데이터 가져오기
        form_data = FormData.query.get(form_id)

        if form_data:
            # 요청에서 업데이트된 양식 데이터 가져오기
            data = request.form.to_dict()

            # 텍스트 필드 업데이트
            form_data.project_name = data.get('projectName')
            form_data.number_of_people = data.get('numberOfPeople')
            form_data.goals = data.get('goals')
            form_data.what_learned = data.get('whatLearned')
            form_data.role = data.get('role')
            form_data.your_stake = data.get('yourStake')

            # 새 파일이 제공된 경우 이미지 파일 업데이트
            new_image_files = []
            for i in range(3):
                file_key = f'imageFiles[{i}][file]'
                file = request.files.get(file_key)
                if file:
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    new_image_files.append(file_path)

            # 새로운 이미지 파일 경로들을 업데이트
            form_data.image_files = json.dumps(new_image_files)

            db.session.commit()

            return jsonify({'message': '양식이 성공적으로 업데이트되었습니다'})
        else:
            return jsonify({'error': '양식을 찾을 수 없음'}), 404
    except Exception as e:
        print(f"양식 업데이트 오류: {str(e)}")
        return jsonify({'error': '양식 업데이트 실패'}), 500

# 양식 삭제 라우트
@app.route('/form/delete_form/<int:form_id>', methods=['DELETE'])
def delete_form(form_id):
    form_data = FormData.query.get(form_id)

    if form_data:
        db.session.delete(form_data)
        db.session.commit()

        return jsonify({'message': '양식이 성공적으로 삭제되었습니다'})
    else:
        return jsonify({'error': '해당 ID의 양식을 찾을 수 없습니다'}), 404



@app.route('/api/data', methods=['GET', 'POST', 'PUT'])
def handle_data():
    if request.method == 'GET':
        return get_data()
    elif request.method in ['POST', 'PUT']:
        return update_data_with_image()
    else:
        return jsonify({'message': 'Invalid request method.'}), 400


def get_data():
    try:
        data_entries = AboutMeEdit.query.all()
        data_list = [{
            'id': entry.id,
            'oneline': entry.oneline,
            'tools': entry.tools,
            'skills': entry.skills,
            'certificate': entry.certificate,
            'contact': entry.contact,
            'education': entry.education,
            'image_path': entry.image_path
        } for entry in data_entries]
        return jsonify(data_list)
    except Exception as e:
        print("Error fetching data:", str(e))
        return jsonify({'message': 'Error fetching data.'}), 500


def update_data_with_image():
    try:
        if request.method == 'OPTIONS':
            # 프리플라이트 요청에 대한 응답
            response = jsonify({'message': 'Preflight request received.'})
            response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE')
            return response
        elif request.method in ['POST', 'PUT']:
            # POST 및 PUT 요청에 대한 처리
            req_data = request.json if request.is_json else request.form

            about_me_entry = AboutMeEdit.query.get(req_data.get('id'))

            if about_me_entry:
                about_me_entry.oneline = req_data['oneline']
                about_me_entry.tools = req_data['tools']
                about_me_entry.skills = req_data['skills']
                about_me_entry.certificate = req_data['certificate']
                about_me_entry.contact = req_data['contact']
                about_me_entry.education = req_data['education']

                # Axios로 이미지 파일 업로드 및 경로 저장
                if 'image' in request.files:
                    uploaded_image = request.files['image']
                    image_path = upload_image_with_axios(uploaded_image)
                    if image_path:
                        about_me_entry.image_path = image_path

                db.session.commit()
                return jsonify({'message': 'Data updated successfully.'}), 200
            else:
                return jsonify({'message': 'Data not found.'}), 404
        else:
            return jsonify({'message': 'Invalid request method.'}), 400
    except Exception as e:
        print("Error updating data:", str(e))
        return jsonify({'message': str(e)}), 500



def upload_image_with_axios(image_file):
    try:
        # 이미지 파일을 업로드하고 서버에 저장
        filename = secure_filename(image_file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image_file.save(file_path)
        
        # 이미지 파일 경로를 반환
        return file_path
    except Exception as e:
        print("Error uploading image:", str(e))
        return None




# 애플리케이션 실행
if __name__ == '__main__':
    with app.app_context():
        # 데이터베이스 초기화
        db.create_all()
    app.run(host='0.0.0.0', port=9998, debug=True)