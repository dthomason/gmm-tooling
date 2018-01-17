import os, sys, subprocess, time
import DBreplace
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)
import awsinfo


a=awsinfo
h=awsinfo.Hhtb
acc=a.AccountSwitch
d=DBreplace

#Copies the desired Snap Shot from desired Source Account and Source Region to the Target Region, and then confirms it is read for copying or sharing
def copySnapShot():
  acc(SA)
  d.keyID=a.keyID
  d.secA=a.secA
  d.CopyDBSS(CD,SD,SAN,TR,SR)
  SSName=d.SSName
  d.CheckNwait(tss,SSName,TR)
#Shares the copied Snap Shot to the Target Account.
def shareSnapShot():
  d.SharingDBSS(TAN,SAN,TR)
  global SDBID
  SDBID=d.SDBID
  acc(TA)
  d.keyID=a.keyID
  d.secA=a.secA
  return SDBID
#Deletes the existing DB, restores the DB from the desired Snap Shot, confirms the DB is ready for modifications, makes the modifications, 
#confirms it is done modifying, reboots for the pgstats change, and finally confirms the DB is available
def replaceDB():
  d.DeletingDB(TD,TR)
  SnG=d.SnG
  d.RestoringDB(TD,DBCS,SDBID,SnG,TR)
  d.CheckNwait(tdb,TD,TR)
  d.CheckNwait(tdb,TD,TR)
  d.ModifyDB(TD,TSG,PG,MR,TR)
  d.CheckNwait(tdb,TD,TR)
  d.CheckNwait(tdb,TD,TR)
  d.rebootDB(TD,TR)
  d.CheckNwait(tdb,TD,TR)
  d.CreateDBRR(RR,TD,TR)
  print("done!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1")
  
#Variables to be used in the above functions
global tss,tdb,CD  
tss=h.typ['s']
tdb=h.typ['d']
CD=h.CurrentDate  
SA='p'
TA='s'
SAN=h.acc['p']
TAN=h.acc['s']
SR=h.reg['nv']
TR=h.reg['nv']
SD=h.db['p']
TD=h.db['s']
TSG=h.sg['snv']
DBCS='db.m4.large'
PG='pgstats'
MR=h.mr['s']
RR=('%s-replica-1' % TD)
dbPW=a.dbPW
dbU=a.dbU
#Actually running the above functions
copySnapShot()
shareSnapShot()
replaceDB()
time.sleep(30)
#getting a fcdump file from the new DB
os.system("sudo PGPASSWORD=%s pg_dump --host gmm-staging-db.ckhau7urrr2b.us-east-1.rds.amazonaws.com --port 5432 -U %s -f /home/ec2-user/BigMath.fcdump BigMath -Fc" % (dbPW, dbU))
print("dump")
#uploading the fcdump to the appropriate AWS S3 bucket
subprocess.call("sudo python3.6 /home/ec2-user/database/db_backup.py", shell=True)  
#removing the fcdump file from brains
os.system ("sudo rm -f /home/ec2-user/BigMath.fcdum 
print("remove")