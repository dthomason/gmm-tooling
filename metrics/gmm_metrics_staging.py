import requests, json, time, psycopg2, random, datetime, threading
from boto.ec2.cloudwatch import connect_to_region
import boto.ec2.cloudwatch
import os
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)
from auth import credentials

def grab_students():

    # Get current date and time
    dat = time.ctime()
    dt = str(dat)
    # Database connection
    try:
        hostname = 'gmm-staging-db.ckhau7urrr2b.us-east-1.rds.amazonaws.com'
        myConnection = psycopg2.connect(host=hostname, user=credentials['DB_USERNAME'], password=credentials['DB_PASSWORD'], dbname=credentials['DATABASE'])
    except:
        ee = open("log.txt", "a+")
        ee.write(dt + " Error: can not connect to DB \r\n")
        ee.close()
    # SQL Query function
    def doQuery(conn) :
        cur = conn.cursor()
        # Calculate time frame needed in epoch time
        e = int(time.time() * 1000)
        e1 = e - 300000

        # SQL Query
        sql = ("""SELECT * FROM LogIn
                WHERE time > %s""" % str(e1))

        # Execute the SQL Query
        cur.execute( sql )
        # Store them in students
        global students
        students = cur.fetchall()

    # Run Query
    try:
        doQuery(myConnection)
    except:
        ee = open("log.txt", "a+")
        ee.write(dt + " Error: retrieving data from the DB \r\n")
        ee.close()

    myConnection.close()

    # How many students pulled from DB
    #print "Pulled %s students from database" % (len(students))

def active():

    r = redis.Redis(
        host='messagestore.3dxgn6.0001.use1.cache.amazonaws.com',
        port='6379')
    global active_teachers, active_students
    active_teachers = r.keys('activeTchr*')
    active_students = r.keys('activeStd*')

grab_students()
number=len(students)
region='us-east-1'

active()
active_teacher_count = len(active_teachers)
#print active_teacher_count
active_student_count = len(active_students)
#print active_student_count

conn_cw=boto.ec2.cloudwatch.connect_to_region(region,aws_access_key_id=credentials["AWS_ID"],aws_secret_access_key=credentials["AWS_SECRET"])
conn_cw.put_metric_data(namespace='gmmops',name='logins',value=number)
conn_cw.put_metric_data(namespace='gmmops',name='active_teachers',value=active_teacher_count)
conn_cw.put_metric_data(namespace='gmmops',name='active_students',value=active_student_count)
