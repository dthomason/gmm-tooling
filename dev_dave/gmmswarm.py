import requests, json, time, psycopg2, random, datetime, threading
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from locust import HttpLocust, TaskSet, task
import os
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)
from auth import credentials

# Get current date and time
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
            LIMIT 10""" % str(e1))
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

# Fake students for testing
studs= [('jsmith123','jsmith123'),('yyy','yyy')]

base_url = 'https://preproduction.getmoremath.com'
headers = {'content-type': "application/x-www-form-urlencoded"}

d = {}

# Locust Class
class UserBehavior(TaskSet):

    # Login method
    @task
    def login(self):
        if len(students) > 0:
            try:
                # Pull a random student from student list
                #student = random.choice(students)
                #user = student[0]
                #pwd = student[1]

                # Comment out above and uncomment below to go from first to last in students list
                student = students[0]
                user = student[0]
                pwd = student[1]
                del students[0]
            
                # Login Payload setup
                login_payload = {"username":user,"password":pwd,"gmmcodebase":"2"}
                
                # Login Student
                login_post = self.client.post("/Login", data=login_payload, headers=headers)
                print "logged in %s" % user
                login_response = json.loads(login_post.text)
                
                # Gather information for future posts
                question_id = login_response['w']
                ss = login_response['ss']
                guid = login_response['guid']
                sic_id = login_response['sicId']
                
                # Question payload setup
                question_payload = {"id":question_id,"ss":ss,"user":user,"isTest":"false","guid":guid,"sicId":sic_id}
                
                # Get question for md5 hash
                question_post = self.client.post("/ServletRestore", data=question_payload, headers=headers)
                question_response = json.loads(question_post.text)
                md5 = question_response['p']['md5']
                
                # Update dict with student info
                d.update({user: [question_id, ss, guid, sic_id, pwd, md5]})
                print "Logged in students: %s" % (len(d))
                
                # Message Check sent every 5 seconds per logged in student, 4 times
                count = 0
                while (count < 4):
                    time.sleep(5)
                    message_payload = {'ss': ss, 'lastMsgId':-1, 'guid': guid, 'user': user}
                    message_post = self.client.post("/MessageCheck", data=message_payload, headers=headers)
                    message_response = json.loads(message_post.text)
                    print "Message Check for %s" % (user)
                    count += 1

            # Error catch and logging for Key Error, caused by bad response
            except KeyError, e:
                print 'Key Error: missing %s for %s password %s.  Failed login task' % (e, user, pwd)
                print 'Payload sent: %s' % (login_payload)
                print "Login Response: %s" % (login_response)
                ee = open("log.txt", "a+")
                ee.write("""Key Error: missing %s for user=%s \n
                            Payload sent: %s \n
                            Login Post: %s \r\n""" % (e, user, login_payload, login_post))
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

    # Answer Method
    @task
    def answer(self):

        # Wait a random amount of seconds within one minute
        #wait = random.randrange(60)
        #time.sleep(wait)
        
        # If dict has entries, continue
        if len(d) > 0:
            try:
                # Random student chosen from dict
                chosen = random.choice(d.keys())

                # 70% correct = true
                correct = 'true' if random.randrange(100) < 70 else 'false'

                # Pull latest student info from dict
                a_question_id = d[chosen][0]
                a_ss = d[chosen][1]
                a_guid = d[chosen][2]
                a_sic_id = d[chosen][3]
                a_pwd = d[chosen][4]

                # Answer payload setup
                answer_payload = {'id':a_question_id, 'ss':a_ss, 'user':chosen, 'guid': a_guid, 'sicId': a_sic_id, 'correct': correct}

                # Answer question
                answer_post = self.client.post("/Submit", data=answer_payload, headers=headers)
                answer_response = json.loads(answer_post.text)

                # If Answer Response contains a new question ID then this requests the new question and updates the dict with new ID and MD5 hash
                if 'w' in answer_response and answer_response['w'] != a_question_id:
                    next_question_payload = {"id":a_question_id,"ss":a_ss,"user":chosen,"isTest":"false","guid":a_guid,"sicId":a_sic_id}
                    next_question_post = self.client.post("/ServletRestore", data=next_question_payload, headers=headers)
                    next_question_response = json.loads(next_question_post.text)
                    a_md5 = next_question_response['p']['md5']
                    a_question_id = answer_response['w']
                    d.update({chosen: [a_question_id, a_ss, a_guid, a_sic_id, a_pwd, a_md5]})
                    print "Updated info: User=%s %s" % (chosen, d[chosen])

                # Final successful print statement for t-shooting
                print 'Answered question for user=%s id=%s guid=%s' % (chosen, a_question_id, a_guid)

                # Message Check sent every 5 seconds per logged in student, 4 times
                count = 0
                while (count < 4):
                    time.sleep(5)
                    a_message_payload = {'ss': a_ss, 'lastMsgId':-1, 'guid': a_guid, 'user': chosen}
                    a_message_post = self.client.post("/MessageCheck", data=a_message_payload, headers=headers)
                    a_message_response = json.loads(a_message_post.text)
                    print "Message Check for %s" % (chosen)
                    count += 1

            # Error handling
            except KeyError, k:
                print 'Key Error: missing %s for user=%s password=%s Failed answer task' % (k, chosen, a_pwd)
                print 'Payload sent: %s' % (answer_payload)
                print "Answer Response: %s" % (answer_response)
                ee = open("log.txt", "a+")
                ee.write("""Key Error: missing %s for user=%s \n
                        Payload sent: %s \n
                        Login Post: %s \r\n""" % (k, chosen, answer_payload, answer_post))
                ee.close()




class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 1000
    max_wait = 3000
