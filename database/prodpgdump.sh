PGPASSWORD=$dbPW pg_dump --host prod-static-i.cblcix4wsn1v.us-east-1.rds.amazonaws.com --port 5432 -U $dbU -f home/ec2-user/BigMath.fcdump BigMath -Fc