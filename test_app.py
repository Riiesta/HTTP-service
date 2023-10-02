import unittest
import base64
import os
# Assuming import test_app is necessary
import test_app
from main import app, db, File

class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_files.db'
        self.client = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_authorization(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 401)  # Expect unauthorized

        headers = {"Authorization": "Basic " + base64.b64encode("admin:password".encode()).decode()}
        response = self.client.get('/', headers=headers)
        self.assertEqual(response.status_code, 200)  # Expect success

    def test_upload_file(self):
        headers = {"Authorization": "Basic " + base64.b64encode("admin:password".encode()).decode()}

        with open('some_test_file.csv', 'rb') as f:
            data = {
                'file': (f, 'some_test_file.csv')
            }
            response = self.client.post('/upload', headers=headers, content_type='multipart/form-data', data=data)
            self.assertEqual(response.status_code, 200)  # Expect success
            # Optionally, cleanup the uploaded file if it gets saved on disk.
            if response.status_code == 200 and os.path.exists('path_to_uploaded_files/some_test_file.csv'):
                os.remove('path_to_uploaded_files/some_test_file.csv')

    def test_delete_file(self):
        headers = {"Authorization": "Basic " + base64.b64encode("admin:password".encode()).decode()}

        # Better approach would be to create a file here and delete that file, ensuring the file existence.
        file = File(filename="some_test_file.csv")  # Assuming File is the model representing the file.
        with app.app_context():
            db.session.add(file)
            db.session.commit()

        response = self.client.delete(f'/file/{file.id}', headers=headers)
        self.assertEqual(response.status_code, 200)  # Expect success


if __name__ == '__main__':
    unittest.main()


