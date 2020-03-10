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
    'default_label': 'ejemplo de microservicio con api cursos',
    'description': 'id del curso con su nombre y profesor'
}

api = Api(application, **api_config)

parser = reqparse.RequestParser()


FAVORITE_BODY = api.model('Favorite', {
    'id': fields.String(required=True, description='id del curso'),
    'name': fields.String(required=True, description='nombre del curso'),
    'profesor': fields.String(required=True, description='nombre del profesor'),
})

DELETE_BODY = api.model('Delete favorite', {
    'id': fields.String(required=True, description='id del curso'),
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

def get_cursor(conn):
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

def delete_favorite(args):
    """Delete favorite from cursos_db"""
    conn = get_conn()
    cursor = get_cursor(conn)
    try:
        cursor.execute(
            '''
            SELECT deleted_curso(
                '{id}'::TEXT
            )
            '''.format(**args)
        )
        logging.info("1 row deleted from Curso")
        conn.commit()
        return True
    except Exception as error:
        logging.error(error)
        return False

def get_cursos():
    """Get cursos from db"""
    query = "SELECT * FROM select_cursos()"
    cursor = get_cursor(get_conn(), 'cl')
    try:
        cursor.execute(query)
    except Exception as error:
        logging.error(error)
        return False

    favorites = cursor.fetchall()

    return favorites, True

@api.route('/curso/')
class Favorite(Resource):
    """ Class to insert and delete cursos """
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
    @api.doc(description='Delete curso')
    def delete(self):
        """ Method delete favorite with id"""
        country = get_country()
        val = {
            'id': api.payload.get('id'),
        }

        return get_response(delete_curso(val, country), 'DELETE')

    @api.doc(description='Chrome does not allow to use DELETE verb if OPTIONS is not implemented')
    def options(self):
        return {}


@api.route('/cursos/')
class FavoriteList(Resource):
    """ Class to get curso list"""
    @api.doc(parser=parser, description='obtenemos todos los cursos cursos')
    def get(self):
        """ Method get all cursos with user_id """
        country = get_country()
        args = parser.parse_args()
        list_favorites, status_bool = get_cursos()
        return list_favorites, get_response(status_bool, 'GET')
        #TODO: Add index for user_id on favorites collection (speed purposes)



if __name__ == "__main__":
    application.run(host='0.0.0.0')
