from flask import Flask
from flask_restful import Resource, Api
from flask_restful import reqparse
from flaskext.mysql import MySQL
from flask import request

from config import Config


config = Config()
mysql = MySQL()
app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = config.db_username
app.config['MYSQL_DATABASE_PASSWORD'] = config.db_password
app.config['MYSQL_DATABASE_DB'] = config.db_databaseName
app.config['MYSQL_DATABASE_HOST'] = config.db_hostname
app.config['MYSQL_DATABASE_PORT'] = config.db_port


mysql.init_app(app)

api = Api(app)


class EventLogger(Resource):
    def post(self):
        try:
            print request.method
            if request.method == 'POST':
                if len(request.data)>0:
                    conn = mysql.connect()
                    cursor = conn.cursor()
                    cursor.callproc('sp_insertEvent',(request.data,))
                    data = cursor.fetchall()
                    conn.commit()
                    return {'StatusCode':'200','Message': 'Success'}
                else:
                    return {'error': 'Blank data found.'}
            else:
                return {'error': 'Unsupported Method found. Only POST method allowed.'}
        except Exception as e:
            return {'error': str(e)}

api.add_resource(EventLogger, '/AddEventLog')

if __name__ == '__main__':
    app.run(debug=True)
