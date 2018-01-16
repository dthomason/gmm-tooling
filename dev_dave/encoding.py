import requests, json, time, psycopg2, random, datetime, threading, urllib
#from requests.packages.urllib3.exceptions import InsecureRequestWarning
from locust import HttpLocust, TaskSet, task
import os
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)
from auth import credentials

#studs= [('LS111193','StepFifth60&')]
studs=[('yyy','xxx')]
creds=studs[0]
user=creds[0]
pwd=creds[1]

#base_url = 'http://localhost:8080/'
headers = {'content-type': "application/x-www-form-urlencoded"}

loginPayload = {"username":user,
                "password":pwd,
                "gmmcodebase":"2"}

#loginPayload = 'username=%s&password=%s&gmmcodebase=2' % (user, pwd)
loginPost = requests.post(base_url+"Login", data=loginPayload, headers=headers)
loginResponse = json.loads(loginPost.text)

newId = 34172194

answerResponse = {u'lastThree': u'3/3', u'aC': True, u'pfd': 10, u'myAllTime': u'103/147', u'lastAttempt': 1514915170821L, u'lastTen': u'8/10', 
u'ptd': 6, u's': 3, u'tC': True, u'rawScore': 6.900001525878906, u'p': {u'r': [[{u'xml': u'<t>Your bill is $37.08</t>'}], 
[{u'xml': u'<t>You pay with $40</t>'}], [{u'xml': u'<t>What is your change?</t>'}],
[{u'ag': {u'vH': 100, u'lines': [{u'xml': u'<t></t>'}], u'agId': 0, u's': u'u', u't': u'n', u'vW': 200}}]], 
u'md5': u'4930842DEF16662A6622405FC7203F46'}, u'incScore': True, u'gc': 2, u'w': 34172195, 
u'lvl': u'gold', u'allTime': u'322/429', u'id': u'34186406', u'd': [34172195]}

#answerResponse = {u'lastThree': u'3/3', u'aC': True, u'pfd': 10, u'myAllTime': u'103/147', u'lastAttempt': 1514915170821L, u'lastTen': u'8/10', 
#u'ptd': 6, u's': 3, u'tC': True, u'rawScore': 6.900001525878906}

if 'w' in answerResponse and answerResponse['w'] != newId:
    print newId

newTest = '4321'
test = '1234'
if '1234' in test and test == newTest:
    print test

l = []

value = "info"
l.append(value)
value2 = "stuff"
l.append(value2)

base_url = 'https://preproduction.getmoremath.com'

get_student_count = requests.get(base_url+'/stats/requests')
print get_student_count

def grab_students(limit):

    

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
        e1 = e - 1209600000

        # SQL Query
        sql = ("""SELECT l.username, s.password, MAX(l.time) mTime 
                FROM public.login l 
                JOIN public.student s ON s.username = l.username
                WHERE l.time > %s
                Group By l.username, s.password
                Order By mTime DESC
                LIMIT %s""" % (str(e1), str(limit)))
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
    print "Pulled %s students from database" % (len(students))

