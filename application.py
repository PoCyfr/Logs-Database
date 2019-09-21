import config, os, csv, math, sys, tempfile, shutil, logging, sys
from os import listdir
from flask import Flask, render_template, request, flash, redirect, url_for, Blueprint, current_app, Response, send_from_directory
from flask_paginate import Pagination, get_page_parameter, get_page_args
from application import db

from sqlalchemy import create_engine, Column, Integer, String, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, scoped_session, sessionmaker, Query
from sqlalchemy.pool import NullPool

from wtforms import DateField, SubmitField, StringField, BooleanField
from wtforms.fields.html5 import DateTimeLocalField
from wtforms_components import TimeField, DateTimeField
from flask_wtf import Form
from flask_wtf.file import FileField

from werkzeug.utils import secure_filename
from werkzeug.datastructures import MultiDict

from datetime import datetime, timedelta, date, time
import datetime as dt


ALLOWED_EXTENSIONS = set(['csv', 'txt'])
LOGSPERPAGE =  100
#DBNAME = "myDatabase"
#LOCATIONTABLE = "location"
#LOGSTABLE = "data"

application = Flask(__name__)
application.debug=True
application.secret_key = 'cC1YCIWOjGgWspgNEo2'  
mod = Blueprint(config.LOGSTABLE, __name__)

engine = create_engine(config.SQLALCHEMY_DATABASE_URI, poolclass=NullPool)
connection = engine.connect()
Base = declarative_base()
Base.metadata.reflect(engine)

#Models
class Logs(db.Model):
    __table__ = Base.metadata.tables[config.LOGSTABLE]

    def m_id(self):
        return self.f3>>5

    def d_id(self):
        return self.f3 & 31
    
class Location(db.Model):
    __table__ = Base.metadata.tables[config.LOCATIONTABLE]



def close():
    connection.close()
    engine.dispose()

def allowed_file(filename):
    #Tests if file extension is allowed
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@application.route('/', methods=['GET', 'POST'])
def index():
    Session = scoped_session(sessionmaker(bind=engine))
    session = Session()

    #loc = session.query(Location).filter(Location.id==1).first()
    #allLogsInserted = session.query(Logs).filter(and_(Logs.id <= loc.last_id, Logs.id >= loc.first_id))

    if request.method == 'POST':
        if 'file' not in request.files:
            print('No file part')
            #session.close()
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            print('No file selected for uploading')
           # session.close()
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            name = request.form['name']
            time = request.form['time']
            date = request.form['date']
            tags = request.form['tags']
            car = request.form['car']

            #gets start_id
            nextAutoIncrement = engine.execute('SELECT AUTO_INCREMENT\
                                    FROM information_schema.TABLES\
                                    WHERE TABLE_SCHEMA = "'+ config.DBNAME+ '"\
                                    AND TABLE_NAME = "' + config.LOGSTABLE + '"').fetchone()[0]

            
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, filename)

            #Copy file to /tmp/
            file.save(temp_path)          

            #Uploads file
            sql='LOAD DATA LOCAL INFILE "' + temp_path+'"\
                INTO TABLE ' + config.LOGSTABLE + '\
                FIELDS TERMINATED BY \',\'\
                ENCLOSED BY \'\"\'\
                LINES TERMINATED BY \'\\n\'\
                (f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13,f14)'
            print(sql)
            engine.execute(sql)

            lastId = session.query(Logs.id).order_by(Logs.id.desc()).limit(1)
            if lastId==None: lastId=0
            
            newLocation = Location( name = name,
                                    date = date,
                                    time = time,
                                    first_id = nextAutoIncrement,
                                    last_id = lastId,
                                    tag = tags,
                                    car = car)
            
            session.add(newLocation)
            session.commit()

            session.close()
            close()
            
            os.remove(temp_path)
            #data = Load_Data(filename) 

            return redirect('/')
        else:
            print("wrong format")
            session.close()
            close()
            return redirect(request.url)

    location =session.query(Location).all()
    
    session.close()
    close()

    #close(engine)
    return render_template('form.html', locations=location)
    
    return redirect('asd')
    #return render_template('tables.html', tables = connection.execute(db.select([Logs]).limit(10)).fetchall())


@application.route('/id:<id>/', methods=['GET', 'POST'])
def show_logs_by_id(id):
    Session = scoped_session(sessionmaker(bind=engine))
    session = Session()

    location = session.query(Location).filter(Location.id == id).first()
    totalLogs = int(location.last_id-location.first_id+1)
    print("Tot",totalLogs)

    page=int(request.args.get('page', 1))
    offset = (page-1)*LOGSPERPAGE
    
    #Finds id of last log line
    if location.last_id < offset+LOGSPERPAGE+location.first_id:
        last=location.last_id+1
    else:
        last=offset+LOGSPERPAGE+location.first_id

    
    logs = Logs.query.filter(and_(Logs.id < last, Logs.id >= offset+location.first_id)).all()

    conv = None
    if request.method == 'POST':
        dev = request.form['dev id']
        msg = request.form['msg id']
        conv = (int(msg)<<5) + int(dev)
    
   

    pagination = Pagination(page=page,
                            per_page=LOGSPERPAGE,
                            offset=offset,
                            total=totalLogs,
                            record_name='logs',
                            format_total=False,
                            format_number=True,
                            bs_version=4,
                            )

    session.close()
    close()
    return render_template('showLogs.html', location = location,
                                        logs = logs,
                                        pagination=pagination,
                                        conv = conv,
                                        )


@application.route('/id:<id>/convertID', methods=['GET', 'POST'])
def conv():
    redirect(url_for('show_logs_by_id', ))



