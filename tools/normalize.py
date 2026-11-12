import json, re, os, collections, html

def load(f):
    return json.load(open(f, encoding="utf-8")) if os.path.exists(f) else {}

PLACE = re.compile(r"District of Columbia|Columbia,? (S\.? ?C|South Carolina|Tenn|Mo\b|Missouri|Pa\b|Penn|Ky|Calif|Ohio)|Columbia (River|University|College|Univ|Heights|Road|Rd|Pike|Bridge|Hospital|Institution|Records|Phonograph|Graphophone|Broadcasting|Pictures|Theat|Bicycle|Club|Gorge|Basin|County|Glacier|Falls|Mills|Hotel|Street|Avenue|Gas|Railway|Railroad|Yacht|Steam|Brewery|Law|Country|Park|Island|Plateau|Highway|Building|Historical|Athletic)|British Columbia|(yacht|schooner|steamer|ship|shuttle|sloop|cruiser|U\.?S\.?S\.?|balloon|locomotive) [\"']?Columbia|Columbia Univ|Columbias?,? (yacht|Shamrock)|Shamrock", re.I)

def year_of(s):
    if not s:
        return None
    m = re.search(r"\b(1[4-9]\d\d|20[0-2]\d)\b", str(s))
    return int(m.group(1)) if m else None

def strip(s):
    s = html.unescape(re.sub(r"<[^>]+>", " ", s or ""))
    return re.sub(r"\s+", " ", s).strip()

def cyear(name, em):
    def ys(t):
        return [int(v) for v in re.findall(r"(?<![\d.#])(1[5-9]\d\d|20[0-2]\d)(?!\d)", re.sub(r"(no|No|nr|v|vol)\.? ?\d+", " ", t)) if 1490 <= int(v) <= 2026]
    dt = ys(em.get("DateTimeOriginal", ""))
    if dt and dt[0] <= 1950:
        return dt[0]
    nm = ys(name)
    if nm:
        return min(nm)
    ds = ys(em.get("ImageDescription", "")[:250])
    if ds:
        return ds[0]
    return dt[0] if dt else None

recs = []
def add(**k):
    recs.append(k)

FIG = re.compile(r"Columbia \(Symbolic|Liberty \(personified\)|Liberty--Symbolic|United States--Symbolic|Union \(Personified\)|Allegorical figures of America|Temple of Liberty|Brother Jonathan|America \(Symbolic", re.I)
COLFIG = re.compile(
    r"\b(Miss|Mrs\.?|Dame|Mother|fair|weeping|young|our) Columbia\b|\bColumbia'?s\b"
    r"|\bColumbia (holding|standing|seated|sitting|wearing|weeping|mourning|kneeling|leading|welcom|crown|offering|presenting|greeting|pointing|handing|looking|and (Uncle Sam|Britannia|John Bull|Brother Jonathan)|to (her|John Bull|Britannia|Uncle Sam))"
    r"|(Uncle Sam|Britannia|John Bull|Brother Jonathan) and Columbia|Hail,? Columbia|Columbia,? the gem"
    r"|(figure|personification|goddess|allegor\w+) of (Columbia|America|Liberty|the Union|the United States|the Republic)"
    r"|(female|allegorical|symbolic) figures? (of|representing|symbolizing|as|labeled|personifying) [\"']?(Columbia|America|Liberty|the Union|the United States|the Republic)"
    r"|(Columbia|America|Liberty|United States|the Union|Republic)[^.]{0,50}(personifi|represented as|depicted as|as an? (Indian|woman|female|goddess)|allegorical figure|female figure)"
    r"|Goddess of Liberty|Genius of (America|Liberty|Columbia)"
    r"|America[^.]{0,30}Indian (princess|queen|woman|maiden)|Indian (princess|queen|woman|maiden)[^.]{0,40}(representing|symboli|America|colonies)", re.I)

