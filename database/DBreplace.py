import boto3  
import botocore 
import datetime  
import time

keyID
secA


#function used in CopyDBSS
def byTimestamp(snap):  
  if 'SnapshotCreateTime' in snap:
    return datetime.datetime.isoformat(snap['SnapshotCreateTime'])
  else:
    return datetime.datetime.isoformat(datetime.datetime.now())
#creating Database Snap Shot
def CreateDBSS (SSName,DBName,source_region):
  source = boto3.client('rds', aws_access_key_id=keyID, aws_secret_access_key=secA, region_name=source_region)
  source.create_db_snapshot(
    DBSnapshotIdentifier=SSName,
    DBInstanceIdentifier=DBName
)
#Coping Database Snap Shot
def CopyDBSS(CurrentDate,name,account,target_region,source_region):
    source = boto3.client('rds', aws_access_key_id=keyID, aws_secret_access_key=secA, region_name=source_region)
    source_snaps = source.describe_db_snapshots(DBInstanceIdentifier=name)['DBSnapshots']
    source_snap = sorted(source_snaps, key=byTimestamp, reverse=True)[0]['DBSnapshotIdentifier']
    source_snap_arn = 'arn:aws:rds:%s:%s:snapshot:%s' % (source_region, account, source_snap)
    print('Will Copy %s to %s' % (source_snap_arn, name))
    target = boto3.client('rds', aws_access_key_id=keyID, aws_secret_access_key=secA, region_name=target_region)
    global SSName
    SSName=("copy-from-%s-%s" % (name, CurrentDate))
    try:
        response = target.copy_db_snapshot(
        SourceDBSnapshotIdentifier=source_snap_arn,
        TargetDBSnapshotIdentifier=SSName,
        CopyTags = True)
    except botocore.exceptions.ClientError as e:
        raise Exception("Could not issue copy command: %s" % e)
    return SSName
#Sharing Database Snap Shot with another AWS Account
def SharingDBSS(target_account,source_account,source_region):
    source = boto3.client('rds', aws_access_key_id=keyID, aws_secret_access_key=secA, region_name=source_region)
    print("Sharing")
    source.modify_db_snapshot_attribute(
	    DBSnapshotIdentifier=SSName, 
	    AttributeName='restore', 
	    ValuesToAdd=[target_account]
    )
    time.sleep(15)
    global SDBID
    SDBID = "arn:aws:rds:%s:%s:snapshot:%s" % (source_region,source_account,SSName)
    return SDBID
#Deleing a Database Snap Shot
def DeleteSS(SSName,source_region):
    source = boto3.client('rds', aws_access_key_id=keyID, aws_secret_access_key=secA, region_name=source_region)
    source.delete_db_snapshot(
      DBSnapshotIdentifier=SSName
    )

#Deleting a Database and waiting until the deletion is complete
def DeletingDB(name,source_region):
    global SnG
    source = boto3.client('rds', aws_access_key_id=keyID, aws_secret_access_key=secA, region_name=source_region)
    print("Deleting")
    describe = source.describe_db_instances(DBInstanceIdentifier=name)['DBInstances']
    db_intance = describe[0]
    vpc = db_intance['DBSubnetGroup']['VpcId']
    source.delete_db_instance(
        DBInstanceIdentifier=name,
        SkipFinalSnapshot=True,
    )
    time.sleep(15)
    while True:
      source = boto3.client('rds', aws_access_key_id=keyID, aws_secret_access_key=secA, region_name=source_region)
      try:
        describe = source.describe_db_instances(DBInstanceIdentifier=name)['DBInstances']
        time.sleep(5)
      except botocore.exceptions.ClientError:
        break
    SnG=str("default-%s" % vpc)
    return SnG
#Restoring a Database from a snap shot	
def RestoringDB(name,dbcs,SSI,SnG,source_region):
    
    source = boto3.client('rds', aws_access_key_id=keyID, aws_secret_access_key=secA, region_name=source_region)
    print("Restoring")
    source.restore_db_instance_from_db_snapshot(
        DBInstanceIdentifier=name,
        DBSnapshotIdentifier=SSI,
        DBInstanceClass=dbcs,
        Port=5432,
        DBSubnetGroupName=SnG,
        MultiAZ=True,
        PubliclyAccessible=True,
        AutoMinorVersionUpgrade=False,
        Engine='postgres',
        StorageType='gp2',
    )
    return
#modifing a Database for the correct Security Group and Parameter Group.
def ModifyDB(name,SGC,param,MonRole,source_region):
  source = boto3.client('rds', aws_access_key_id=keyID, aws_secret_access_key=secA, region_name=source_region)
  source.modify_db_instance(
    DBInstanceIdentifier=name,
    DBParameterGroupName=param,
	VpcSecurityGroupIds=[
        SGC,
    ],
	ApplyImmediately=True,
    MonitoringInterval=60,
    MonitoringRoleArn=MonRole,
    
  )

#rebooting a Database
def rebootDB(name,source_region):
  print("rebooting")
  source = boto3.client('rds', aws_access_key_id=keyID, aws_secret_access_key=secA, region_name=source_region)
  source.reboot_db_instance(
    DBInstanceIdentifier=name,
    ForceFailover=False
  )

  
def CreateDBRR(Rname,Sname,source_region):
  source = boto3.client('rds', aws_access_key_id=keyID, aws_secret_access_key=secA, region_name=source_region)
  source.create_db_instance_read_replica(
    DBInstanceIdentifier=Rname,
    SourceDBInstanceIdentifier=Sname,
    DBInstanceClass='db.t2.small',
    AvailabilityZone='us-east-1f',
    Port=5432,
    AutoMinorVersionUpgrade=False,
    PubliclyAccessible=True,
    DBSubnetGroupName=SnG,
    StorageType='gp2',
    SourceRegion=source_region
)
#Checking to see if a Database or Database Snap Shot is in the available state.  
def CheckNwait(type,name,source_region):
  status='status'
  i=0
  while status != 'available':
    time.sleep(10)
    if type=='database':
      source = boto3.client('rds', aws_access_key_id=keyID, aws_secret_access_key=secA, region_name=source_region)
      describe = source.describe_db_instances(DBInstanceIdentifier=name)['DBInstances']
      db_intance = describe[0]
      status = db_intance['DBInstanceStatus']
      print(status)
    elif type=='snapshot': 
      source = boto3.client('rds', aws_access_key_id=keyID, aws_secret_access_key=secA, region_name=source_region)
      describe = source.describe_db_snapshots(DBSnapshotIdentifier=name)['DBSnapshots']
      db_snap = describe[0]
      status = db_snap['Status']
      print(status)
    else:
      print("not a snapshot or databse")
    i=i+1
    if i == 128:
      break
      print("timedout")
  time.sleep(45)
