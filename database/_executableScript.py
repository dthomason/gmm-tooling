import os, sys, subprocess, time
import DBreplace
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)
import awsinfo

a=awsinfo
h=awsinfo.Hhtb
acc=a.AccountSwitch
d=DBreplace

#function which prompts the user for input. based on the input, variables are assigned values.
#Source DB, Target DB, Source Region, Target Account, DB class
def SSnDB():
  global SR,TR,SD,TD,DBCS
  sore = 'a'
  tare = 'a'
  sodb = 'a'
  tadb = 'a'
  while sore not in ('n.vir','n.cal','ore'):
    sore = input('What region contains the snapshot? n.vir, n.cal, ore  ')
    if sore == 'n.vir':
      SR = h.reg['nv']
    elif sore == 'n.cal':
      SR = h.reg['nc']
    elif sore == 'ore':
      SR = h.reg['or']
    else:
      print('e')
  while tare not in ('n.vir','n.cal','ore'):
    tare = input('what region contains the db you wish to replace? n.vir, n.cal, ore  ')
    if tare == 'n.vir':
      TR = h.reg['nv']
    elif tare =='n.cal':
      TR = h.reg['nc']
    elif tare == 'ore':
      TR = h.reg['or']
    else:
      print('e')
  while sodb not in ('prod','dev','staging'):
    sodb = input('What is the Name of the db which the snapshot is created from? e.g. prod, dev, staging  ')
    if sodb =='prod':
      SD = h.db['p']
    elif sodb == 'dev':
      SD = h.db['d']
    elif sodb == 'staging':
      SD = h.db['s']
    else:
      print('e')
  while tadb not in ('dev','staging'):
    tadb = input('Name of the db you wish to replace? dev, staging  ')
    if tadb == 'dev':
      TD = h.db['d']
    elif tadb == 'staging':
      TD = h.db['s']
    else:
      print('e')
  DBCS=input("DB size? e.g. db.m4.large  ")
  return SR,TR,SD,TD,DBCS
#copies the latest snapshot of the deisred DB to a region. 
def copySnapShot():
  acc(SA)
  d.CopyDBSS(CD,SD,SAN,TR,SR)
  SSName=d.SSName
  d.CheckNwait(tss,SSName,TR)
#shares the copied DB to a different AWS account.
def shareSnapShot():
  d.SharingDBSS(TAN,SAN,TR)
  global SDBID
  SDBID=d.SDBID
  acc(TA)
  return SDBID
#Deletes, restores, modifies, and reboots, a desired database with the copied/shared DB snap shot.
def replaceDB():
  d.DeletingDB(TD,TR)
  vpc=d.vpc
  d.RestoringDB(TD,DBCS,SDBID,TR)
  d.CheckNwait(tdb,TD,TR)
  d.CheckNwait(tdb,TD,TR)
  d.ModifyDB(TD,TSG,PG,MR,TR)
  d.CheckNwait(tdb,TD,TR)
  d.rebootDB(TD,TR)
  d.CheckNwait(tdb,TD,TR)
  print("done!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1")
  
#variables not determined by the user input script above.  
global tss,tdb,CD,PG  
tss=h.typ['s']
tdb=h.typ['d']
CD=h.CurrentDate  
PG = 'pgstats'  
MR = h.mr['s']
#start of the running script.  
print("This script allows you to replace an existing DB from a snapshot. Please answer the following questsions")
time.sleep(5)

#more user prompted input.
Share = 'a'
while Share not in ('Y','N'):
  Share = input('Is the snapshot under a different account? Y or N  ')
  if Share in ('Y','N'):
    break

if Share == 'Y':
  soac='a'
  while soac not in ('GMM','GMMOPS', 'GMMDEV'):
    soac = input('What account is the snapshot located? GMM,, GMMDEV, or GMMOPS  ')
    if soac in ('GMM','GMMOPS'):
      if soac == 'GMM':
        SA = 'p'
        SAN = h.acc['p']
      elif soac == 'GMMOPS':
        SA = 's'
        SAN = h.acc['s']
      elif soac == 'GMMDEV':
        SA = 's'
        SAN = h.acc['d']
      else:
        print("What?")

  taag='a'
  while taag not in ('GMM','GMMOPS', 'GMMDEV'):
    taag = input('What account has the DB that you wish to replace? GMM, GMMDEV, or GMMOPS  ')
    if taag in ('GMM','GMMOPS'):
      if taag == 'GMM':
        TA = 'p'
        TAN = h.acc['p']
      elif taag == 'GMMOPS':
        TA = 's'
        TAN = h.acc['s']
      elif taag == 'GMMDEV':
        TA = 'd'
        TAN = h.acc['d']
      else:
        print("What?")
         
  SSnDB()
  if TR == 'us-east-1' and TA == 's':
    TSG = h.sg['snv']
    q = input("do you want to replace the longterm Redis")
    if q =='y':
      subprocess.call("redisR.py", shell=True)
      print("staging longterm redis is being replaced")
    else:
      break
  elif TR == 'us-west-2' and TA == 'p':
    TSG = h.sg['por']
  else:
    print("Not available yet, please start over")
    sys.exit()
  copySnapShot()
  shareSnapShot()
  replaceDB()
	  
elif Share == 'N':
  AA = 'a'
  while AA not in ('GMM','GMMOPS', 'GMMDEV'):
    AA = input("what account is the snapshot and DB located? GMM, GMMDEV, or GMMOPS  ")
    if AA in ('GMM','GMMOPS'):
      if AA == 'GMM':
        SA = 'p'
        SAN = h.acc['p']
        TA = 'p'
        TAN = h.acc['p']
      elif AA == 'GMMOPS':
        SA = 's'
        SAN = h.acc['s']
        TA = 's'
        TAN = h.acc['s']
      elif AA == 'GMMDEV':
        SA = 's'
        SAN = h.acc['d']
        TA = 's'
        TAN = h.acc['d']
      else:
        print("What?")
        
  SSnDB()
  if TR == 'us-east-1' and TA == 's':
    TSG = h.sg['snv']
    q = input("do you want to replace the longterm Redis? (y)  ")
    if q =='y':
      subprocess.call("redisR.py", shell=True)
      print("preprod longterm redis is being replaced")
    else:
      break
  elif TR == 'us-west-2' and TA == 'p':
    TSG = h.sg['por']
  else:
    print("Not available yet, please start over")
    sys.exit()
  copySnapShot()
  replaceDB()

else:
  print("WOW HOW DID THIS HAPPEN")
  
  
