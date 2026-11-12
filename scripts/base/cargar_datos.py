import boto3
import json
from pathlib import Path
root=Path(__file__).resolve().parents[2]/"data"
regions={"irlanda":("eu-west-1","ej7-mensajes-irlanda"),"virginia":("us-east-1","ej7-mensajes-virginia"),"tokio":("ap-northeast-1","ej7-mensajes-tokio")}
for label,(region,table_name) in regions.items():
    s=boto3.Session(profile_name="terraform",region_name=region)
    table=s.resource("dynamodb").Table(table_name)
    items=json.loads((root/f"mensajes_{label}.json").read_text(encoding="utf-8"))
    with table.batch_writer() as batch:
        for item in items: batch.put_item(Item=item)
    # Strongly consistent scan; pages fully processed; eventually consistent by default unless requested.
    count=0; kwargs={"Select":"COUNT","ConsistentRead":True}
    while True:
        r=table.scan(**kwargs);count+=r["Count"]
        if "LastEvaluatedKey" not in r: break
        kwargs["ExclusiveStartKey"]=r["LastEvaluatedKey"]
    print(f"{label} {region}: {count} mensajes")
    assert count==100
