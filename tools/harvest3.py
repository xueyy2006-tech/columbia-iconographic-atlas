import requests, json, time
H={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36"}
jcb={}
for q in ["America allegory","allegorical figure America","America personified","America Indian woman allegorical","Britannia America","Columbia","Liberty America allegorical","four continents","America female figure","colonies cartoon America Indian","emblematic America","Liberty cap America"]:
    os_=0
    while os_<400:
        try:
            r=requests.get("https://jcb.lunaimaging.com/luna/servlet/as/search",params={"q":q,"os":os_,"bs":100},headers=H,timeout=90); j=r.json()
        except Exception as e: print("err",e); break
        res=j.get("results",[])
        for x in res:
            k=x.get("id")
            if k in jcb: jcb[k]["queries"].append(q)
            else: x["queries"]=[q]; jcb[k]=x
        print("JCB",q,os_,j.get("totalResults"),len(jcb),flush=True)
        os_+=100
        if os_>=int(j.get("totalResults",0)): break
        time.sleep(1.5)
json.dump(jcb,open("jcb_raw.json","w",encoding="utf-8"),ensure_ascii=False)
dc={}
for q in ["Columbia allegory","Columbia personification","Columbia symbolic","Goddess of Liberty","Liberty allegory America","America allegory","Brother Jonathan","Miss Columbia","Hail Columbia","Columbia Uncle Sam"]:
    page=1
    while page<=4:
        try:
            r=requests.get("https://www.digitalcommonwealth.org/search.json",params={"q":q,"per_page":100,"page":page},headers=H,timeout=90); j=r.json()
        except Exception as e: print("err",e); break
        for x in j.get("data",[]):
            a=x["attributes"]; k=x["id"]
            y={f:a.get(f) for f in ["id","title_info_primary_tsi","genre_basic_ssim","genre_specific_ssim","date_tsim","date_start_dtsi","name_tsim","name_role_tsim","subject_topic_tsim","subject_facet_ssim","abstract_tsi","institution_name_ssi","physical_location_ssim","exemplary_image_ssi","exemplary_image_iiif_bsi","rights_ssim","license_ssm","reuse_allowed_ssi","identifier_iiif_manifest_ssi","collection_name_ssim"]}
            if k in dc: dc[k]["queries"].append(q)
            else: y["queries"]=[q]; dc[k]=y
        tp=j.get("meta",{}).get("pages",{}).get("total_pages",1)
        print("DC",q,page,tp,len(dc),flush=True)
        if page>=tp: break
        page+=1; time.sleep(1.5)
json.dump(dc,open("dc_raw.json","w",encoding="utf-8"),ensure_ascii=False)
x=next(iter(jcb.values())); print(json.dumps(x,ensure_ascii=False)[:2500])
x=next(iter(dc.values())); print(json.dumps(x,ensure_ascii=False)[:1500])
