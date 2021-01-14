import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from models import setup_db, Movie, Actor
from app import create_app

auth_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InYtaTg0RmhMNDZmdGJvWXBwOHVBQiJ9.eyJpc3MiOiJodHRwczovL2Rldi11ZGlwZXdxci51cy5hdXRoMC5jb20vIiwic3ViIjoiT3pUSE5kcHoyT3RWYjJlQVN4WkdnRVBVeVU5YU50dzlAY2xpZW50cyIsImF1ZCI6ImNhc3RpbmdhZ2VuY3lhcGkiLCJpYXQiOjE2MTA1ODgyOTIsImV4cCI6MTYxMDY3NDY5MiwiYXpwIjoiT3pUSE5kcHoyT3RWYjJlQVN4WkdnRVBVeVU5YU50dzkiLCJzY29wZSI6ImdldDptb3ZpZXMgZ2V0OmFjdG9ycyBkZWxldGU6YWN0b3JzIGRlbGV0ZTptb3ZpZXMgcGF0Y2g6bW92aWVzIHBhdGNoOmFjdG9ycyBwb3N0Om1vdmllcyBwb3N0OmFjdG9ycyIsImd0eSI6ImNsaWVudC1jcmVkZW50aWFscyIsInBlcm1pc3Npb25zIjpbImdldDptb3ZpZXMiLCJnZXQ6YWN0b3JzIiwiZGVsZXRlOmFjdG9ycyIsImRlbGV0ZTptb3ZpZXMiLCJwYXRjaDptb3ZpZXMiLCJwYXRjaDphY3RvcnMiLCJwb3N0Om1vdmllcyIsInBvc3Q6YWN0b3JzIl19.ZbJMLXINU_0vkPNmlmwACATqsAXyq5sZfmDQnZfgSg7weOFvSaKNJbL-vaXjuEyp_xwNCj-8rZZOr6YlXxVzvc1PcF3WnNhmtp6tFSGaShbEg2c7FZtt8sMZrK5d6A__wSd6jO-6JjUTGl3IfHmDkjvevnqRUR51eMoIcfI2YPqV5bYVUCsWagmq58OS8BOFOGdh0wOwpVG8C9rLEYADeWoZc7J4JIKlEbLnFsGqE8WWebIPPZL3ps80vyL5Vgmk9L4t3y0-dTl3njK4mgiwOOjiXZDGaD2_p9Ai5PSXuoawINYHpuDHnBvpWnyCW3IOKxH4s1jLpKGgySDaLyZ9bQ"

