import requests, json, time, psycopg2, random, datetime, threading, urllib
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from locust import HttpLocust, TaskSet, task
from auth import credentials

#studs= [('jsmith123','jsmith123')]
studs= [('LS111193','StepFifth60&')]
base_url = 'https://localhost:8080'
headers = {'content-type': "application/x-www-form-urlencoded"}

d = {}
l = []

print len(studs)

class UserBehavior(TaskSet):

    
    def on_start(self):
        if len(studs) > 0:
            try:
                #creds = random.choice(studs)
                creds = studs[0]
                user = creds[0]
                pwd = creds[1]
                # add user to list for message check sequence
                l.append(user)
                del studs[0]
                login_payload = {"username":user,"password":pwd,"gmmcodebase":"2"}
                login_post = self.client.post("/Login", data=login_payload, headers=headers)
                print "logged in %s" % creds[0]
                login_response = json.loads(login_post.text)
                question_id = login_response['w']
                ss = login_response['ss']
                guid = login_response['guid']
                sic_id = login_response['sicId']
                question_payload = {"id":question_id,"ss":ss,"user":user,"isTest":"false","guid":guid,"sicId":sic_id}
                question_post = self.client.post("/ServletRestore", data=question_payload, headers=headers)
                question_response = json.loads(question_post.text)
                md5 = question_response['p']['md5']
                d.update({user: [question_id, ss, guid, sic_id, pwd, md5]})
                print len(studs)
                # Message Check sent every 5 seconds per logged in student, 60 times
                count = 0
                while (count < 4):
                    pass
                    time.sleep(5)
                    message_payload = 'ss=%s&lastMsgId=-1&guid=%s&user=%s' % (ss, guid, user)
                    message_post = self.client.post("/MessageCheck", data=message_payload, headers=headers)
                    message_response = json.loads(message_post.text)
                    print "Message Check for %s" % (user)
                    count += 1
            except KeyError, e:
                print 'Key Error: missing %s for %s password %s.  Failed login task' % (e, user, pwd)
                print 'Payload sent: %s' % (login_payload)
                print "Login Response: %s" % (login_response)
                ee = open("log.txt", "a+")
                ee.write(e)
                ee.close()
                #students.remove(credentials)
            except ValueError, v:
                print 'Value Error: No JSON object for user=%s password=%s' % (user, pwd)
                print 'Payload sent: %s' % (login_payload)
                print 'Login Post: %s' % (login_post)
                ee = open("log.txt", "a+")
                ee.write(v)
                ee.close()

    def message_check(self):
        if len(l) > 0:
            try:
                # Pull student from list and remove
                kid = l[0]
                del l[0]

                # Gather info for payload
                m_ss = d[kid][1]
                m_guid = d[kid][2]

                # Message Check sent every 5 seconds per logged in student, 100 times
                count = 0
                while (count < 100):
                    time.sleep(5)
                    message_payload = {'ss': m_ss, 'lastMsgId':-1, 'guid': m_guid, 'user': kid}
                    message_post = self.client.post("/MessageCheck", data=message_payload, headers=headers)
                    message_response = json.loads(message_post.text)
                    print "Message Check for %s" % (kid)
                    count += 1
            except KeyError, k:
                print 'Key Error: missing %s for %s password %s Failed answer task' % (k, chosen, a_pwd)
                print answer_payload
                print d[chosen]
                print answer_response

    @task
    def answer(self):
        #wait = random.randrange(60)
        #time.sleep(wait)
        if len(d) > 0:
            try:
                chosen = random.choice(d.keys())
                correct = 'true' if random.randrange(100) < 70 else 'false'
                a_question_id = d[chosen][0]
                a_ss = d[chosen][1]
                a_guid = d[chosen][2]
                a_sic_id = d[chosen][3]
                a_pwd = d[chosen][4]
                a_md5 = d[chosen][5]
                answer_payload = {'id': a_question_id, 'ss': a_ss, 'user': chosen, 'guid': a_guid, 'correct' : correct, 'md5': a_md5}
                print "Payload sent %s" % (answer_payload)
                #print answer_payload
                answer_post = self.client.post("/Submit", data=answer_payload, headers=headers)
                #time.sleep(1)
                answer_response = json.loads(answer_post.text)
                #print answer_response
                if 'w' in answer_response and answer_response['w'] != a_question_id:
                    next_question_payload = {"id":a_question_id,"ss":a_ss,"user":chosen,"isTest":"false","guid":a_guid,"sicId":a_sic_id}
                    next_question_post = self.client.post("/ServletRestore", data=next_question_payload, headers=headers)
                    next_question_response = json.loads(next_question_post.text)
                    a_md5 = next_question_response['p']['md5']
                    print a_md5
                    a_question_id = answer_response['w']
                    d.update({chosen: [a_question_id, a_ss, a_guid, a_sic_id, a_pwd, a_md5]})
                    print "Answer Response: %s" % (answer_response)
                    print "Question Response: %s" % (next_question_response)
                    print "Updated info: User=%s %s" % (chosen, d[chosen])
                print 'Answered question for user=%s id=%s guid=%s' % (chosen, a_question_id, a_guid)
                count = 0
                while (count < 4):
                    time.sleep(5)
                    a_message_payload = {'ss': a_ss, 'lastMsgId':-1, 'guid': a_guid, 'user': chosen}
                    a_message_post = self.client.post("/MessageCheck", data=a_message_payload, headers=headers)
                    a_message_response = json.loads(a_message_post.text)
                    print "Message Check for %s" % (chosen)
                    count += 1
            except KeyError, k:
                print 'Key Error: missing %s for %s password %s Failed answer task' % (k, chosen, a_pwd)
                print answer_payload
                print d[chosen]
                print answer_response
                #del d[chosen]
            except IndexError, i:
                print 'Index Error'
                print 'User %s password %s' (chosen, a_pwd)
                print d[chosen]



class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 1000
    max_wait = 3000