@application.route('/searchid:<id>/', methods=['GET', 'POST'])
def redirectToSearch(id):
    '''
    this function is needed because the url where the pagination happens cannot receive get or post
    '''
    search = request.form['search']
    return redirect(url_for('searchId', id=id, search = search))



@application.route('/id:<id>/search:<search>')
def searchId(id, search):
    Session = scoped_session(sessionmaker(bind=engine))
    session = Session()

    location = session.query(Location).filter(Location.id == id).first()
    totalLogs = Logs.query.filter(and_(Logs.id <= location.last_id, Logs.id >= location.first_id, Logs.f3==search)).count()

    page=int(request.args.get('page', 1))
    offset = (page-1)*LOGSPERPAGE
    
    if totalLogs < offset+LOGSPERPAGE:
        last=totalLogs+1
    else:
        last=offset+LOGSPERPAGE


    logs = Logs.query.filter(and_(Logs.f3==search), Logs.id>= location.first_id, Logs.id<=location.last_id).offset(offset).limit(LOGSPERPAGE)

    pagination = Pagination(page=page,
                            per_page=LOGSPERPAGE,
                            offset=offset,
                            total=totalLogs,
                            record_name='logs',
                            format_total=False,
                            format_number=True,
                            bs_version=4,
                            )

    session.close()
    close()
    return render_template('showLogs.html', location = location,
                                        logs = logs,
                                        pagination=pagination,
                                        )


@application.route('/delete/id:<id>/')
def delete(id):
    Session = scoped_session(sessionmaker(bind=engine))
    session = Session()

    location = session.query(Location).filter(Location.id == id).first()

    session.query(Logs).filter(and_(Logs.id <= location.last_id, Logs.id >= location.first_id)).delete()
    session.delete(location)
    session.commit()

    session.close()
    close()
    return redirect('/')

#dl = session.query(Logs).filter(Logs.id == 60).first()
    #session.delete(dl)


@application.route("/download/<date>,<time>")
def get_single_file(date, time):
    Session = scoped_session(sessionmaker(bind=engine))
    session = Session()

    location = session.query(Location).filter(Location.date==date, Location.time==time).first()    
    
    if not location:
        print("File not found")
    with MeasureDuration() as m:
        with open("/tmp/test.txt", "w") as f:
            logs = session.query(Logs).filter(and_(Logs.id >= location.first_id , Logs.id <= location.last_id ))  

            for l in logs:
                f.write(str(l.f1) + "," + 
                        str(l.f2) + "," + 
                        str(l.f3) + "," + 
                        str(l.f4) + "," + 
                        str(l.f5) + "," + 
                        str(l.f6) + "," + 
                        str(l.f7) + "," + 
                        str(l.f8) + "," + 
                        str(l.f9) + "," + 
                        str(l.f10) + "," + 
                        str(l.f11) + "," + 
                        str(l.f12) + "," + 
                        str(l.f13) + "," + 
                        str(l.f14) + "\n")

    session.close()
    close()

    #sql='SELECT * FROM ' + config.LOGSTABLE + ' WHERE id>=' + str(location.first_id) + ' AND id<=' + str(location.last_id) +\
    #    ' INTO OUTFILE \'/tmp/test.csv\'' 

    #print(sql)
    #engine.execute(sql)
    session.close()
    return send_from_directory('/tmp/', "test.txt", as_attachment=False)


@application.route("/download/from:<date>,<time>/to:<date2>,<time2>")
def get_file(date,time,date2,time2):
    Session = scoped_session(sessionmaker(bind=engine))
    session = Session()

    location = session.query(Location).filter(Location.date>=date, Location.date<=date2, Location.time>=time, Location.time<=time2)\
                .order_by(Location.date.asc(), Location.time.asc())
    
    #Test if location is not empty
    if location:
        firstLocation = session.query(Location).order_by(Location.id.desc()).filter(Location[0].id<location.id).first()
    else:
        firstLocation = None
    #logs = session.query(Logs).filter(and_(Logs.id <=20000 , Logs.id >=81 ))
    
    
    with MeasureDuration() as m:
        with open("/tmp/test.txt", "w") as f:

            if not location:
                print("no results\n")
            else:

                if firstLocation != None:
                    logs = session.query(Logs).filter(and_(Logs.id >= firstLocation.first_id , Logs.id <= firstLocation.last_id )) 
                    #for l in logs:



                for loc in location:
                    print("loc:", loc.date, loc.time)
                    

                    if loc == location[-1]: #if its the last location in the list
                        logs = session.query(Logs).filter(and_(Logs.id >= loc.first_id , Logs.id <= loc.last_id ))                        
                        print("last loc", loc.first_id,"\n")
                    else:
                        logs = session.query(Logs).filter(and_(Logs.id >= loc.first_id , Logs.id <= loc.last_id ))
                        print("loc", loc.first_id, "\n")
                        
                    
                    for l in logs:
                        #print("printing\n")
                        f.write(str(l.f1) + "," + 
                                    str(l.f2) + "," + 
                                    str(l.f3) + "," + 
                                    str(l.f4) + "," + 
                                    str(l.f5) + "," + 
                                    str(l.f6) + "," + 
                                    str(l.f7) + "," + 
                                    str(l.f8) + "," + 
                                    str(l.f9) + "," + 
                                    str(l.f10) + "," + 
                                    str(l.f11) + "," + 
                                    str(l.f12) + "," + 
                                    str(l.f13) + "," + 
                                    str(l.f14) + "\n")
                    

    #sys.stdout.flush()

    session.close()
    close()
    return send_from_directory('/tmp/', "test.txt", as_attachment=False)

####################

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
        #print "Total time taken: %s" % self.duration()

    def duration(self):
        return str((self.end - self.start) * 1000) + ' milliseconds'
 
####################



if __name__ == '__main__':
    application.run(host='0.0.0.0')


