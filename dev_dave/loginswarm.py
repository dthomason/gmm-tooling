import requests, json, time, psycopg2, random, datetime, threading
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from locust import HttpLocust, TaskSet, task
import os
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)
from auth import credentials


dat = time.ctime()
dt = str(dat)
# Database connection
try:
    hostname = 'gmm-preproduction-db.ckhau7urrr2b.us-east-1.rds.amazonaws.com'
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
            LIMIT 5000""" % str(e1))
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

print "Pulled %s students from database" % (len(students))

# Fake students for testing
studs= [('jsmith123','jsmith123'),('yyy','yyy')]

base_url = 'https://localhost:8080'
headers = {'content-type': "application/x-www-form-urlencoded"}

d = {}

class UserBehavior(TaskSet):

    @task(1)
    def login(self):
        try:
            #credentials = random.choice(students)
            credentials = students[0]
            user = credentials[0]
            pwd = credentials[1]
            del students[0]
            loginPayload = {"username":user,"password":pwd,"gmmcodebase":"2"}
            loginPost = self.client.post("/Login", data=loginPayload, headers=headers)
            print "logged in %s" % user
            loginResponse = json.loads(loginPost.text)
            questionId = loginResponse['w']
            ss = loginResponse['ss']
            guid = loginResponse['guid']
            sicId = loginResponse['sicId']
            d.update({user: [questionId, ss, guid, sicId, pwd]})
            print len(students)
        except KeyError, e:
            print 'Key Error: missing %s for %s password %s.  Failed login task' % (e, user, pwd)
            print 'Payload sent: %s' % (loginPayload)
            print "Login Response: %s" % (loginResponse)
            ee = open("log.txt", "a+")
            ee.write("""Key Error: missing %s for user=%s \n
                        Payload sent: %s \n
                        Login Post: %s \r\n""" % (e, user, loginPayload, loginPost))
            ee.close()
            #students.remove(credentials)
        except ValueError, v:
            print 'Value Error: No JSON object for user=%s password=%s' % (user, pwd)
            print 'Payload sent: %s' % (loginPayload)
            print 'Login Post: %s' % (loginPost)
            ee = open("log.txt", "a+")
            ee.write("""Value Error: %s for user=%s \n
                        Payload sent: %s \n
                        Login Post: %s \r\n""" % (v, user, loginPayload, loginPost))
            ee.close()

      
    def answer(self):
        wait = random.randrange(60)
        time.sleep(wait)
        if len(d) > 0:
            try:
                chosen = random.choice(d.keys())
                correct = 'true' if random.randrange(100) < 70 else 'false'
                a_questionId = d[chosen][0]
                a_ss = d[chosen][1]
                a_guid = d[chosen][2]
                a_sicId = d[chosen][3]
                a_pwd = d[chosen][4]
                answerPayload = 'id=%s&ss=%s&user=%s&guid=%s&sicId=%s&correct=%s' % (a_questionId, a_ss, chosen, a_guid, a_sicId, correct)
                #print answerPayload
                answerPost = self.client.post("/Submit", data=answerPayload, headers=headers)
                #time.sleep(1)
                answerResponse = json.loads(answerPost.text)
                #print answerResponse
                if answerResponse['aC'] == True:
                    a_questionId = answerResponse['w']
                    d.update({chosen: [a_questionId, a_ss, a_guid, a_sicId, a_pwd]})
                print 'Answered question for %s after waiting %s seconds' % (chosen, wait)
            except KeyError, k:
                print 'Key Error: missing %s for %s password %s Failed answer task' % (k, chosen, a_pwd)
                print answerPayload
                print d[chosen]
                print answerResponse
                del d[chosen]



class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 1000
    max_wait = 3000
    