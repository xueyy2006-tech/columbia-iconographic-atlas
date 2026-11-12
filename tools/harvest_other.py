import requests, json, time, re
H={"User-Agent":"Mozilla/5.0 (research image survey script)"}
A="https://commons.wikimedia.org/w/api.php"
def api(**p):
    p["format"]="json"
    for i in range(4):
        try:
            r=requests.get(A,params=p,headers=H,timeout=60)
            if r.ok: return r.json()
        except Exception as e: print("err",e,flush=True)
        time.sleep(5)
    return {}
SKIP={"Category:Things named after Columbia","Category:Columbia Pictures logos","Category:Uncle Sam","Category:Statue of Liberty","Category:Statue of Liberty National Monument","Category:Liberty Enlightening the World"}
roots=[("Category:Columbia (personification)",3),("Category:Personifications of the United States",1),("Category:Allegories of the United States",1),("Category:Allegories of America",2),("Category:Allegories of the Americas",2),("Category:Personifications of the Americas",2),("Category:Brother Jonathan",1),("Category:Allegories of liberty in the United States",1),("Category:American revolution cow commerce cartoon (1778)",0),("Category:American revolution cow commerce cartoon (1781)",0)]
files={}; seen=set()
def walk(cat,depth,root):
    if cat in seen or cat in SKIP: return
    seen.add(cat)
    cont={}
    while True:
        j=api(action="query",list="categorymembers",cmtitle=cat,cmlimit=500,cmtype="file|subcat",**cont)
        for m in j.get("query",{}).get("categorymembers",[]):
            if m["ns"]==6:
                files.setdefault(m["title"],{"cats":[],"root":root})["cats"].append(cat)
            elif m["ns"]==14 and depth>0:
                t=m["title"]
                if re.search(r"Uncle Sam|Statue of Liberty|Pictures|named after|coins of|Seated Liberty|Morgan|dollar|Liberty Bell|Videos|Audio|Freedom Tower",t): continue
                walk(t,depth-1,root)
        if "continue" in j: cont=j["continue"]
        else: break
    print(cat,len(files),flush=True)
for c,d in roots: walk(c,d,c)
# search-based extras
for s in ['"Columbia" personification cartoon','Columbia Puck cartoon','Columbia Judge magazine cartoon','Columbia Thomas Nast','"Miss Columbia"','Columbia Harper\'s Weekly','"Columbia" allegory engraving']:
    j=api(action="query",list="search",srsearch=s+" filetype:bitmap",srnamespace=6,srlimit=200)
    for m in j.get("query",{}).get("search",[]):
        files.setdefault(m["title"],{"cats":[],"root":"search:"+s})
    print(s,len(files),flush=True)
titles=[t for t in files if re.search(r"\.(jpe?g|png|tiff?|gif)$",t,re.I)]
for i in range(0,len(titles),40):
    j=api(action="query",prop="imageinfo",titles="|".join(titles[i:i+40]),iiprop="url|size|extmetadata|mime",iiurlwidth=1600,iiextmetadatafilter="ImageDescription|Artist|DateTimeOriginal|LicenseShortName|Credit|ObjectName|Categories")
    for p in j.get("query",{}).get("pages",{}).values():
        if "imageinfo" in p: files[p["title"]]["ii"]=p["imageinfo"][0]
    time.sleep(0.5)
json.dump({t:files[t] for t in titles},open("commons_raw.json","w",encoding="utf-8"),ensure_ascii=False)
print("COMMONS",len(titles))
# MET
ids=set()
for q in ["Columbia allegory","Columbia personification","Columbia America figure","America allegory Indian","Liberty goddess America","Brother Jonathan","Hail Columbia","Genius of America","America Britannia","Columbia"]:
    try:
        r=requests.get("https://collectionapi.metmuseum.org/public/collection/v1.1/search",params={"q":q,"isPublicDomain":"true","hasImages":"true","size":150},headers=H,timeout=60).json()
        got=r.get("objectIDs") or []; print("MET",q,r.get("total"),len(got),flush=True); ids.update(got[:150])
    except Exception as e: print("meterr",e)
met={}
for n,i in enumerate(sorted(ids)):
    try:
        r=requests.get(f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{i}",headers=H,timeout=40)
        if r.ok:
            o=r.json()
            if o.get("isPublicDomain") and o.get("primaryImage"): met[i]={k:o.get(k) for k in ["objectID","title","artistDisplayName","objectDate","objectBeginDate","medium","classification","objectName","department","culture","primaryImage","primaryImageSmall","objectURL","creditLine","accessionNumber","tags"]}
    except Exception as e: print("e",e)
    time.sleep(0.25)
json.dump(met,open("met_raw.json","w",encoding="utf-8"),ensure_ascii=False); print("MET objs",len(met),flush=True)
# AIC
aic={}
for q in ["Columbia allegory","Columbia America personification","America allegory Indian princess","Liberty goddess America","Brother Jonathan","Britannia America"]:
    r=requests.get("https://api.artic.edu/api/v1/artworks/search",params={"q":q,"limit":60,"fields":"id,title,date_display,date_start,artist_display,is_public_domain,image_id,classification_title,medium_display,main_reference_number"},headers=H,timeout=60).json()
    for x in r.get("data",[]):
        if x.get("is_public_domain") and x.get("image_id"): aic[x["id"]]=x
json.dump(aic,open("aic_raw.json","w",encoding="utf-8"),ensure_ascii=False); print("AIC",len(aic),flush=True)
# SI
si={}
for q in ['Columbia AND allegory','"Columbia" AND personification','"Miss Columbia"','Columbia AND "Uncle Sam"','"Goddess of Liberty"','America AND allegory AND print','"Brother Jonathan"']:
    try:
        r=requests.get("https://api.si.edu/openaccess/api/v1.0/search",params={"q":q+' AND online_media_type:"Images"',"api_key":"DEMO_KEY","rows":200},headers=H,timeout=90)
        print("SI",q,r.status_code,flush=True)
        if r.ok:
            for row in r.json()["response"]["rows"]: si[row["id"]]=row
    except Exception as e: print("sierr",e)
    time.sleep(3)
json.dump(si,open("si_raw.json","w",encoding="utf-8"),ensure_ascii=False); print("SI",len(si))
