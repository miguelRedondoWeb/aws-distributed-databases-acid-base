import boto3
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

REGIONS={"irlanda":("eu-west-1","ej7-hashtags-irlanda"),"virginia":("us-east-1","ej7-hashtags-virginia"),"tokio":("ap-northeast-1","ej7-hashtags-tokio")}
out=Path(__file__).resolve().parents[2]/"results"
out.mkdir(exist_ok=True)

def run(name,top_n):
    total=Counter();received={};errors={}
    for label,(region,fn) in REGIONS.items():
        try:
            client=boto3.Session(profile_name="terraform",region_name=region).client("lambda")
            rsp=client.invoke(FunctionName=fn,InvocationType="RequestResponse",Payload=json.dumps({"top_n":top_n}).encode())
            payload=json.loads(rsp["Payload"].read())
            if rsp.get("FunctionError") or "counts" not in payload:
                raise RuntimeError(str(payload))
            received[label]=payload
            total.update(payload["counts"])
        except Exception as exc:
            errors[label]=f"{type(exc).__name__}: {exc}"
    ranking=sorted(total.items(),key=lambda x:(-x[1],x[0]))
    summary={"utc":datetime.now(timezone.utc).isoformat(),"escenario":name,
       "regiones_respondieron":list(received),"regiones_fallaron":errors,
       "parcial":len(received)!=3,"ganador":ranking[0] if ranking else None,
       "ranking":ranking,"detalle_regional":received}
    (out/f"base_{name}.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"{name}: {summary['ganador']} | parcial={summary['parcial']} | regiones={list(received)} | errores={list(errors)}")
    return summary

if __name__=="__main__":
    run("completo",None)
    run("top2",2)
    run("top3",3)
    print("Para simular caída: aws lambda put-function-concurrency --function-name ej7-hashtags-tokio --reserved-concurrent-executions 0 --region ap-northeast-1 --profile terraform")
    input("Tras aplicar concurrencia 0, pulsa Enter para ejecutar escenario parcial...")
    run("region_caida",None)
    print("RESTAURA: aws lambda delete-function-concurrency --function-name ej7-hashtags-tokio --region ap-northeast-1 --profile terraform")
