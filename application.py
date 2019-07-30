import config, os, csv
from flask import Flask, render_template, request, flash, redirect
from application import db
from application.models import Data
from application.forms import EnterDBInfo, RetrieveDBInfo

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, scoped_session, sessionmaker, Query

from wtforms import DateField, SubmitField, StringField, BooleanField
from wtforms.fields.html5 import DateTimeLocalField
from wtforms_components import TimeField, DateTimeField
from flask_wtf import Form
from flask_wtf.file import FileField

from werkzeug.utils import secure_filename
from werkzeug.datastructures import MultiDict

UPLOAD_FOLDER = '/home/rafa/Documents/fst/logs/uploaded'
ALLOWED_EXTENSIONS = set(['csv', 'txt'])
DBNAME = "myDatabase"
LOGSTABLE = "test2"

# Elastic Beanstalk initalization
application = Flask(__name__)
application.debug=True
application.secret_key = 'cC1YCIWOjGgWspgNEo2'  
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
connection = engine.connect()
Base = declarative_base()
Base.metadata.reflect(engine)


class Form(Form):
    #date = DateField('Date dd-mm-yyyy', format='%d-%m-%Y' )
    #time = TimeField('Time hh:mm ')
   # datetime = DateTimeLocalField('Date Time', format = '%d/%m/%y')
    #file = FileField()
    submit = SubmitField('Submit')

class Data(Base):
    __table__ = Base.metadata.tables['data']

class Logs(Base):
    __table__ = Base.metadata.tables['test2']

class Location(Base):
    __table__ = Base.metadata.tables['location']


'''
@application.route('/', methods=['GET', 'POST'])
@application.route('/index', methods=['GET', 'POST'])
def index():
    engine = create_engine('mysql+pymysql://flask:entrar123@flasktest.c8swnljwrtnx.us-east-2.rds.amazonaws.com:3306/myDatabase', pool_recycle=3600)
    q = engine.execute('SHOW TABLES')
    available_tables = q.fetchall()
    print(available_tables)

    form1 = EnterDBInfo(request.form) 
    form2 = RetrieveDBInfo(request.form) 
    
    if request.method == 'POST' and form1.validate():
        data_entered = Data(notes=form1.dbNotes.data)
        try:     
            db.session.add(data_entered)
            db.session.commit()        
            db.session.close()
        except:
            db.session.rollback()
        return render_template('thanks.html', notes=form1.dbNotes.data)
        
    if request.method == 'POST' and form2.validate():
        try:   
            num_return = int(form2.numRetrieve.data)
            query_db = Data.query.order_by(Data.id.desc()).limit(num_return)
            for q in query_db:
                print(q.notes)
            db.session.close()
        except:
            db.session.rollback()
        return render_template('results.html', results=query_db, num_return=num_return)                
    
    return render_template('index.html', form1=form1, form2=form2)
'''

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def Load_Data(filename):
    data = genfromtxt(filename)

@application.route('/', methods=['GET', 'POST'])
def index():
    #print(db.session.query('data').all())

    Session = scoped_session(sessionmaker(bind=engine))
    session = Session()
    #session._model_changes = {}

    #s2 = create_session()

    #for item in connection.execute(db.select([Data])).fetchall():
     #   print item
    
    #print(session.query(Logs).filter(Logs.id.like('1150000')).all()[0].f1)
    #print(session.execute('EXPLAIN ' + str(session.query(Logs).filter(Logs.id.like(1150000)))), {'s':'1150000'})
    #print(str(session.query(Logs).filter(Logs.id.like("?"), 1150000 )))

    #query = str(session.query(Logs).filter(Logs.id.like(1150000))) % ('123',)
    #result = session.execute('EXPLAIN ' + query).fetchone()
    #print("R2", result)


    #r = str(session.query(Logs).filter(Logs.id == 123)) %('123')
    #r2 = session.execute('EXPLAIN ' + r).fetchone()
    #print(r2)

    if request.method == 'POST':
        print("**DATE:" + request.form['date'] + "TIME**" + request.form['time'])
        print("LLLLLLLLLLLLLLLLLLLLL", request.files, 'file' in request.files)
        if 'file' not in request.files:
            print('No file part')
            return redirect(request.url)
        file = request.files['file']
        print("IF POST" + file.filename)
        if file.filename == '':
            print('No file selected for uploading')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            #contents = file.read(20)
            #print(contents)

            nextAutoIncrement = engine.execute('SELECT AUTO_INCREMENT\
                                    FROM information_schema.TABLES\
                                    WHERE TABLE_SCHEMA = "'+ DBNAME+ '"\
                                    AND TABLE_NAME = "' + LOGSTABLE + '"').fetchone()[0]

            csv_reader = csv.reader(file)
            count = 0
            buffer = []
            for row in csv_reader:
                buffer.append({
                    'f1':row[0],
                    'f2':row[1],
                    'f3':row[2],
                    'f4':row[3],
                    'f5':row[4],
                    'f6':row[5],
                    'f7':row[6],
                    'f8':row[7],
                    'f9':row[8],
                    'f10':row[9],
                    'f11':row[10],
                    'f12':row[11],
                    'f13':row[12],
                    'f14':row[13]
                    })
                if len(buffer) % 20000 == 0:
                    session.bulk_insert_mappings(Logs, buffer)
                    buffer = []

            session.bulk_insert_mappings(Logs, buffer)
            

            lastId = session.query(Logs.id).order_by(Logs.id.desc()).limit(1)
            if lastId==None: lastId=0
            print(nextAutoIncrement)
            newLocation = Location( date = request.form['date'],
                                    time = request.form['time'],
                                    first_id = nextAutoIncrement,
                                    last_id = lastId)
            session.add(newLocation)

            session.commit()
            #file.save(os.path.join(application.config['UPLOAD_FOLDER'], filename))
            print('File successfully uploaded')


            #data = Load_Data(filename) 

            return redirect('/')
        else:
            print("wrong format")
            return redirect(request.url)



    return render_template('form.html', locations=session.query(Location).all())
    #return render_template('tables.html', tables = connection.execute(db.select([Logs]).limit(10)).fetchall())


@application.route('/id=<id>/page=<page>')
def show_logs_by_id(id, page):
    Session = scoped_session(sessionmaker(bind=engine))
    session = Session()

    location = session.query(Location).filter(Location.id == id).first()
    return render_template('showLogs.html', location = location, logs=session.query(Logs).limit(25))

if __name__ == '__main__':
    application.run(host='0.0.0.0')
