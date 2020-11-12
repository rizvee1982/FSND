import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from models import setup_db, Question, Category
from flask import Flask, request, abort, jsonify
from flaskr import create_app

db = SQLAlchemy()

def setup_db(app, database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = Flask(__name__)
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        """Test _____________ """
        res = self.client().get('/categories')
        print(res)
        data = json.loads(res.data)
        print(len(data['categories']))

        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertEqual(res.status_code, 200)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()