# ---------- LOC pictures
loc1 = load("loc_raw.json")
seen = set()
for pk, x in loc1.items():
    img = (x.get("image") or {}).get("full") or ""
    if not img or "notdigitized" in img or "500x500" in img or "grouprecord" in img:
        continue
    subs = " | ".join(x.get("subjects") or [])
    t = x.get("title") or ""
    y = year_of(x.get("created_published_date"))
    med = x.get("medium") or ""
    photo = bool(re.search(r"negative|photograph|transparency|slide|stereograph", med, re.I))
    keep = bool(FIG.search(subs) or FIG.search(t))
    if not keep and re.search(r"Britannia \(Symbolic", subs) and (y or 9999) < 1830:
        keep = True
    if not keep and COLFIG.search(t) and not PLACE.search(t) and not photo:
        keep = True
    if not keep and re.search(r"Allegor|Symbols", subs) and re.search(r"America|Liberty|Union|Columbia|Republic|United States|Britannia|Colonies", t) and not photo and (y or 0) < 1930:
        keep = True
    if not keep:
        continue
    seen.add(pk)
    add(src="LOC", sid=pk, title=t.strip(" /"), creator=x.get("creator") or "", date=x.get("created_published_date") or "", year=y, medium=med, desc="", subjects=subs,
        repo="Library of Congress, Prints & Photographs Division", call=x.get("call_number") or "", url="https://www.loc.gov/pictures/item/%s/" % pk,
        img=[img.replace("r.jpg", "v.jpg"), img], lic="见 LOC Rights Advisory（多为无已知限制）")

# ---------- LOC photos API
loc2 = load("loc2_raw.json")
for k, x in loc2.items():
    pk = k.rstrip("/").split("/")[-1]
    if pk in seen:
        # enrich description
        d = " ".join(x.get("description") or [])
        for r in recs:
            if r["src"] == "LOC" and r["sid"] == pk and "|" in d:
                r["desc"] = strip(d.split("|", 1)[1])[:700]
        continue
    ims = [u.split("#")[0] for u in (x.get("image_url") or [])]
    ims = [u for u in ims if re.search(r"\.(jpg|jpeg)$", u) and "150px" not in u]
    if not ims:
        continue
    t = x.get("title") or ""
    d = " ".join(x.get("description") or [])
    subs = " | ".join(x.get("subject") or [])
    y = year_of(x.get("date"))
    T = t + " . " + d
    keep = ("columbia (symbolic character)" in subs) or ("liberty (personified)" in subs) or "brother jonathan" in T.lower()
    if not keep and COLFIG.search(T) and not PLACE.search(t):
        keep = True
    if not keep:
        continue
    if re.search(r"statue of liberty", t, re.I) and not re.search(r"columbia", T, re.I):
        continue
    if re.search(r"DANIELS|Trademark registration", t):
        continue
    seen.add(pk)
    med = d.split("|")[0].strip() if "|" in d else ""
    add(src="LOC", sid=pk, title=t, creator="; ".join(x.get("contributor") or []), date=x.get("date") or "", year=y, medium=med,
        desc=strip(d.split("|", 1)[1] if "|" in d else d)[:700], subjects=subs, repo="Library of Congress", call="",
        url=k.replace("http://", "https://"), img=[ims[-1]] + ims[::-1], lic="见 LOC Rights Advisory（多为无已知限制）")

# ---------- Commons
cm = load("commons_raw.json")
percat = collections.Counter()
for t, x in cm.items():
    ii = x.get("ii")
    if not ii or not ii.get("mime", "").startswith("image/") or "svg" in ii.get("mime", ""):
        continue
    if ii.get("width", 0) < 500:
        continue
    em = {k: strip(v.get("value", "")) for k, v in (ii.get("extmetadata") or {}).items()}
    name = t.replace("File:", "")
    cats = x.get("cats") or []
    if not cats:
        if not re.search(r"Columbia", name) or PLACE.search(name) or re.search(r"Columbia[ _](Pictures|shuttle)|Space Shuttle|STS-|Colombia", name):
            continue
        T = name + " " + em.get("ImageDescription", "")
        if not (COLFIG.search(T) or re.search(r"cartoon|Puck|Judge|Nast|Harper|allegor|personif", T, re.I)):
            continue
    else:
        c0 = cats[0]
        if re.search(r"Monument|Memorial|Statue|by |Sculptures|Fountain|Park|Building|Capitol|Pediment", c0) and c0 != "Category:Sculptures of Columbia":
            percat[c0] += 1
            if percat[c0] > 3:
                continue
        if re.search(r"bald eagle|Southern belles|Sino-American|Duratsky|rivers in|Argentin|Colombia|Mexico|Panchito|Catete|Tamarita|Peru|Ecuador|Canada|Brazil|Brasil|Alma Mater|Quadriga|Memorial Cemetery|West Coast Memorial|Littlefield|Commonwealth \(|Chile|Venezuela|Uruguay|Cuba", " ".join(cats)):
            continue
    add(src="Commons", sid=name, title=re.sub(r"\.(jpe?g|png|tiff?|gif)$", "", name, flags=re.I).replace("_", " "), creator=em.get("Artist", "")[:150],
        date=em.get("DateTimeOriginal", "")[:60], year=cyear(name, em), medium="", desc=em.get("ImageDescription", "")[:600],
        subjects=" | ".join(c.replace("Category:", "") for c in cats),
        repo="Wikimedia Commons" + (("（来源：" + em["Credit"][:80] + "）") if em.get("Credit") else ""), call="", url=ii.get("descriptionurl", ""),
        img=[ii.get("thumburl") or ii["url"], ii["url"]], lic=em.get("LicenseShortName", ""))

