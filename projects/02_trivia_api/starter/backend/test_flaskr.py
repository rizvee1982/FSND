import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    new_question = {'question': 'What is a test question?',
                    'answer' : 'test answer',
                    'category': 1,
                    'difficulty': 1}

    new_question_error = {'question': 'What is a bad test question?',
                        'answer' : 'One that mixes types',
                        'category': 'error',
                        'difficulty': 1}

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get('/categories')
        res_json = json.loads(res.data)
        self.assertTrue(res_json['success'])
        self.assertTrue(res_json['categories'])

    def test_get_questions(self):
        res = self.client().get('/questions?page=1')
        res_json = json.loads(res.data)
        self.assertTrue(res_json['success'])
        self.assertTrue(res_json['questions'])

    def test_get_questions_beyond_range(self):
        res = self.client().get('/questions?page=100')
        res_json = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res_json['error'], 404)
        self.assertEqual(res_json['success'], False)

    def test_get_questions_without_arg(self):
        res = self.client().get('/questions')
        res_json = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res_json['error'], 400)
        self.assertEqual(res_json['success'], False)

    # def test_delete_question(self):
    #     res = self.client().delete('/questions/3')
    #     res_json = json.loads(res.data)
    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(res_json['success'], True)

    def test_delete_question_beyond_range(self):
        res = self.client().delete('/questions/2000')
        res_json = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res_json['success'], False)

    def test_create_question(self):
        res = self.client().post('/questions', json=self.new_question)
        res_json = json.loads(res.data)
        question = Question.query.filter(Question.question == self.new_question['question'], 
                                        Question.answer == self.new_question['answer'],
                                        Question.category == self.new_question['category'],
                                        Question.difficulty == self.new_question['difficulty'])
        self.assertTrue(question)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res_json['success'], True)

    def test_422_create_question(self):
        res = self.client().post('/questions', json=self.new_question_error)
        res_json = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(res_json['success'], False)

    def test_search_questions(self):
        searchTerm = 'test'
        res = self.client().post('/questions/search', json={'searchTerm': searchTerm})
        res_json = json.loads(res.data)
        result_questions = Question.query.filter(Question.question.ilike(f'%{searchTerm}%'))
        self.assertEqual(res_json['total_questions'], result_questions.count())
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res_json['success'], True)

    def test_405_search_questions(self):
        res = self.client().delete('/questions/search', json=self.new_question_error)
        res_json = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(res_json['success'], False)

    def test_get_category_questions(self):
        res = self.client().get('/categories/1/questions')
        res_json = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res_json['questions'], True)

    def test_404_get_category_questions(self):
        res = self.client().get('/categories/100/questions')
        res_json = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res_json['success'], False)

    def test_viewQuiz(self):
        res = self.client().post('/quizzes', json={'quiz_category': {'id': 1, 'type': 'Science'}, 'previous_questions': [1, 2]})
        res_json = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res_json['success'], True)
        self.assertEqual(res_json['question']['category'], 1)

    def test_404_viewQuiz(self):
        res = self.client().post('/quizzes', json={'quiz_category': {'id': 400, 'type': 'Science'}, 'previous_questions': [1, 2]})
        res_json = json.loads(res.data)
        print(res_json['success'])
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res_json['success'], False)       

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()