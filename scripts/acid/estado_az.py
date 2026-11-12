import boto3
from datetime import datetime, timezone
r=boto3.Session(profile_name="terraform",region_name="eu-south-2").client("rds")
i=r.describe_db_instances(DBInstanceIdentifier="ej7-banco-mysql")["DBInstances"][0]
print(datetime.now(timezone.utc).isoformat(), "AZ primaria:",i["AvailabilityZone"],"MultiAZ:",i["MultiAZ"],"Estado:",i["DBInstanceStatus"])