# ---------- JCB
for k, x in load("jcb_raw.json").items():
    fv = {}
    for f in x.get("fieldValues", []):
        for a, b in f.items():
            fv[a] = " ; ".join(map(str, b))
    T = " . ".join(fv.get(n, "") for n in ["Title", "Image title", "Narrative description", "Description", "Commentary", "Subject", "Subject headings", "Notes"])
    if re.search(r"British Columbia|Botany|Alaska|Catafalque|Funeral", T):
        continue
    if not re.search(r"allegor|personif|Emblems--America|Britan+ia|America[^.]{0,60}(as an? |Indian (woman|princess|queen|maiden|girl)|female|woman|daughter)|(Indian (woman|princess|queen|maiden)|female figure|woman|Miss)[^.]{0,40}(America|colonies)|Liberty|Columbia", T, re.I):
        continue
    if not re.search(r"America|Columbia|United States|colon|Liberty", T, re.I):
        continue
    if not x.get("urlSize4"):
        continue
    title = fv.get("Title") or fv.get("Image title") or x.get("displayName", "")
    date = fv.get("Date") or fv.get("Image date") or fv.get("Normalized date", "")
    coll = "JCB Political Cartoons" if "JCBMAPS~2" in k else ("JCB Map Collection" if "JCBMAPS~1" in k else "JCB Archive of Early American Images")
    desc = (fv.get("Narrative description") or fv.get("Description") or fv.get("Commentary", ""))[:600]
    if fv.get("Source title"):
        desc += " 〔出处：" + fv["Source title"][:200] + "〕"
    add(src="JCB", sid=k, title=title, creator=fv.get("Creators") or fv.get("Source creator") or fv.get("Creator", ""), date=date,
        year=year_of(fv.get("Normalized date") or date), medium=fv.get("Image technique") or fv.get("Technique", ""), desc=desc,
        subjects=fv.get("Subject") or fv.get("Subject headings", ""), repo="John Carter Brown Library (" + coll + ")",
        call=fv.get("Call number") or fv.get("Accession number", ""), url="https://jcb.lunaimaging.com/luna/servlet/detail/" + k,
        img=[x["urlSize4"], x.get("urlSize3")], lic="JCB：公开使用，引用请注明馆藏", coll=coll)

# ---------- Digital Commonwealth
for k, x in load("dc_raw.json").items():
    t = x.get("title_info_primary_tsi") or ""
    subs = " | ".join(x.get("subject_facet_ssim") or [])
    ab = x.get("abstract_tsi") or ""
    y = year_of(x.get("date_start_dtsi")) or year_of(" ".join(x.get("date_tsim") or []))
    if not x.get("exemplary_image_ssi") or (y or 0) > 1935:
        continue
    T = t + " . " + ab
    keep = bool(re.search(r"Columbia \(Symbolic|Liberty \(Symbolic|Brother Jonathan", subs + t, re.I)) or bool(COLFIG.search(T) and not PLACE.search(t))
    if not keep and re.search(r"Allegor|Symbols|Personif", subs) and re.search(r"America|Liberty|Columbia|Union|United States", T + subs):
        keep = True
    if not keep:
        continue
    g = " ; ".join((x.get("genre_specific_ssim") or []) + (x.get("genre_basic_ssim") or []))
    e = x["exemplary_image_ssi"]
    add(src="DC", sid=k, title=t, creator=" ; ".join(x.get("name_tsim") or []), date=" ".join(x.get("date_tsim") or []), year=y, medium=g, desc=ab[:600], subjects=subs,
        repo=(x.get("institution_name_ssi") or "Digital Commonwealth") + "（经 Digital Commonwealth）", call="", url="https://www.digitalcommonwealth.org/search/" + k,
        img=["https://iiif.digitalcommonwealth.org/iiif/2/%s/full/1400,/0/default.jpg" % e, "https://bpldcassets.blob.core.windows.net/derivatives/images/%s/image_access_800.jpg" % e],
        lic=x.get("reuse_allowed_ssi") or "")

