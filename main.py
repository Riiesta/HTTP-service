# main.py
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///files.db'
db = SQLAlchemy(app)

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(150), unique=True, nullable=False)
    columns = db.Column(db.String(500), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/upload', methods=['POST'])
def upload_file():
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        filepath = os.path.join('uploads', uploaded_file.filename)
        uploaded_file.save(filepath)
        data = pd.read_csv(filepath)
        columns = ",".join(data.columns.tolist())
        file_record = File(filename=uploaded_file.filename, columns=columns)
        db.session.add(file_record)
        db.session.commit()
        return jsonify({'message': 'File uploaded successfully', 'file_id': file_record.id})
    else:
        return jsonify({'error': 'No file uploaded'}), 400

@app.route('/files', methods=['GET'])
def list_files():
    files = File.query.all()
    files_list = [{'id': file.id, 'filename': file.filename, 'columns': file.columns.split(',')} for file in files]
    return jsonify(files_list)

@app.route('/data/<int:file_id>', methods=['GET'])
def get_data(file_id):
    file = File.query.get_or_404(file_id)
    filepath = os.path.join('uploads', file.filename)
    data = pd.read_csv(filepath)

    # Фильтрация и сортировка данных (опционально)
    # ...

    return data.to_json(orient='records')

if __name__ == '__main__':
    app.run(debug=True)

