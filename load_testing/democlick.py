import requests, json
from locust import HttpLocust, TaskSet, task

base_url = 'http://preproduction.getmoremath.com/'
headers = {'content-type': "application/x-www-form-urlencoded"}

class UserBehavior(TaskSet):

    @task
    def get_demo(self):
        demo = requests.get(base_url+"DemoProduction", headers=headers)
        print "New Student created"

class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 5000
    max_wait = 9000

