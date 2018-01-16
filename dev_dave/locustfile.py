import requests, json, time, psycopg2, random, datetime, threading
from multiprocessing import Process
from auth import credentials
from locust import HttpLocust, TaskSet, task

base_url = 'http://localhost:8080/'
headers = {'content-type': "application/x-www-form-urlencoded"}


# Fake students for testing
kids= [('jsmith123','jsmith123'),('yyy','yyy')]
user = 'jsmith123'
pwd = 'jsmith123'

class UserBehavior(TaskSet):
    @task
    def student_login(self):
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
            print questionPayload
            questionResponse = json.loads(questionPost.text)
            md5 = questionResponse['p']['md5']
            print "Successfully logged in student:", user
            correct = 'true' if random.randrange(100) < 70 else 'false'
            answerPayload = 'id=%s&ss=%s&user=%s&guid=%s&correct=%s' % (questionId, ss, user, guid, correct)
            print answerPayload
            answerPost = requests.post(base_url+"Submit", data=answerPayload, headers=headers)
            answerResponse = json.loads(answerPost.text)
            if answerResponse['aC'] == True:
                questionId = answerResponse['w']
        except requests.ConnectionError, e:
            print e
        except KeyError, k:
            print 'Key Error: missing %s' % k

class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 5000
    max_wait = 9000