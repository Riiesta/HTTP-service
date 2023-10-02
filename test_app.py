import unittest
import base64
import os
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
        self.assertEqual(response.status_code, 401)

        headers = {"Authorization": "Basic " + base64.b64encode("admin:password".encode()).decode()}
        response = self.client.get('/', headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_upload_file(self):
        headers = {"Authorization": "Basic " + base64.b64encode("admin:password".encode()).decode()}

        with open('some_test_file.csv', 'rb') as f:
            data = {
                'file': (f, 'some_test_file.csv')
            }
            response = self.client.post('/upload', headers=headers, content_type='multipart/form-data', data=data)
            self.assertEqual(response.status_code, 200)
            if response.status_code == 200 and os.path.exists('path_to_uploaded_files/some_test_file.csv'):
                os.remove('path_to_uploaded_files/some_test_file.csv')

    def test_delete_file(self):
        headers = {"Authorization": "Basic " + base64.b64encode("admin:password".encode()).decode()}

        file = File(filename="some_test_file.csv")
        with app.app_context():
            db.session.add(file)
            db.session.commit()

        response = self.client.delete(f'/file/{file.id}', headers=headers)
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()


