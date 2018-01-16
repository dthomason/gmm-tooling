#Deleting, creating, and checking a Redis instance.
import boto3
import botocore
import sys
import time
import DBreplace
import awsinfo

d=DBreplace
a=awsinfo
h=a.Hhtb
acc=a.AccountSwitch

def deleteR(name,SR):
  source_region = SR
  source = boto3.client('elasticache', aws_access_key_id=keyID, aws_secret_access_key=secA, region_name=source_region )
  source.delete_cache_cluster(
    CacheClusterId=name,
  )
  time.sleep(5)
  while True:
      source = boto3.client('elasticache', aws_access_key_id=keyID, aws_secret_access_key=secA, region_name=source_region)
      try:
        describe = source.describe_cache_clusters(CacheClusterId=name)['CacheClusters']
        cacheDes = describe[0]
        status = cacheDes['CacheClusterStatus']
        #print(status)
        time.sleep(10)
      except:
        break

def createR(type,name,csng,SR):
  source_region = SR
  source = boto3.client('elasticache', aws_access_key_id=keyID, aws_secret_access_key=secA, region_name=source_region )
  source.create_cache_cluster(
    CacheClusterId=name,
    AZMode='single-az',
    PreferredAvailabilityZone='us-east-1e',
    NumCacheNodes=1,
    CacheNodeType=type,
    Engine='redis',
    EngineVersion='3.2.4',
    CacheSubnetGroupName=csng,
    SecurityGroupIds=[
        'sg-5ed67b2a',
    ],
    Port=6379,
    AutoMinorVersionUpgrade=False,
  )
  
def CacheSNGCheck(source_region):
  source = boto3.client('elasticache', aws_access_key_id=keyID, aws_secret_access_key=secA, region_name=source_region)
  response = source.describe_cache_subnet_groups()['CacheSubnetGroups']
  first=response[0]['CacheSubnetGroupName']
  return first


def check(name,SR):
  status='status'
  i=0
  while status != 'available':
    time.sleep(10)
    source = boto3.client('elasticache', aws_access_key_id=keyID, aws_secret_access_key=secA, region_name=SR)
    describe = source.describe_cache_clusters(CacheClusterId=name)['CacheClusters']
    cacheDes = describe[0]
    status = cacheDes['CacheClusterStatus']
    print(status)
    i=i+1
    if i == 128:
      break
      print("timedout")

#SR = input("What region?  ")
#name = input("what is the name of the redis cache?  ")
#type = input("What is the cache type?  ")

SA = 's'
SR = 'us-east-1'
name = 'longterm'
type = 'cache.t2.medium'

acc(SA)
keyID = a.keyID
secA = a.secA

CacheSNGCheck(SR)
csng = first

deleteR(name,SR)
createR(type,name,csng,SR)
check(name,SR)
print("done!!!!!!!!!!!1")










