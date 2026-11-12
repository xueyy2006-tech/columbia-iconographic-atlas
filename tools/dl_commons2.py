import json, os, time, hashlib, io, requests, collections, re
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
R=[x for x in json.load(open("records.json",encoding="utf-8")) if x["src"]=="Commons"]
s=requests.Session(); s.headers["User-Agent"]="ColumbiaIconographySurvey/1.0 (academic image-history research; python-requests)"
st=collections.Counter()
def out(r): return "cache/"+hashlib.sha1((r["src"]+"|"+r["sid"]).encode("utf-8")).hexdigest()[:16]+".jpg"
def save(content,o):
    im=Image.open(io.BytesIO(content)); im.load()
    if (im.format or "")=="JPEG" and max(im.size)<=4000: open(o,"wb").write(content)
    else:
        if im.mode not in("RGB","L"): im=im.convert("RGB")
        im.thumbnail((3000,3000)); im.save(o,"JPEG",quality=90)
todo=[r for r in R if not os.path.exists(out(r))]
pace=5
for n,r in enumerate(todo):
    u=r["img"][0].split("?")[0]; ok=False
    for attempt in range(6):
        try:
            q=s.get(u,timeout=120)
            if q.status_code==200 and len(q.content)>3000:
                save(q.content,out(r)); ok=True; break
            st["http%s"%q.status_code]+=1
            if q.status_code==404: break
            ra=int(q.headers.get("retry-after") or 10)
            time.sleep(min(ra,900)+5*(attempt+1))
        except Exception as e:
            st["exc"]+=1; time.sleep(10)
    st["ok" if ok else "fail"]+=1
    if n%10==0: print(n,len(todo),dict(st),flush=True)
    time.sleep(pace)
print("DONE",dict(st))
