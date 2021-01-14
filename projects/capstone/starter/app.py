import os
import sys
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import setup_db, Movie, Actor
from auth import AuthError, requires_auth
from sqlalchemy.exc import DataError

def create_app(test_config=None):
  # create and configure the app
	app = Flask(__name__)
	CORS(app)
	
	@app.route('/movies')
	@requires_auth('get:movies')
	def get_movies(payload):
	    try: 
	        movies = Movie.query.all()
	        movie_list = []
	        for movie in movies:
	            movie_list.append(movie.format())
	        return jsonify({'success': True, "movies": movie_list}), 200
	    except:
	    	abort(422)

	@app.route('/actors')
	@requires_auth('get:actors')
	def get_actors(payload):
	    try: 
	        actors = Actor.query.all()
	        actor_list = []
	        for actor in actors:
	            actor_list.append(actor.format())
	        return jsonify({'success': True, "actors": actor_list}), 200
	    except:
	    	abort(422)

	@app.route('/movies/<int:movie_id>', methods=['DELETE'])
	@requires_auth('delete:movies')
	def delete_movie(payload, movie_id):
		movie = Movie.query.get(movie_id)
		if movie is None:
			abort(404)		
		else:
			movie.delete()
			return jsonify({'success': True}), 200

	@app.route('/actors/<int:actor_id>', methods=['DELETE'])
	@requires_auth('delete:actors')
	def delete_actor(payload, actor_id):
		actor = Actor.query.get(actor_id)
		if actor is None:
			abort(404)		
		else:
			actor.delete()
			return jsonify({'success': True}), 200


	@app.route('/actors', methods=['POST'])
	@requires_auth('post:actors')
	def create_actor(payload):
		try:
			request_json = request.get_json()
			age = request_json.get('age')
			gender = request_json.get('gender')
			name = request_json.get('name')
			if None in (age, gender, name):
				abort(400)
			actor = Actor(name=name, gender=gender, age=age)
			actor.insert()
			return jsonify({'success': True, 'actor': actor.format()}), 200
		except DataError:
			abort(422)


	@app.route('/movies', methods=['POST'])
	@requires_auth('post:movies')
	def create_movie(payload):
		try: 
			request_json = request.get_json()
			title = request_json.get('title')
			release_date = request_json.get('release_date')
			if None in (title, release_date):
				abort(400)
			movie = Movie(title=title, release_date=release_date)
			movie.insert()
			return jsonify({'success': True, 'movie': movie.format()}), 200
		except DataError:
			abort(422)


	@app.route('/movies/<int:movie_id>', methods=['PATCH'])
	@requires_auth('patch:movies')
	def update_movie(payload, movie_id):
		try:
			request_json = request.get_json()
			movie = Movie.query.get(movie_id)
			if movie is None:
				abort(404)
			
			# If there are attributes sent that are not related to the resource
			if not set(request_json.keys()).issubset(['title', 'release_date']):
				abort(400)

			if request_json.get('title') is not None:
				movie.title = request_json.get('title')

			if request_json.get('release_date') is not None:
				movie.release_date = request_json.get('release_date')

			movie.update()
			return jsonify({'success': True, 'movie': movie.format()}), 200
		except DataError as e:
			abort(422)


	@app.route('/actors/<int:actor_id>', methods=['PATCH'])
	@requires_auth('patch:actors')
	def update_actor(payload, actor_id):
		try:
			request_json = request.get_json()
			actor = Actor.query.get(actor_id)
			# If the actor id does not have a corresponding resource  
			if actor is None:
				abort(404)
			# If there are attributes sent that are not related to the resource
			if not set(request_json.keys()).issubset(['name', 'gender', 'age']):
				abort(400)
			
			if request_json.get('name') is not None:
				actor.name = request_json.get('name')

			if request_json.get('age') is not None:
				actor.age = request_json.get('age')

			if request_json.get('gender') is not None: 
				actor.gender = request_json.get('gender')
			actor.update()
			return jsonify({'success': True, 'movie': actor.format()}), 200
		except DataError:
			abort(422)


	@app.errorhandler(422)
	def unprocessable(error):
	    return jsonify({
	                    "success": False, 
	                    "error": 422,
	                    "message": "unprocessable"
	                    }), 422

	@app.errorhandler(400)
	def badreqest(error):
	    return jsonify({
	                    "success": False, 
	                    "error": 400,
	                    "message": "bad request"
	                    }), 400

	@app.errorhandler(404)
	def not_found(error):
	    return jsonify({
	                    "success": False, 
	                    "error": 404,
	                    "message": "Resource not found."
	                    }), 404

	@app.errorhandler(AuthError)
	def handle_auth_error(ex):
	    response = jsonify(ex.error)
	    response.status_code = ex.status_code
	    return response
	
	return app

app = create_app()
setup_db(app)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)