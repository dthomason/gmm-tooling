import requests, json, time, psycopg2, random, datetime, threading
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from locust import HttpLocust, TaskSet, task, events
from locust.exception import StopLocust
import os
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)
from auth import credentials

#resource.setrlimit(resource.RLIMIT_NOFILE, (999999, 999999))

num_of_students = 10000
#print resource.getrlimit(resource.RLIMIT_NOFILE)

# Fake students for testing
studs= [('jsmith123','jsmith123'),('yyy','yyy')]

base_url = 'https://gmm.getmoremath.com'
headers = {'content-type': "application/x-www-form-urlencoded"}

d = {}

local_url = 'http://localhost:8089'


def grab_students():

    # Get current date and time
    dat = time.ctime()
    dt = str(dat)
    # Database connection
    try:
        hostname = 'awsdb.cblcix4wsn1v.us-east-1.rds.amazonaws.com'
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
        #e1 = e - 300000
        e1 = e - 1209600000

        # SQL Query
        sql = ("""SELECT l.username, s.password, MAX(l.time) mTime 
                FROM public.login l 
                JOIN public.student s ON s.username = l.username
                WHERE l.time > %s
                Group By l.username, s.password
                Order By mTime DESC""" % str(e1))
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


# Locust Class
class UserBehavior(TaskSet):

    grab_students()

    # Login method
    @task
    def login(self):
        if len(students) > 0:
            try:

                # Pull credentials for first user in list then delete
                student = students[0]
                user = student[0]
                pwd = student[1]
                del students[0]
            
                # Login Payload setup
                login_payload = {"username":user,"password":pwd,"gmmcodebase":"2","fakeLoginForRedisRestoration":"true"}
                
                # Login Student
                #login_post = self.client.post("/Login", data=login_payload, headers=headers)
                #login_response = json.loads(login_post.text)
                
                # Login and Catch Response to check values to report to locust
                with self.client.post("/Login", data=login_payload, headers=headers, catch_response=True) as login_post:
                    login_response = json.loads(login_post.text)
                    if 'w' not in login_response:
                        print 'Failed login task for %s' % (user)
                        dat = time.ctime()
                        dt = str(dat)
                        login_post.failure('Payload Sent: %s ---- Response: %s' % (login_payload, login_response))
                        ee = open("log.txt", "a+")
                        ee.write(dt + """ Payload Sent: %s \n%s Response: %s \r\n""" % (login_payload, dt, login_response))
                        ee.close()
                        raise StopLocust()
                
                # Update dict with student info
                d.update({user: [pwd]})
                print "Logged in student=%s count=%s" % (user, len(d))


            # Error catch and logging for Key Error, caused by bad response
            except KeyError, e:
                ee = open("log.txt", "a+")
                ee.write(dt + """ Payload Sent: %s \n%s Response: %s \r\n""" % (login_payload, dt, login_response))
                ee.close()
                #students.remove(credentials)

            # Error catch and logging for Value Error, usually no JSON object returned
            except ValueError, v:
                print 'Value Error: No JSON object for user=%s password=%s' % (user, pwd)
                print 'Payload sent: %s' % (login_payload)
                print "Login Response: %s" % (login_response)
                ee = open("log.txt", "a+")
                ee.write("""Value Error: %s for user=%s \n
                            Payload sent: %s \n
                            Login Post: %s \r\n""" % (v, user, login_payload, login_post))
                ee.close()




class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    # Might want to remove
