import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import random
import sys
import math


from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  DONE
  '''

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  DONE
  '''
  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
      return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  @cross_origin()
  def get_categories():
    categories = Category.query.all()
    categoryArray = []
    for category in categories:
      categoryArray.append(category.type)
    print(jsonify({'categories': categoryArray, 'success': True}))
    return jsonify({'categories': categoryArray, 'success': True})
      


  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  def get_page_questions(page, questions):
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE 
    questions = [question.format() for question in questions]
    return questions[start:end]

  @app.route('/questions')
  @cross_origin()
  def get_questions():
    page = request.args.get('page')
    if page is None:
      abort(400)
    categories = Category.query.all()
    current_questions = []
    categoryArray = []
    for category in categories:
      categoryArray.append(category.type)
    questions = Question.query.all()
    if int(page) > math.ceil(len(questions)/QUESTIONS_PER_PAGE):
      abort(404)
    current_questions = get_page_questions(int(page), questions)
    print(jsonify({'questions': current_questions,
                  'total_questions': len(questions),
                  'categories': categoryArray,
                  'current_category': categoryArray[0],
                  'success': True }))
    return jsonify({'questions': current_questions,
                  'total_questions': len(questions),
                  'categories': categoryArray,
                  'current_category': categoryArray[0],
                  'success': True })

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 

  Testing: Done 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  @cross_origin()
  def delete_questions(question_id):
    question = Question.query.get(question_id)
    print(question_id)
    print(question)
    if question is None:
      abort(404)
    else:
      question.delete()
      return jsonify({'success': True})



  '''
  @TODO: 

  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  

  Testing (Done)
  '''

  @app.route('/questions', methods=['POST'])
  @cross_origin()
  def create_question():
    try:
      request_json = request.get_json()
      category = request_json.get('category', '')
      difficulty = request_json.get('difficulty', '')
      question_text = request_json.get('question', '')
      answer = request_json.get('answer', '')
      question = Question(question=question_text, answer=answer, category=category, difficulty = difficulty)
      result = question.insert()
      return jsonify({'success':True})
    except Exception as e:
      abort(422)
      

  '''
  @TODO: 


  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  @app.route('/questions/search', methods=['POST'])
  @cross_origin()
  def search_questions():
    request_json = request.get_json()
    searchTerm = request_json.get('searchTerm','')
    questions = Question.query.filter(Question.question.ilike(f'%{searchTerm}%'))
    questionArray = []
    questionArray = [question.format() for question in questions]
    success = True 
    return jsonify({'questions' : questionArray,
                    'total_questions' : len(questionArray),
                    'current_category' : 0,
                    'success' : success})
  
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions')
  @cross_origin()
  def get_category_questions(category_id):
    if Category.query.get(category_id) is None:
      abort(404)
    else: 
      questions = Question.query.filter(Question.category == category_id)
      questionArray = []
      questionArray = [question.format() for question in questions]
      success = True 
      return jsonify({'questions' : questionArray,
                      'total_questions' : len(questionArray),
                      'current_category' : category_id,
                      'success' : success})


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

  @app.route('/quizzes', methods=['POST'])
  @cross_origin()
  def viewQuiz():
    request_json = request.get_json()
    previous_questions = request_json.get('previous_questions','')
    quiz_category = request_json.get('quiz_category','')

    if quiz_category['type'] == 'click':
      questions = Question.query.filter(~Question.id.in_(previous_questions)).all()
    elif Question.query.filter(Question.category==quiz_category['id']).count() == 0:
      abort(404)
    else:
      questions = Question.query.filter(Question.category == int(quiz_category['id'])).filter(~Question.id.in_(previous_questions)).all()

    if len(questions)==0:
      return jsonify({'success' : True})
    else:
      question = random.choice(questions)
      return jsonify({'question' : question.format(),
                      'success' : True})


  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False, 
      "error": 404,
      "message": "resource not found"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "unprocessable"
      }), 422

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False, 
      "error": 400,
      "message": "bad request"
      }), 400

  @app.errorhandler(405)
  def bad_request(error):
    return jsonify({
      "success": False, 
      "error": 405,
      "message": "method not allowed"
      }), 405
  
  @app.errorhandler(500)
  def bad_request(error):
    return jsonify({
      "success": False, 
      "error": 500,
      "message": "server error"
      }), 500
  
  return app

    