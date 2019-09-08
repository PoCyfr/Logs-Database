import config, os, csv, math, sys, tempfile, shutil, logging
from os import listdir
from flask import Flask, render_template, request, flash, redirect, url_for, Blueprint, current_app
from flask_paginate import Pagination, get_page_parameter, get_page_args
from application import db
from application.models import Data
from application.forms import EnterDBInfo, RetrieveDBInfo

from sqlalchemy import create_engine, Column, Integer, String, and_
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
LOGSPERPAGE =  100

# Elastic Beanstalk initalization
application = Flask(__name__)
application.debug=True
application.secret_key = 'cC1YCIWOjGgWspgNEo2'  
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
mod = Blueprint(LOGSTABLE, __name__)
#tlogs=None

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

class Logs(db.Model):
    __table__ = Base.metadata.tables[LOGSTABLE]

class Location(Base):
    __table__ = Base.metadata.tables['location']

print Logs.__table__.name
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

    print engine.execute('SELECT @@global.local_infile').fetchone()
    print engine.execute("SHOW VARIABLES LIKE 'local_infile'").fetchone()

    Session = scoped_session(sessionmaker(bind=engine))
    session = Session()
    #session._model_changes = {}

    #global tlogs
    #tlogs = None
    #print tlogs
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
            #with MeasureDuration() as m:

            #get next id to be inserted
            nextAutoIncrement = engine.execute('SELECT AUTO_INCREMENT\
                                    FROM information_schema.TABLES\
                                    WHERE TABLE_SCHEMA = "'+ DBNAME+ '"\
                                    AND TABLE_NAME = "' + LOGSTABLE + '"').fetchone()[0]

            '''
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
                '''

                
            
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, filename)

            print temp_dir, temp_path
            logging.warning("#########################################################")
            logging.warning(temp_dir)
            logging.warning(temp_path)

            #Copy file to temp probably
            file.save(temp_path)

            files = os.listdir("/tmp")
            for i in files:
                logging.warning(i)

            #Upload file from temp to database
            '''
            engine.execute('LOAD DATA LOCAL INFILE "' + temp_path+'"\
                            INTO TABLE ' + LOGSTABLE + '\
                            FIELDS TERMINATED BY \',\'\
                            ENCLOSED BY \'\"\'\
                            LINES TERMINATED BY \'\\n\'')
            '''
            print engine.execute('SELECT @@global.local_infile').fetchone()
            print engine.execute("SHOW VARIABLES LIKE 'local_infile'").fetchone()
            sql='LOAD DATA LOCAL INFILE "' + temp_path+'"\
                            INTO TABLE ' + LOGSTABLE + '\
                            FIELDS TERMINATED BY \',\'\
                            ENCLOSED BY \'\"\'\
                            LINES TERMINATED BY \'\\n\'\
                            (f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13,f14)'

            print sql
            engine.execute(sql)
            '''
            files = os.listdir(os.path.dirname(os.path.abspath(__file__)))
            for i in files:
                logging.warning(i)
            #file.save(os.path.join('/tmp', filename))

            logging.warning("#########################################################")

            files = os.listdir("/tmp")
            for i in files:
                logging.warning(i)
            '''

            lastId = session.query(Logs.id).order_by(Logs.id.desc()).limit(1)
            if lastId==None: lastId=0
            print("AUTO INC: " + str(nextAutoIncrement))
            newLocation = Location( date = request.form['date'],
                                    time = request.form['time'],
                                    first_id = nextAutoIncrement,
                                    last_id = lastId)
            session.add(newLocation)

            session.commit()
            os.remove(temp_path)
            #data = Load_Data(filename) 

            return redirect('/')
        else:
            print("wrong format")
            return redirect(request.url)


    #######
    
    #######



    return render_template('form.html', locations=session.query(Location).all(),
                                        )
    #return render_template('tables.html', tables = connection.execute(db.select([Logs]).limit(10)).fetchall())


@application.route('/id:<id>/')
def show_logs_by_id(id):

    Session = scoped_session(sessionmaker(bind=engine))
    session = Session()

    location = session.query(Location).filter(Location.id == id).first()

    totalLogs = int(location.last_id-location.first_id+1)
    print("Tot",totalLogs)

    '''
    with MeasureDuration() as m:

        logs = Logs.query.filter(and_(Logs.id <= location.last_id, Logs.id >= location.first_id))
        pageLogs = logs.paginate(page, logsPerPage, False)
        pagination = Pagination(page=page,
                                per_page=logsPerPage, 
                                total=totalLogs, 
                                
                                record_name='RECORD_NAME',
                                )
    
        if(pageLogs.has_next):
        nextUrl = url_for('show_logs_by_id', id = id, page=pageLogs.next_num)
    else: nextUrl = None

    if(pageLogs.has_prev):
        prevUrl = url_for('show_logs_by_id', id = id, page=pageLogs.prev_num)
    else: prevUrl = None

    return render_template('showLogs.html', location = location,
                                            logs=pageLogs.items,
                                            nu=nextUrl,
                                            pu=prevUrl,
                                            pagination=pagination,)


    '''
    page=int(request.args.get('page', 1))
    per_page = LOGSPERPAGE
    offset = (page-1)*per_page
    print page
    print per_page
    print offset
    #logs = Logs.query.filter(and_(Logs.id <= location.last_id, Logs.id >= location.first_id)).offset(offset).limit(per_page)
    if location.last_id < offset+per_page+location.first_id:
        last=location.last_id+1
    else:
        last=offset+per_page+location.first_id

    print last
    print offset+location.first_id
    logs = Logs.query.filter(and_(Logs.id < last, Logs.id >= offset+location.first_id)).all()
    #print logs

    pagination = Pagination(page=page,
                            per_page=per_page,
                            offset=offset,
                            total=totalLogs,
                            record_name='logs',
                            format_total=False,
                            format_number=True,
                            bs_version=4,
                            )


    return render_template('showLogs.html', location = location,
                                        logs = logs,
                                        pagination=pagination,
                                        )

##################
import time
class MeasureDuration:
    def __init__(self):
        self.start = None
        self.end = None
 
    def __enter__(self):
        self.start = time.time()
        return self
 
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end = time.time()
        print "Total time taken: %s" % self.duration()

    def duration(self):
        return str((self.end - self.start) * 1000) + ' milliseconds'
 
####################



@application.route('/id:<id>/page:<page>')
def show(id):
    print ok



if __name__ == '__main__':
    application.run(host='0.0.0.0')