# ---------- MET
for k, x in load("met_raw.json").items():
    tags = " | ".join(t.get("term", "") for t in (x.get("tags") or []))
    t = x.get("title") or ""
    if (x.get("objectBeginDate") or 0) < 1490:
        continue
    cls = (x.get("classification") or "") + " " + (x.get("objectName") or "")
    keep = bool(COLFIG.search(t) and not PLACE.search(t))
    if not keep and re.search(r"\bColumbia\b", t) and not PLACE.search(t) and re.search(r"Print|Drawing|Sculpture|Medal|Textile|Ceramic|Glass", cls):
        keep = True
    if not keep and re.search(r"Brother Jonathan|Britannia.*America|America.*Britannia|Liberty.*(America|Washington|Eagle)|Allegory of America|America,? from|Four Continents|Apotheosis of (Washington|Franklin)", t, re.I):
        keep = True
    if re.search(r"U\.S\. Columbia|United States of Columbia|River Scene|Colombia", t) or (re.search(r"Africa|Asia|Europe", t) and not re.search(r"America", t)):
        keep = False
    if not keep:
        continue
    add(src="MET", sid=str(k), title=t, creator=x.get("artistDisplayName") or "", date=x.get("objectDate") or "", year=year_of(x.get("objectDate")) or x.get("objectBeginDate"),
        medium=x.get("medium") or "", desc="", subjects=tags + " | " + cls, repo="The Metropolitan Museum of Art", call=x.get("accessionNumber") or "",
        url=x.get("objectURL") or "", img=[x.get("primaryImageSmall"), x.get("primaryImage")], lic="CC0 (Met Open Access)")

# ---------- AIC
for k, x in load("aic_raw.json").items():
    t = x.get("title") or ""
    if not ((COLFIG.search(t) or re.search(r"\bColumbia\b|Brother Jonathan|Britannia|Allegory of America|America\b.*(Continent|Allegor)|Liberty", t)) and not PLACE.search(t)):
        continue
    if (x.get("date_start") or 0) < 1490:
        continue
    add(src="AIC", sid=str(k), title=t, creator=(x.get("artist_display") or "").replace("\n", "; "), date=x.get("date_display") or "", year=x.get("date_start"),
        medium=x.get("medium_display") or "", desc="", subjects=x.get("classification_title") or "", repo="Art Institute of Chicago", call=x.get("main_reference_number") or "",
        url="https://www.artic.edu/artworks/%s" % k,
        img=["https://www.artic.edu/iiif/2/%s/full/1200,/0/default.jpg" % x["image_id"], "https://www.artic.edu/iiif/2/%s/full/843,/0/default.jpg" % x["image_id"]],
        lic="CC0 (AIC Public Domain)")

# ---------- SI
for k, x in load("si_raw.json").items():
    c = x.get("content", {})
    dn = c.get("descriptiveNonRepeating", {})
    media = (dn.get("online_media") or {}).get("media") or []
    if not media:
        continue
    m = media[0]
    if (m.get("usage") or {}).get("access") != "CC0":
        continue
    t = x.get("title") or ""
    ft = c.get("freetext", {})
    def F(n):
        return " ; ".join(i.get("content", "") for i in ft.get(n, []) if isinstance(i.get("content"), str))
    T = t + " " + F("notes") + " " + F("topic")
    if not (COLFIG.search(T) or re.search(r"Brother Jonathan", T)) or PLACE.search(t):
        continue
    if re.search(r"Company Cape|Fire", t):
        continue
    ids = m.get("idsId")
    img = ["https://ids.si.edu/ids/deliveryService?id=%s&max=1600" % ids] if ids else [m.get("content") or ""]
    add(src="SI", sid=k, title=t, creator=F("name"), date=F("date"), year=year_of(F("date")), medium=F("physicalDescription")[:200], desc=F("notes")[:600],
        subjects=F("topic") + " | " + F("objectType"), repo="Smithsonian Institution · " + (dn.get("data_source") or ""), call=F("identifier")[:80],
        url=dn.get("record_link") or dn.get("guid") or "", img=img, lic="CC0 (Smithsonian Open Access)")

json.dump(recs, open("records.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(collections.Counter(r["src"] for r in recs), len(recs))
