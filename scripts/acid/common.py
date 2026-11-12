import boto3
import json
from pathlib import Path
import pymysql

PROFILE = "terraform"
REGION = "eu-south-2"
INSTANCE = "ej7-banco-mysql"

def connection():
    session = boto3.Session(profile_name=PROFILE, region_name=REGION)
    db = session.client("rds").describe_db_instances(DBInstanceIdentifier=INSTANCE)["DBInstances"][0]
    secret_arn = db["MasterUserSecret"]["SecretArn"]
    secret = json.loads(session.client("secretsmanager").get_secret_value(SecretId=secret_arn)["SecretString"])
    ca = Path(__file__).resolve().parents[2]/"certs"/"global-bundle.pem"
    if not ca.exists():
        raise FileNotFoundError(f"Descarga el certificado RDS en {ca}")
    return pymysql.connect(host=db["Endpoint"]["Address"],port=db["Endpoint"]["Port"],
       user=secret["username"],password=secret["password"], database="banco",
       ssl_ca=str(ca), ssl_verify_cert=True, ssl_verify_identity=True,
       connect_timeout=5, read_timeout=10, write_timeout=10, autocommit=False)
