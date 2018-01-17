$dbPW=
$dbU=

PGPASSWORD=$dbPW pg_dump --host gmm-staging-db.ckhau7urrr2b.us-east-1.rds.amazonaws.com --port 5432 -U $dbU -f /home/ec2-user/BigMath.fcdump BigMath -Fc
