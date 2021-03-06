#making a snap shot of the replica DB in prod, spinning up a DB in prod, getting a dump from the new DB, uploading the dump to AWS, finally removing the snap shot, DB, and dump.
import os, sys, subprocess, time, datetime
import boto3
import DBreplace
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)
import awsinfo

a=awsinfo
acc=a.AccountSwitch
h=a.Hhtb
d=DBreplace

#variables
name = 'prod-static-I'
SR = h.reg['nv']
DB = 'gmm-production-db-replica-1'
s = h.typ['s']
db = h.typ['d']
SG = h.sg['rep']
vpc = 'default'

#running the script, calling the necessary functions from the DBreplace file
acc('p')
d.keyID=a.keyID
d.secA=a.secA
d.CreateDBSS(name,DB,SR)
d.CheckNwait(s,name,SR)
time.sleep(15)
d.CheckNwait(s,name,SR)
time.sleep(15)
d.CheckNwait(s,name,SR)
d.RestoringDB(name,'db.t2.small',name,vpc,SR)
d.CheckNwait(db,name,SR)
d.CheckNwait(db,name,SR)
d.ModifyDB(name,SG,'pgstats',SR)
d.CheckNwait(db,name,SR)
d.CheckNwait(db,name,SR)
time.sleep(30)
#getting a fcdump file from the new DB
os.system("sudo PGPASSWORD=%s pg_dump --host gmm-staging-db.ckhau7urrr2b.us-east-1.rds.amazonaws.com --port 5432 -U %s -f /home/ec2-user/BigMath.fcdump BigMath -Fc" % (dbPW, dbU))
print("dump")
#uploading the fcdump to the appropriate AWS S3 bucket
subprocess.call("sudo python3.6 /home/ec2-user/_dbrep/dbplace/db_backup.py", shell=True)  
#removing the fcdump file from brains
os.system ("sudo PGPASSWORD=%s pg_dump --host prod-static-i.cblcix4wsn1v.us-east-1.rds.amazonaws.com --port 5432 -U %s -f home/ec2-user/BigMath.fcdump BigMath -Fc" % (dbPW, dbU)) 
print("remove")
d.DeleteSS(name,SR)
d.DeletingDB(name,SR)
print("done!!!!!!!!!!!!!!!!!!!!!!!")

