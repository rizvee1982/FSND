import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, abort, jsonify
from models import setup_db, Question, Category

database_name = "trivia_test"
database_path = "postgres://{}/{}".format('localhost:5432', database_name)

class TriviaTestCase(unittest.TestCase):
    """This class represents the resource test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        setup_db(self.app, self.database_path)
    
    def tearDown(self):
        """Executed after each test"""
        pass

    def test_get_categories(self):
        """Test _____________ """
        res = self.client().get('/categories')
        data = json.loads(res.data)
        print(len(data['categories']))

        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertEqual(res.status_code, 200)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()