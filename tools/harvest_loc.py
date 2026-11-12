import requests, json, time, sys
H={"User-Agent":"Mozilla/5.0 (research image survey script)"}
QS=["Columbia (Symbolic character)","Liberty (Symbolic character)","America (Symbolic character)","Brother Jonathan (Symbolic character)","Uncle Sam Columbia","Columbia allegory","Columbia allegorical","goddess of liberty","genius of America","America allegorical figure","America Indian princess","America Indian woman Britannia","Britannia America daughter","Miss Columbia","Columbia Britannia","four continents America allegory","Minerva America","apotheosis Washington","temple of liberty","Columbia weeping","Columbia mourning","Columbia eagle shield","Liberty cap pole female figure","Liberty goddess eagle","Hail Columbia","Columbia gem of the ocean","Columbia Puck","Columbia Judge cartoon","Columbia Nast","Columbia poster war","female figure representing America","woman representing America","America personified","Liberty personified","British cartoon America Indian","colonies America female figure","Columbia suffrage","Columbia Lincoln","Columbia Washington","Columbia Confederacy","Columbia Cuba","Columbia Philippines","Columbia immigrants","Columbian Exposition Columbia","Columbia Statue of Liberty","Freedom statue Capitol Crawford","Liberty flag woman 1860","Union allegory woman flag Civil War","Columbia secession","Columbia slavery","Columbia school","Columbia South reconstruction"]
out={}
for q in QS:
    sp=1
    while True:
        for attempt in range(4):
            try:
                r=requests.get("https://www.loc.gov/pictures/search/",params={"q":q,"fo":"json","c":100,"sp":sp},headers=H,timeout=60)
                if r.status_code==200: break
                print("status",r.status_code,q,sp,flush=True); time.sleep(20)
            except Exception as e:
                print("err",e,flush=True); time.sleep(15)
        else: break
        try: j=r.json()
        except Exception: break
        res=j.get("results",[])
        for x in res:
            pk=str(x.get("pk"))
            if pk in out: out[pk]["queries"].append(q)
            else:
                x["queries"]=[q]; out[pk]=x
        pages=j.get("pages",{}).get("total",1)
        print(q,sp,"/",pages,"hits",j.get("search",{}).get("hits"),"total",len(out),flush=True)
        if sp>=pages or sp>=6: break
        sp+=1; time.sleep(3.5)
    time.sleep(3.5)
    json.dump(out,open("loc_raw.json","w",encoding="utf-8"),ensure_ascii=False)
print("DONE",len(out))
