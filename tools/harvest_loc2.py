import requests, json, time
H={"User-Agent":"Mozilla/5.0 (research image survey script)"}
QS=[("Columbia",12),("Columbia symbolic character",4),("America represented as Indian",4),("America Indian woman allegorical",3),("personification of America",3),("female figure representing America",3),("female figure representing Liberty",4),("figure of Liberty",5),("goddess of Liberty",3),("Liberty personified",3),("Britannia America",4),("Brother Jonathan",3),("female figure Union allegorical",3),("allegorical America",5),("Columbia Uncle Sam",4),("genius of America",2),("Liberty cap pole female",3),("America Indian princess",2),("colonies Indian Britannia cartoon",3),("Miss Columbia",2),("allegorical print United States",4),("temple of Liberty",2),("apotheosis",2),("emblematic America",3),("Liberty holding flag shield eagle",3)]
out={}
for q,maxp in QS:
    for sp in range(1,maxp+1):
        r=None
        for attempt in range(4):
            try:
                r=requests.get("https://www.loc.gov/photos/",params={"q":q,"fo":"json","c":150,"sp":sp,"dates":"1600/1930","fa":"online-format:image"},headers=H,timeout=90)
                if r.status_code==200: break
                print("status",r.status_code,q,sp,flush=True); time.sleep(30)
            except Exception as e: print("err",e,flush=True); time.sleep(15)
        if r is None or r.status_code!=200: break
        try: j=r.json()
        except Exception: break
        res=j.get("results",[])
        for x in res:
            k=x.get("id")
            y={f:x.get(f) for f in ["id","title","date","dates","description","subject","contributor","original_format","image_url","partof","item","url","number_lccn"]}
            if k in out: out[k]["queries"].append(q)
            else: y["queries"]=[q]; out[k]=y
        tot=j.get("pagination",{}).get("total",1)
        print(q,sp,"/",tot,"of",j.get("pagination",{}).get("of"),"total",len(out),flush=True)
        time.sleep(4)
        if sp>=tot: break
    json.dump(out,open("loc2_raw.json","w",encoding="utf-8"),ensure_ascii=False)
print("DONE",len(out))
