import json
from pathlib import Path
root=Path(__file__).resolve().parents[2]/"data"
# 100 messages per region. #cloud is third locally (25) but first globally (75).
# Region-specific top: 36, second: 30, shared: 25, fourth: 9.
regions={
 "irlanda": [("#irishmusic",36),("#dublin",30),("#cloud",25),("#cork",9)],
 "virginia": [("#virginia",36),("#bluegrass",30),("#cloud",25),("#richmond",9)],
 "tokio": [("#anime",36),("#ramen",30),("#cloud",25),("#shibuya",9)]}
for region,groups in regions.items():
    posts=[]
    for tag,n in groups:
        for _ in range(n):
            i=len(posts)+1
            posts.append({"id":f"{region}-{i:03}","region":region,"texto":f"Mensaje {i} de {region} {tag}","hashtags":[tag]})
    assert len(posts)==100
    (root/f"mensajes_{region}.json").write_text(json.dumps(posts,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(region,len(posts),groups)
