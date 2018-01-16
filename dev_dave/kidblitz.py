import requests, json, time, psycopg2, random, datetime, threading
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from multiprocessing import Process
from auth import credentials


dat = time.ctime()
dt = str(dat)
# Database connection
try:
    hostname = 'gmm-preproduction-db.cjvmtlk6flsa.us-west-1.rds.amazonaws.com'
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
    e1 = e - 80480000

    # SQL Query
    sql = ("""SELECT DISTINCT l.username, s.password 
            FROM public.login l 
            JOIN public.student s ON s.username = l.username 
            WHERE l.time > """ + str (e1) )
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

base_url = 'http://localhost:8080/'
headers = {'content-type': "application/x-www-form-urlencoded"}

#class gmmSession(object):
#    def __init__(self):

#        self.base_url = 'https://preproduction.getmoremath.com/'
#        self.headers = {'content-type': "application/x-www-form-urlencoded"}
#        self.count = 0
#    def student_login(self, username, password):
#        try:
#            loginPayload = 'username=%s&password=%s&gmmcodebase=2' % (username, password)
#            loginPost = requests.post(self.base_url+"Login", data=loginPayload, headers=self.headers)
#            loginResponse = json.loads(loginPost.text)
#            self.questionId = loginResponse['w']
#            self.ss = loginResponse['ss']
#            self.guid = loginResponse['guid']
#            self.sicId = loginResponse['sicId']
#        except requests.ConnectionError, e:
#            print e
#        return username
#    def get_question(self,)


def student_login(user, pwd):
    try:
        loginPayload = 'username=%s&password=%s&gmmcodebase=2' % (user, pwd)
        loginPost = requests.post(base_url+"Login", data=loginPayload, headers=headers)
        loginResponse = json.loads(loginPost.text)
        #if loginResponse['badCredentials'] = 't':
        global questionId, ss, guid, sicId, md5
        questionId = loginResponse['w']
        ss = loginResponse['ss']
        guid = loginResponse['guid']
        sicId = loginResponse['sicId']

        # MAKE NEW FUNCTION HERE student_question
        questionPayload = 'id=%s&ss=%s&user=%s&isTest=false&guid=%s&sicId=%s' % (questionId, ss, user, guid, sicId)
        questionPost = requests.post(base_url+"ServletRestore", data=questionPayload, headers=headers)
        questionResponse = json.loads(questionPost.text)
        md5 = questionResponse['p']['md5']
        print "Successfully logged in student:", user
    except requests.ConnectionError, e:
        print e
    except KeyError, k:
        print 'Key Error: missing %s' % k

def student_submit(user):
    try:
        global questionId
        correct = 'true' if random.randrange(100) < 70 else 'false'
        answerPayload = 'id=%s&ss=%s&user=%s&guid=%s&correct=%s' % (questionId, ss, user, guid, correct)
        answerPost = requests.post(base_url+"Submit", data=answerPayload, headers=headers)
        answerResponse = json.loads(answerPost.text)
        if answerResponse['aC'] == True:
            questionId = answerResponse['w']
    except requests.ConnectionError, e:
        print e
    except KeyError, k:
        print 'Key Error: missing %s' % k

# Fake students for testing
studs= [('jsmith123','jsmith123'),('yyy','yyy')]



def kid_blitz(kids):
    for kid in kids:
        try:
            student_login(kid[0],kid[1])
            for i in range(2):
                student_submit(kid[0])
                currentDT = datetime.datetime.now()
                print (str(currentDT))
                print "Answered question for student: %s" % (kid[0])

        except ValueError, v:
            print v

kid_blitz(studs)

#proc = []
#for i in range(20):
#    p = Process(target=kid_blitz(students))
#    p.start()
#    proc.append(p)
#    print proc
#for p in proc:
#    p.join()


#for i in range(5):
#    t = threading.Thread(target=kid_blitz(studs))
#    t.start()
