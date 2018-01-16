
# Locust Setup
## New Instance Setup

- Install dependencies
```
pip install locustio
pip install psycopg2
```
- Make sure you have uploaded the auth.py file into gmm-tooling/ directory

## Script Definitions
- strictly_logins.py - pulls all students from the database and logs them in at a rate defined in the UI. (http://localhost:8089) replace localhost with IP of master


- studentswarm.py - pulls amount of students specified in locust UI, then logs them in and answers questions.

    Command Example:
```
locust -f ./strictly_logins.py --host=https://staging.getmoremath.com --no-reset-stats
```
