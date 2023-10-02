from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import os
import csv
import chardet
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///files.db'
db = SQLAlchemy(app)
auth = HTTPBasicAuth()

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(150), unique=True, nullable=False)
    columns = db.Column(db.String(500), nullable=False)

@auth.verify_password
def verify_password(username, password):
    return username == 'admin' and password == 'password'

@app.route('/', methods=['GET'])
@auth.login_required
def home():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
@auth.login_required
def upload_file():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            filepath = os.path.join('uploads', uploaded_file.filename)
            if not os.path.exists('uploads'):
                os.makedirs('uploads')
            uploaded_file.save(filepath)

            delimiter = detect_delimiter(filepath)
            encoding = detect_encoding(filepath)
            data = pd.read_csv(filepath, delimiter=delimiter, encoding=encoding)  # Используйте переменную encoding

            columns = ",".join(data.columns.tolist())
            file_record = File(filename=uploaded_file.filename, columns=columns)
            db.session.add(file_record)
            db.session.commit()
            return jsonify({'message': 'File uploaded successfully', 'file_id': file_record.id})
        else:
            return jsonify({'error': 'No file uploaded'}), 400
    return render_template('upload.html')

@app.route('/file/<int:file_id>', methods=['DELETE'])
@auth.login_required
def delete_file(file_id):
    file = File.query.get_or_404(file_id)

    filepath = os.path.join('uploads', file.filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    else:
        return jsonify({'error': 'File not found on disk'}), 404

    db.session.delete(file)
    db.session.commit()

    return jsonify({'message': 'File deleted successfully'}), 200


@app.route('/files', methods=['GET'])
@auth.login_required
def list_files():
    files = File.query.all()
    files_list = [{'id': file.id, 'filename': file.filename, 'columns': file.columns.split(',')} for file in files]
    return jsonify(files_list)

@app.route('/data/<int:file_id>', methods=['GET'])
@auth.login_required
def get_data(file_id):
    file = File.query.get_or_404(file_id)
    filepath = os.path.join('uploads', file.filename)
    data = pd.read_csv(filepath)
    return data.to_json(orient='records')

def detect_encoding(file_path):
    with open(file_path, 'rb') as file:
        result = chardet.detect(file.read())
    return result['encoding']

def detect_delimiter(file_path):
    with open(file_path, 'r', encoding='cp1251', errors='replace') as file:
        sniffer = csv.Sniffer()
        delimiter = sniffer.sniff(file.read(1024)).delimiter
    return delimiter

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)



