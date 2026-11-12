import requests, json, time, os, re
H={"User-Agent":"Mozilla/5.0 (research image survey script)"}
R=json.load(open("records.json",encoding="utf-8"))
out=json.load(open("loc_place.json",encoding="utf-8")) if os.path.exists("loc_place.json") else {}
ids=[r["sid"] for r in R if r["src"]=="LOC"]
# Commons files carrying an LCCN
for r in R:
    if r["src"]=="Commons":
        m=re.search(r"LCCN(\d{8,10})",r["sid"])
        if m: ids.append(m.group(1))
ids=[i for i in dict.fromkeys(ids) if i not in out]
print(len(ids),flush=True)
for n,pk in enumerate(ids):
    for a in range(3):
        try:
            r=requests.get("https://www.loc.gov/pictures/item/%s/?fo=json"%pk,headers=H,timeout=60)
            if r.status_code==200:
                it=r.json().get("item",{})
                out[pk]={"cp":it.get("created_published"),"summary":(it.get("summary") or "")[:800] if isinstance(it.get("summary"),str) else it.get("summary"),"creators":[c.get("title") for c in (it.get("creators") or [])],"notes":it.get("notes")}
                break
            if r.status_code==404: out[pk]={}; break
            time.sleep(20)
        except Exception as e: time.sleep(10)
    if n%20==0:
        print(n,len(ids),flush=True); json.dump(out,open("loc_place.json","w",encoding="utf-8"),ensure_ascii=False)
    time.sleep(3.2)
json.dump(out,open("loc_place.json","w",encoding="utf-8"),ensure_ascii=False); print("DONE",len(out))