class CastingagencyTestCase(unittest.TestCase):
	"""This class represents the trivia test case"""

	new_actor = {'name': 'Leo Dicaprio',
					'gender' : 'male',
					'age': 32}

	new_movie = {'title': 'Shawshank Redemption',
					'release_date': '2008-12-15'}

	actor_patch = {'name': 'Troy Sivan'}

	new_actor_err_type = {'name': 'Leo Dicaprio',
						'gender' : 'male',
						'age': 'twenty'}

	movie_patch = {'title': 'What belongs to you'}

	new_movie_err_type = {'title': 'Shawshank Redemption',
					'release_date': '2 0 O eight'}


	def setUp(self):
		"""Define test variables and initialize app."""
		self.app = create_app()
		self.client = self.app.test_client
		self.database_name = "castingagency_test"
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
	def test_get_actors(self):
		res = self.client().get('/actors', headers={"authorization": f"bearer {auth_token}"})
		print(res)
		res_json = json.loads(res.data)
		self.assertTrue(res_json['success'])
		self.assertTrue(res_json['actors'])

	def test_get_actors_param(self):
		res = self.client().get('/actors/5', headers={"authorization": f"bearer {auth_token}"})
		self.assertEqual(res.status_code, 405)

	def test_get_movies(self):
		res = self.client().get('/movies', headers={"authorization": f"bearer {auth_token}"})
		res_json = json.loads(res.data)
		self.assertTrue(res_json['success'])
		self.assertTrue(res_json['movies'])

	def test_get_movies_param(self):
		res = self.client().get('/movies/5', headers={"authorization": f"bearer {auth_token}"})
		self.assertEqual(res.status_code, 405)

	def test_delete_actor(self):
		res = self.client().delete('/actors/6', headers={"authorization": f"bearer {auth_token}"})
		res_json = json.loads(res.data)
		self.assertEqual(res.status_code, 200)
		self.assertEqual(res_json['success'], True)

	def test_delete_actor_beyond_range(self):
		res = self.client().delete('/actors/2000', headers={"authorization": f"bearer {auth_token}"})
		res_json = json.loads(res.data)
		self.assertEqual(res.status_code, 404)
		self.assertEqual(res_json['success'], False)

	def test_delete_movie(self):
		res = self.client().delete('/movies/6', headers={"authorization": f"bearer {auth_token}"})
		res_json = json.loads(res.data)
		self.assertEqual(res.status_code, 200)
		self.assertEqual(res_json['success'], True)

	def test_delete_movie_beyond_range(self):
		res = self.client().delete('/movies/2000', headers={"authorization": f"bearer {auth_token}"})
		res_json = json.loads(res.data)
		self.assertEqual(res.status_code, 404)
		self.assertEqual(res_json['success'], False)

	def test_create_actor(self):
		res = self.client().post('/actors', json=self.new_actor, headers={"authorization": f"bearer {auth_token}"})
		res_json = json.loads(res.data)
		actor = Actor.query.filter(
			Actor.name == self.new_actor['name'], 
			Actor.gender == self.new_actor['gender'],
			Actor.age == self.new_actor['age'])
		self.assertTrue(actor)
		self.assertEqual(res.status_code, 200)
		self.assertEqual(res_json['success'], True)

	def test_422_create_actor(self):
		res = self.client().post('/actors', json=self.new_actor_err_type, headers={"authorization": f"bearer {auth_token}"})
		res_json = json.loads(res.data)
		self.assertEqual(res.status_code, 422)
		self.assertEqual(res_json['success'], False) 

	def test_create_movie(self):
		res = self.client().post('/movies', json=self.new_movie, headers={"authorization": f"bearer {auth_token}"})
		res_json = json.loads(res.data)
		movie = Movie.query.filter(
			Movie.title == self.new_movie['title'], 
			Movie.release_date == self.new_movie['release_date'])
		self.assertTrue(movie)
		self.assertEqual(res.status_code, 200)
		self.assertEqual(res_json['success'], True)

	def test_422_create_movie(self):
		res = self.client().post('/movies', json=self.new_movie_err_type, headers={"authorization": f"bearer {auth_token}"})
		res_json = json.loads(res.data)
		self.assertEqual(res.status_code, 422)
		self.assertEqual(res_json['success'], False)

	def test_patch_actor(self):
		res = self.client().patch('/actors/5', json=self.actor_patch, headers={"authorization": f"bearer {auth_token}"})
		res_json = json.loads(res.data)
		self.assertEqual(res.status_code, 200)
		self.assertEqual(res_json['success'], True)

	def test_patch_actor_err(self):
		res = self.client().patch('/actors/5', json=self.new_actor_err_type, headers={"authorization": f"bearer {auth_token}"})
		res_json = json.loads(res.data)
		self.assertEqual(res.status_code, 422)
		self.assertEqual(res_json['success'], False)

	def test_patch_movie(self):
		res = self.client().patch('/movies/5', json=self.movie_patch, headers={"authorization": f"bearer {auth_token}"})
		res_json = json.loads(res.data)
		self.assertEqual(res.status_code, 200)
		self.assertEqual(res_json['success'], True)

	def test_patch_movie_err(self):
		res = self.client().patch('/movies/11', json=self.new_movie_err_type, headers={"authorization": f"bearer {auth_token}"})
		res_json = json.loads(res.data)
		self.assertEqual(res.status_code, 422)
		self.assertEqual(res_json['success'], False)

# Make the tests conveniently executable
if __name__ == "__main__":
	unittest.main()