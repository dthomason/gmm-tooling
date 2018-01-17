import requests, json, time, datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning

user = "yyy"
pwd = "yyy"
base_url = "https://staging.getmoremath.com"
login_payload = {'username':user,
    'password':pwd,
    'gmmcodebase':"2"
    }
headers = {
    'content-type': "application/x-www-form-urlencoded",
    'cache-control': "no-cache"
    }

def login():
    with requests.post(base_url+"/Login", data=login_payload, headers=headers) as login_post:
        login_response = json.loads(login_post.text)
        if 'w' not in login_response:
            dat = time.ctime()
            dt = str(dat)
            print dt + ' Failed login for %s' % (user)
        else:
            dat = time.ctime()
            dt = str(dat)
            print dt + ' Check Successful' 


login()

