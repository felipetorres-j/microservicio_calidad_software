""" Knasta Script MicroServices-Favorites """
from datetime import datetime
import os
import logging
from flask import Flask, request
import pytz
from flask_restplus import Resource, Api, reqparse, fields
from flask_cors import CORS
from settings import *
import psycopg2.extras
import psycopg2

logging.basicConfig(level=logging.DEBUG)

HTTP_CODE_OK = 200
HTTP_CODE_CREATED = 201
HTTP_CODE_ERROR = 500

# App create and config
application = Flask(__name__)

CORS(application)
TIMEZONE = 'America/Santiago'
TODAY = lambda: datetime.now(pytz.timezone(TIMEZONE)).strftime('%Y-%m-%d %H:%M:%S')

POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASS = os.getenv('POSTGRES_PASS')
POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_DB = os.getenv('POSTGRES_DB')

api_config = {
    'title': 'Microservicio de ejemplo',
    'default': 'Cursos API',
    'default_label': 'manage/query the user\'s favorites products',
    'description': 'Microservice that manage/query the user\'s favorites products'
}

api = Api(application, **api_config)

parser = reqparse.RequestParser()

parser_collection = reqparse.RequestParser()
parser_collection.add_argument('user_id', type=str, required=True, help='The id of the user')

FAVORITE_BODY = api.model('Favorite', {
    'id': fields.String(required=True, description='id of the user'),
    'name': fields.String(required=True, description='id of the user'),
    'profesor': fields.String(required=True, description='retail to product'),
})

DELETE_BODY = api.model('Delete favorite', {
    'user_id': fields.String(required=True, description='id of the user'),
    'kid': fields.String(description='the retail#sku/id', required=True),
    'collection_id': fields.Integer(description='the collection of product created', required=True)
})

COLLECTION_BODY = api.model('Collection', {
    'user_id': fields.String(required=True, description='id of the user'),
    'name': fields.String(description='name of collection', required=True),
    'description': fields.String(description='collection description', required=True)
})

def get_response(status_bool, method):
    """ Evaluate status of method """
    if status_bool and method == 'GET':
        return HTTP_CODE_OK
    if status_bool and (method in ['POST', 'PUT', 'DELETE']):
        return {"Status": "Done"}, HTTP_CODE_CREATED
    return {"Status": "Error"}, HTTP_CODE_ERROR


def get_country():
    """ Get country of url """
    country = request.host.split(':')[0].split('.')[-1]
    return country

def get_conn():
    """Get connection with database"""
    connect = psycopg2.connect(host=POSTGRES_HOST,
                               dbname=POSTGRES_DB,
                               user=POSTGRES_USER,
                               password=POSTGRES_PASS)
    return connect

def get_cursor(conn, country):
    """Connect to db and configure proper search_path"""
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    return cursor

def insert_curso(args, country):
    """Insert favorites into DB"""
    conn = get_conn()
    cursor = get_cursor(conn, country)
    try:
        cursor.execute(
            '''
            SELECT insert_curso(
                '{id}'::TEXT,
                '{name}'::TEXT,
                '{profesor}'::TEXT,
                '{created_at}'::TIMESTAMP WITH TIME ZONE
            )
            '''.format(**args)
        )
        logging.info("1 row inserted into CURSO")
        conn.commit()
        return True
    except Exception as error:
        logging.error(error)
        return False

def delete_favorite(args, country):
    """Delete favorite from favorites_db"""
    conn = get_conn()
    cursor = get_cursor(conn, country)
    try:
        cursor.execute(
            '''
            SELECT deleted_favorite(
                '{kid}'::TEXT,
                '{user_id}'::TEXT,
                {collection_id}::INTEGER
            )
            '''.format(**args)
        )
        logging.info("1 row deleted from FAVORITES")
        conn.commit()
        return True
    except Exception as error:
        logging.error(error)
        return False

def get_favorites():
    """Get favorites from db"""
    query = "SELECT * FROM select_cursos()"
    cursor = get_cursor(get_conn(), 'cl')
    try:
        cursor.execute(query)
    except Exception as error:
        logging.error(error)
        return False

    favorites = cursor.fetchall()

    return favorites, True

def get_collection(user_id, country):
    """Get collections from db"""
    query = "SELECT * FROM select_collection('{}'::TEXT)".format(user_id)
    cursor = get_cursor(get_conn(), country)
    try:
        cursor.execute(query)
    except Exception as error:
        logging.error(error)
        return False

    collections = cursor.fetchall()
    return collections, True


@api.route('/favorite/')
class Favorite(Resource):
    """ Class to insert and delete favorites """
    @api.expect(FAVORITE_BODY)
    @api.doc(description='Add user\'s favorite')

    def post(self):
        """ Method insert favorite into DB """
        country = get_country()
        val = {
            'id': api.payload.get('id'),
            'name': api.payload.get('name'),
            'profesor': api.payload.get('profesor'),
            'created_at': TODAY()
        }

        return get_response(insert_curso(val, country), 'POST')

    @api.expect(DELETE_BODY)
    @api.doc(description='Delete a user\'s favorite')
    def delete(self):
        """ Method delete favorite with kid, user_id and collection_id """
        country = get_country()
        val = {
            'id': api.payload.get('id'),
        }

        return get_response(delete_favorite(val, country), 'DELETE')

    @api.doc(description='Chrome does not allow to use DELETE verb if OPTIONS is not implemented')
    def options(self):
        return {}


@api.route('/favorites/')
class FavoriteList(Resource):
    """ Class to get favorite list"""
    @api.doc(parser=parser, description='Get all user\'s favorites')
    def get(self):
        """ Method get all favorites with user_id """
        country = get_country()
        args = parser.parse_args()
        list_favorites, status_bool = get_favorites()
        return list_favorites, get_response(status_bool, 'GET')
        #TODO: Add index for user_id on favorites collection (speed purposes)



if __name__ == "__main__":
    application.run(host='0.0.0.0')
