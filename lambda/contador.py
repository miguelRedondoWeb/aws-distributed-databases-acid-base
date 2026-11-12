import os
from collections import Counter
import boto3


def handler(event, context):
    table = boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])
    counts = Counter()
    count_items = 0
    kwargs = {"ProjectionExpression": "hashtags"}
    while True:
        resp = table.scan(**kwargs)
        for item in resp["Items"]:
            count_items += 1
            counts.update(item.get("hashtags", []))
        if "LastEvaluatedKey" not in resp:
            break
        kwargs["ExclusiveStartKey"] = resp["LastEvaluatedKey"]
    top_n = event.get("top_n") if event else None
    ranking = sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))
    if top_n is not None:
        ranking = ranking[:int(top_n)]
    return {"table": os.environ["TABLE_NAME"], "messages": count_items, "counts": dict(ranking), "top_n": top_n}
