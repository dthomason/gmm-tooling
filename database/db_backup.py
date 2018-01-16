import datetime
import boto3
import awsinfo

#naming the fcdump file
CDate=str(datetime.datetime.now().day)
CHour=str(datetime.datetime.now().hour)
CurrentDate = CDate + '-' + CHour

name = ('BigMath%s.fcdump' % CurrentDate)

a=awsinfo

#variables
a.AccountSwitch('p')
keyID=a.keyID
secA=a.secA
source_region='us-east-1'
#command to upload a file to a specific S3 bucket
s3 = boto3.resource('s3', aws_access_key_id=keyID, aws_secret_access_key=secA, region_name=source_region)
s3.meta.client.upload_file('/home/ec2-user/_dbrep/dbplace/BigMath.fcdump', 'gmm.prod.fcdumps', name)
print("uploading to S3")