import requests, json, time, psycopg2, random, multiprocessing


headers = {'content-type': "application/x-www-form-urlencoded"}

class GMM(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.base_url = 'https://preproduction.getmoremath.com/'


    def student_login(username, password):
        try:
            loginPayload = 'username=%s&password=%s&gmmcodebase=2' % (self.username, password)
            loginPost = requests.post(self.base_url+"Login", data=loginPayload, headers=headers)
            loginResponse = json.loads(loginPost.text)
            #if loginResponse['badCredentials'] = 't':
            self.questionId = loginResponse['w']
            self.ss = loginResponse['ss']
            self.guid = loginResponse['guid']
            self.sicId = loginResponse['sicId']

            # MAKE NEW FUNCTION HERE student_question
            questionPayload = 'id=%s&ss=%s&user=%s&isTest=false&guid=%s&sicId=%s' % (self.questionId, self.ss, self.username, self.guid, self.sicId)
            questionPost = requests.post(base_url+"ServletRestore", data=questionPayload, headers=headers)
            questionResponse = json.loads(questionPost.text)
            md5 = questionResponse['p']['md5']
            print "successfully connected", user
        except requests.ConnectionError, e:
            print e
        except KeyError, k:
            print 'Key Error: missing %s' % k

    def student_submit(user):
        try:
            global md5, questionId
            correct = 'true' if random.randrange(100) < 70 else 'false'
            answerPayload = 'id=%s&ss=%s&user=%s&guid=%s&correct=%s' % (questionId, ss, user, guid, correct)
            print answerPayload
            answerPost = requests.post(base_url+"Submit", data=answerPayload, headers=headers)
            answerResponse = json.loads(answerPost.text)
            if answerResponse['aC'] == True:
                print answerResponse['p']['md5']
                questionId = answerResponse['w']
                md5 = answerResponse['p']['md5']
            print answerResponse
        except requests.ConnectionError, e:
            print e

# Fake students for testing
studs= [('jsmith123','jsmith123')]

import thread
import time

# Define a function for the thread
def print_time( threadName, delay):
   count = 0
   while count < 5:
      time.sleep(delay)
      count += 1
      print "%s: %s" % ( threadName, time.ctime(time.time()) )

# Create two threads as follows
try:
   thread.start_new_thread( print_time, ("Thread-1", 2, ) )
   thread.start_new_thread( print_time, ("Thread-2", 4, ) )
except:
   print "Error: unable to start thread"

while 1:
   pass