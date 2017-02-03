import os

base_dir = os.path.abspath(os.path.dirname(__file__))
db_dir = os.path.join(base_dir, '../db/api_db.sqlite')
test_db_dir = os.path.join(base_dir, '../db/api_test_db.sqlite')

class _Config(object):
	SQLALCHEMY_DATABASE_URI = "sqlite:///" + db_dir
	SECRET_KEY = "CaptainGutt!"
	GOOGLE_OAUTH2_CLIENT_ID = '1008302442818-1bmf9b3q0f8oaomban7dj9q4qlgalu35.apps.googleusercontent.com'
	GOOGLE_OAUTH2_CLIENT_SECRET = 'MK_-nRMrx49vBjxLUM1_aKik'
	OAUTH_CREDENTIALS = {
	    'facebook': {
	        'id': '1745285605788389',
	        'secret': '1d7a5b8e59b055e3246fe7df879f7a1f'
	    },
	    'twitter': {
	        'id': 'KUyS6cFjPQDcqh5U7rGWzHlsu',
	        'secret': 'OehVKp8DkoMfXykLYQnsKyPrimaZVNBQ9ymEsIVkIsX0IbGaj4'
	    },
	    'google': {
	        'id': '1008302442818-1bmf9b3q0f8oaomban7dj9q4qlgalu35.apps.googleusercontent.com',
	        'secret': 'MK_-nRMrx49vBjxLUM1_aKik'
	    }
	}
	
	TESTING = False

class _TestConfig(_Config):
	SQLALCHEMY_DATABASE_URI = "sqlite:///" + test_db_dir
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	TESTING = True # Set this to True to avoid rate limit applied

class _DevelopmentConfig(_Config):
	DEBUG = True
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	SQLALCHEMY_ECHO = False

class _GaeDevelopmentMigrationConfig(_Config):
	DEBUG = False

class _GaeDevelopmentConfig(_Config):
	DEBUG = False

_configs = {
	'test': _TestConfig,
	'development': _DevelopmentConfig,
	'gae_development': _GaeDevelopmentConfig,
	'gae_development_migration': _GaeDevelopmentMigrationConfig
}

config = _configs[os.getenv('ENVIRONMENT', 'development')]