"""Build data + derivative images for the Columbia image-history site."""
import json, os, re, sys, math, collections
import numpy as np
from PIL import Image, ImageOps, ImageFilter, ImageEnhance

Image.MAX_IMAGE_PIXELS = None
SITE = sys.argv[1]
cat = json.load(open("catalog.json", encoding="utf-8"))
exec(open("fit.py", encoding="utf-8").read().split("out = {}")[0])  # albers, G, CP

def load(f):
    return json.load(open(f, encoding="utf-8")) if os.path.exists(f) else {}

# ------------------------------------------------------------------ gazetteer
P = [  # key, en, zh, lon, lat, region, regex
 ("newyork", "New York", "纽约", -74.01, 40.71, "us", r"New[- ]?York|\bN\.? ?Y\.?(?![a-z])|Nueva York|Brooklyn|Manhattan"),
 ("philadelphia", "Philadelphia", "费城", -75.16, 39.95, "us", r"Philad\w*|Phila\b\.?"),
 ("boston", "Boston", "波士顿", -71.06, 42.36, "us", r"Boston"),
 ("baltimore", "Baltimore", "巴尔的摩", -76.61, 39.29, "us", r"Baltimore|Balto\b"),
 ("washington", "Washington, D.C.", "华盛顿", -77.04, 38.90, "us", r"Washington,? D\.? ?C\.?|Washington City|\[Washington\]|^Washington\b|District of Columbia|U\.?S\.? Capitol|United States Capitol|Library of Congress Thomas Jefferson"),
 ("cincinnati", "Cincinnati", "辛辛那提", -84.51, 39.10, "us", r"Cincinnati"),
 ("chicago", "Chicago", "芝加哥", -87.63, 41.88, "us", r"Chicago|Columbian Exposition|Jackson Park"),
 ("stlouis", "St. Louis", "圣路易斯", -90.20, 38.63, "us", r"S(ain)?t\.? Louis"),
 ("sanfrancisco", "San Francisco", "旧金山", -122.42, 37.78, "us", r"San Francisco|Midwinter Exposition|Panama[- ]Pacific"),
 ("neworleans", "New Orleans", "新奥尔良", -90.07, 29.95, "us", r"New Orleans"),
 ("charleston", "Charleston", "查尔斯顿", -79.93, 32.78, "us", r"Charleston,? (S\.? ?C|South)"),
 ("richmond", "Richmond", "里士满", -77.44, 37.54, "us", r"Richmond,? (Va|Virginia)|^Richmond\b"),
 ("hartford", "Hartford", "哈特福德", -72.68, 41.76, "us", r"Hartford"),
 ("newhaven", "New Haven", "纽黑文", -72.93, 41.31, "us", r"New[- ]Haven"),
 ("providence", "Providence", "普罗维登斯", -71.41, 41.82, "us", r"Providence,? (R|Rhode)|^Providence\b"),
 ("albany", "Albany", "奥尔巴尼", -73.75, 42.65, "us", r"Albany"),
 ("buffalo", "Buffalo", "布法罗", -78.88, 42.89, "us", r"Buffalo,? N|^Buffalo\b|Pan-American Exposition"),
 ("pittsburgh", "Pittsburgh", "匹兹堡", -80.00, 40.44, "us", r"Pittsburgh?"),
 ("cleveland", "Cleveland", "克利夫兰", -81.69, 41.50, "us", r"Cleveland,? O|^Cleveland\b"),
 ("detroit", "Detroit", "底特律", -83.05, 42.33, "us", r"Detroit"),
 ("milwaukee", "Milwaukee", "密尔沃基", -87.91, 43.04, "us", r"Milwaukee"),
 ("louisville", "Louisville", "路易斯维尔", -85.76, 38.25, "us", r"Louisville"),
 ("newburyport", "Newburyport", "纽伯里波特", -70.88, 42.81, "us", r"Newburyport"),
 ("salem", "Salem, Mass.", "塞勒姆", -70.90, 42.52, "us", r"Salem,? Mass"),
 ("worcester", "Worcester", "伍斯特", -71.80, 42.26, "us", r"Worcester,? Mass|^Worcester\b"),
 ("portlandme", "Portland, Me.", "波特兰（缅因）", -70.26, 43.66, "us", r"Portland,? (Me|Maine)"),
 ("rochester", "Rochester", "罗切斯特", -77.61, 43.16, "us", r"Rochester,? N"),
 ("indianapolis", "Indianapolis", "印第安纳波利斯", -86.16, 39.77, "us", r"Indianapolis"),
 ("minneapolis", "Minneapolis–St. Paul", "明尼阿波利斯—圣保罗", -93.27, 44.98, "us", r"Minneapolis|S(ain)?t\.? Paul,? Minn"),
 ("denver", "Denver", "丹佛", -104.99, 39.74, "us", r"Denver"),
 ("losangeles", "Los Angeles", "洛杉矶", -118.24, 34.05, "us", r"Los Angeles"),
 ("seattle", "Seattle", "西雅图", -122.33, 47.60, "us", r"Seattle"),
 ("atlanta", "Atlanta", "亚特兰大", -84.39, 33.75, "us", r"Atlanta"),
 ("savannah", "Savannah", "萨凡纳", -81.10, 32.08, "us", r"Savannah"),
 ("nashville", "Nashville", "纳什维尔", -86.78, 36.16, "us", r"Nashville"),
 ("kansascity", "Kansas City", "堪萨斯城", -94.58, 39.10, "us", r"Kansas City"),
 ("omaha", "Omaha", "奥马哈", -95.94, 41.26, "us", r"Omaha"),
 ("columbusoh", "Columbus, Ohio", "哥伦布（俄亥俄）", -83.00, 39.96, "us", r"Columbus,? O"),
 ("newark", "Newark", "纽瓦克", -74.17, 40.74, "us", r"Newark,? N"),
 ("trenton", "Trenton", "特伦顿", -74.76, 40.22, "us", r"Trenton"),
 ("harrisburg", "Harrisburg", "哈里斯堡", -76.88, 40.27, "us", r"Harrisburg"),
 ("madison", "Madison, Wis.", "麦迪逊", -89.40, 43.07, "us", r"Madison,? Wis|Wisconsin State Capitol|Wisconsin Senate"),
 ("austin", "Austin", "奥斯汀", -97.74, 30.27, "us", r"Austin,? Tex|Texas State Capitol|Littlefield"),
 ("sacramento", "Sacramento", "萨克拉门托", -121.49, 38.58, "us", r"Sacramento"),
 ("gettysburg", "Gettysburg", "葛底斯堡", -77.23, 39.83, "us", r"Gettysburg"),
 ("syracuse", "Syracuse", "锡拉丘兹", -76.15, 43.05, "us", r"Syracuse"),
 ("springfieldma", "Springfield, Mass.", "斯普林菲尔德", -72.59, 42.10, "us", r"Springfield,? Mass"),
 ("london", "London", "伦敦", -0.13, 51.51, "europe", r"London|Londres|Londra"),
 ("paris", "Paris", "巴黎", 2.35, 48.86, "europe", r"Paris"),
 ("amsterdam", "Amsterdam", "阿姆斯特丹", 4.90, 52.37, "europe", r"Amsterdam|Amstelodami|Amstelaedami"),
 ("antwerp", "Antwerp", "安特卫普", 4.40, 51.22, "europe", r"Antwerp\w*|Anvers|Antverpi\w+"),
 ("augsburg", "Augsburg", "奥格斯堡", 10.90, 48.37, "europe", r"Augsburg|Augspurg|Augustae Vindelicorum"),
 ("nuremberg", "Nuremberg", "纽伦堡", 11.08, 49.45, "europe", r"N[uü]rnberg|Nuremberg|Norimberg\w+"),
 ("leipzig", "Leipzig", "莱比锡", 12.37, 51.34, "europe", r"Leipzig|Lipsiae"),
 ("frankfurt", "Frankfurt", "法兰克福", 8.68, 50.11, "europe", r"Fran[ck]furt\w*|Francofurt\w+"),
 ("berlin", "Berlin", "柏林", 13.40, 52.52, "europe", r"Berlin"),
 ("vienna", "Vienna", "维也纳", 16.37, 48.21, "europe", r"Vienna|Wien\b"),
 ("rome", "Rome", "罗马", 12.50, 41.90, "europe", r"\bRom[ae]\b|Rome"),
 ("venice", "Venice", "威尼斯", 12.32, 45.44, "europe", r"Venice|Venezia|Veneti\w+"),
 ("madrid", "Madrid", "马德里", -3.70, 40.42, "europe", r"Madrid|Matriti"),
 ("lisbon", "Lisbon", "里斯本", -9.14, 38.72, "europe", r"Lisbo[na]|Ulyssipone"),
 ("edinburgh", "Edinburgh", "爱丁堡", -3.19, 55.95, "europe", r"Edinburgh"),
 ("dublin", "Dublin", "都柏林", -6.26, 53.35, "europe", r"Dublin"),
 ("leiden", "Leiden", "莱顿", 4.49, 52.16, "europe", r"Leiden|Leyden|Lugduni Batavorum"),
 ("hague", "The Hague", "海牙", 4.30, 52.07, "europe", r"The Hague|La Haye|'s[- ]Gravenhage|Hagae"),
 ("cologne", "Cologne", "科隆", 6.96, 50.94, "europe", r"Cologne|K[oö]ln|Coloniae"),
 ("lyon", "Lyon", "里昂", 4.84, 45.76, "europe", r"Lyon|Lugduni(?! Bat)"),
 ("milan", "Milan", "米兰", 9.19, 45.46, "europe", r"Milan\w*|Mediolani"),
 ("seville", "Seville", "塞维利亚", -5.98, 37.39, "europe", r"Sevill[ae]|Hispali"),
 ("mexico", "Mexico City", "墨西哥城", -99.13, 19.43, "other", r"M[eé]xico"),
 ("lima", "Lima", "利马", -77.04, -12.05, "other", r"\bLima\b"),
 ("tokyo", "Edo / Tokyo", "江户／东京", 139.69, 35.69, "other", r"Tokyo|\bEdo\b|Yokohama|Kawaraban|Hiroshige"),
]
PL = {p[0]: p for p in P}
RX = [(p[0], re.compile(p[6])) for p in P]

def find_place(text):
    if not text:
        return None
    best = None
    for k, rx in RX:
        m = rx.search(text)
        if m and (best is None or m.start() < best[1]):
            best = (k, m.start())
    return best[0] if best else None

SERIAL = [
 (r"\bPuck\b|PuckMagazine|Keppler|Pughe|Dalrymple|Ehrhart|Nankivell|Glackens|Opper\b|Taylor, C(harles)? J", "newyork", "Puck"),
 (r"JudgeMagazine|\bJudge\b[^.]{0,40}(magazine|v\.|cover|Publishing|18\d\d|19\d\d)|Gillam|Zimmerman|Sackett & Wilhelms", "newyork", "Judge"),
 (r"Harper'?s Weekly|\bNast\b|Harper & Brothers|Harper'?s Bazar", "newyork", "Harper's Weekly"),
 (r"Leslie'?s", "newyork", "Frank Leslie's"),
 (r"LIFEMagazine|Life Magazine|cover of Life\b", "newyork", "Life"),
 (r"Currier|N\. Currier", "newyork", "Currier & Ives"),
 (r"Vanity Fair|Yankee Notions|New York (Herald|Tribune|World|Times)|Daily Graphic", "newyork", "New York press"),
 (r"\bPunch\b|Tenniel|London Charivari", "london", "Punch"),
 (r"\bThe Wasp\b|From the Wasp", "sanfrancisco", "The Wasp"),
 (r"Ram'?s Horn", "chicago", "The Ram's Horn"),
 (r"Berryman|Evening Star|Washington Post", "washington", "Washington press"),
 (r"\bPrang\b", "boston", "L. Prang & Co."),
 (r"Strobridge", "cincinnati", "Strobridge Lith."),
]

jcb = load("jcb_raw.json")
locp = load("loc_place.json")
cm = load("commons_raw.json")

def strip(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s or "")).strip()

def place_of(r):
    """returns (place_key, basis, evidence)"""
    src, sid = r["src"], r["sid"]
    if src == "JCB":
        fv = {}
        for f in jcb.get(sid, {}).get("fieldValues", []):
            for a, b in f.items():
                fv[a] = " ; ".join(map(str, b))
        for fld in ("Place", "Place of publication", "Source place of publication", "Publication place"):
            if fv.get(fld):
                k = find_place(fv[fld])
                if k:
                    return k, "pub", fv[fld][:80]
        for fld in ("Source title", "Creators", "Source creator", "Notes"):
            pass
        st = " ".join(fv.get(n, "") for n in ("Source imprint", "Imprint", "Source publication", "Source title"))
        k = find_place(st)
        if k:
            return k, "pub", st[:80]
    lcid = sid if src == "LOC" else None
    if src == "Commons":
        m = re.search(r"LCCN(\d{8,10})", sid)
        lcid = m.group(1) if m else None
    if lcid and locp.get(lcid, {}).get("cp"):
        cp = locp[lcid]["cp"]
        cp = cp if isinstance(cp, str) else " ".join(cp)
        k = find_place(cp)
        if k:
            return k, "pub", cp[:90]
    full = " | ".join([r.get("title") or "", r.get("creator") or "", r.get("medium") or "", r.get("desc") or "", r.get("subjects") or "", r.get("call") or ""])
    if src == "Commons":
        ii = cm.get("File:" + sid, {}).get("ii") or {}
        em = ii.get("extmetadata") or {}
        full += " | " + strip((em.get("ImageDescription") or {}).get("value", ""))[:3000]
        m = re.search(r"(Created ?/ ?Published|Publisher|Published|Place of publication)\s*:?\s*([^|]{4,120})", full)
        if m:
            k = find_place(m.group(2))
            if k:
                return k, "pub", m.group(2)[:90]
    if lcid and locp.get(lcid):
        s = locp[lcid].get("summary")
        full += " | " + (s if isinstance(s, str) else " ".join(s or []))
        nt = locp[lcid].get("notes")
        full += " | " + (nt if isinstance(nt, str) else " ".join(map(str, nt or [])))
    for rx, k, name in SERIAL:
        if re.search(rx, full):
            return k, "serial", name
    if r["type"] in ("09", "13"):
        t = (r.get("title") or "") + " | " + (r.get("subjects") or "") + " | " + (r.get("desc") or "")[:400]
        k = find_place(t)
        if k:
            return k, "site", ""
    if src == "DC":
        k = find_place(r.get("title") or "")
        if k:
            return k, "pub", (r.get("title") or "")[:80]
    m = re.search(r"\b(published|printed|lith\w*|engraved|sold) (by|at|in)[^|]{0,80}", full, re.I)
    if m:
        k = find_place(m.group(0))
        if k:
            return k, "pub", m.group(0)[:90]
    return None, None, None

STAGES = [(None, 1764, 1), (1765, 1783, 2), (1784, 1815, 3), (1816, 1860, 4), (1861, 1897, 5), (1898, None, 6)]
def stage_of(y):
    if not y:
        return 0
    for a, b, n in STAGES:
        if (a is None or y >= a) and (b is None or y <= b):
            return n
    return 0

TYPE_EN = {"01": "Allegorical prints (engraving, etching, woodcut)", "02": "Lithographs & chromolithographs", "03": "Political cartoons & satires",
           "04": "Posters", "05": "Sheet-music covers", "06": "Book illustrations, frontispieces & magazine covers",
           "07": "Map cartouches & the Four Continents", "08": "Paintings & drawings", "09": "Sculpture, monuments & architectural decoration",
           "10": "Coins, medals, banknotes & certificates", "11": "Printed ephemera", "12": "Decorative arts & objects",
           "13": "Photographs (costume, pageant, tableau)", "14": "Other / unsorted"}
SRC_NAME = {"LOC": ["美国国会图书馆", "Library of Congress"], "Commons": ["维基共享资源", "Wikimedia Commons"], "JCB": ["约翰·卡特·布朗图书馆", "John Carter Brown Library"],
            "DC": ["Digital Commonwealth（波士顿公共图书馆等）", "Digital Commonwealth"], "MET": ["大都会艺术博物馆", "The Metropolitan Museum of Art"],
            "AIC": ["芝加哥艺术博物馆", "Art Institute of Chicago"], "SI": ["史密森尼学会", "Smithsonian Institution"]}

os.makedirs(os.path.join(SITE, "img", "t"), exist_ok=True)
os.makedirs(os.path.join(SITE, "img", "l"), exist_ok=True)
ARCH = os.path.join(os.path.dirname(SITE), "columbia-iconography")
items = []
pc = collections.Counter()
for r in cat:
    cid = r["cid"]
    k, basis, ev = place_of(r)
    pc[(k is not None)] += 1
    srcp = os.path.join(ARCH, r["file"])
    tp = os.path.join(SITE, "img", "t", cid + ".jpg")
    lp = os.path.join(SITE, "img", "l", cid + ".jpg")
    w = h = 0
    try:
        if not (os.path.exists(tp) and os.path.exists(lp) and os.path.getmtime(lp) >= os.path.getmtime(srcp)):
            im = Image.open(srcp).convert("RGB")
            big = im.copy(); big.thumbnail((1600, 1600), Image.LANCZOS); big.save(lp, "JPEG", quality=84, optimize=True)
            im.thumbnail((440, 440), Image.LANCZOS); im.save(tp, "JPEG", quality=78, optimize=True)
        w, h = Image.open(tp).size
    except Exception as e:
        print("img fail", cid, e)
        continue
    items.append({"id": cid, "t": r["title"], "c": (r.get("creator") or "")[:200], "y": r.get("year"), "d": (r.get("date") or "")[:60],
                  "ty": r["type"], "st": stage_of(r.get("year")), "m": (r.get("medium") or "")[:200], "ds": (r.get("desc") or "")[:700],
                  "sj": (r.get("subjects") or "")[:300], "rp": (r.get("repo") or "")[:160], "cn": (r.get("call") or "")[:80], "s": r["src"],
                  "u": r.get("url") or "", "lc": (r.get("lic") or "")[:80], "p": k, "pb": basis, "pe": ev or "", "w": w, "h": h, "f": r["file"]})
print("placed", pc)

# ------------------------------------------------------------------ maps (MLS affine)
MAPS_META = [
 ("m1", 1755, "A Map of the British and French Dominions in North America", "John Mitchell（Covens & Mortier 版）", "Amsterdam, [1755–1761]", "g3300.ar004401", None, 1764,
  dict(lon=(-99, -52), lat=(27.5, 53))),
 ("m2", 1783, "The United States of America laid down from the best authorities, agreeable to the Peace of 1783", "John Wallis", "London, 1783", "g3700.ct000080", 1765, 1783,
  dict(lon=(-97, -52), lat=(28, 53))),
 ("m3", 1804, "Map of the United States, exhibiting the post-roads, the situations, connexions & distances of the post-offices…", "Abraham Bradley Jr.", "Philadelphia, [1804]", "g3700.ct002344", 1784, 1815,
  dict(lon=(-93.5, -66), lat=(29.5, 46.5))),
 ("m4", 1850, "Map of the United States of America, the British Provinces, Mexico, the West Indies and Central America…", "J. H. Colton", "New York, 1850", "g3700.ct000761", 1816, 1860,
  dict(lon=(-126, -64), lat=(24, 50))),
 ("m5", 1876, "Rand McNally & Co.'s New Railroad and County Map of the United States and Canada", "Rand McNally & Co.", "Chicago, 1876", "g3701p.rr000580", 1861, 1897,
  dict(lon=(-125.5, -66), lat=(27.5, 50))),
 ("m6", 1901, "The United States of America, including all its newly acquired territory", "National Publishing Company", "Boston, [1901]", "g3700.ct001444", 1898, None,
  dict(lon=(-125.5, -66), lat=(24.3, 50))),
]

def mls(mk, lon, lat):
    d = CP[mk]
    q = np.array(albers(lon, lat))
    src = np.array([albers(*G[n]) for n in d["pts"]]); dst = np.array([d["pts"][n] for n in d["pts"]], dtype=float)
    w = 1.0 / (((src - q) ** 2).sum(1) + 1e-7) ** 1.0
    # extra control from exact gazetteer matches is implicit (weights explode near control points)
    A = np.hstack([src, np.ones((len(src), 1))])
    W = np.diag(w)
    sol, *_ = np.linalg.lstsq(W @ A, W @ dst, rcond=None)
    return (np.array([q[0], q[1], 1.0]) @ sol).tolist()

maps = []
os.makedirs(os.path.join(SITE, "maps"), exist_ok=True)
for mk, yr, title, maker, imprint, res, y0, y1, cov in MAPS_META:
    raw = [f for f in os.listdir("maps_raw") if f.startswith(mk + "_")][0]
    outp = os.path.join(SITE, "maps", mk + ".jpg")
    im = Image.open(os.path.join("maps_raw", raw)).convert("RGB")
    if not os.path.exists(outp):
        # gentle, faithful clean-up: clip 0.3% tails, slight contrast and unsharp; no recolouring or redrawing
        e = ImageOps.autocontrast(im, cutoff=(0.3, 0.3), preserve_tone=True)
        e = ImageEnhance.Contrast(e).enhance(1.06)
        e = e.filter(ImageFilter.UnsharpMask(radius=1.6, percent=60, threshold=2))
        e.save(outp, "JPEG", quality=88, optimize=True, progressive=True)
    W, H = im.size
    pts = {}
    for p in P:
        if p[5] != "us":
            continue
        lon, lat = p[3], p[4]
        if not (cov["lon"][0] <= lon <= cov["lon"][1] and cov["lat"][0] <= lat <= cov["lat"][1]):
            continue
        x, y = mls(mk, lon, lat)
        if 40 < x < W - 40 and 40 < y < H - 40:
            pts[p[0]] = [round(x), round(y)]
    maps.append({"k": mk, "year": yr, "title": title, "maker": maker, "imprint": imprint, "url": "https://www.loc.gov/resource/%s/" % res,
                 "from": y0, "to": y1, "w": W, "h": H, "pts": pts})
    print(mk, len(pts), "places on map")

places = {p[0]: {"en": p[1], "zh": p[2], "r": p[5]} for p in P}
types = [{"k": k, "zh": next(r["type_label"] for r in cat if r["type"] == k), "en": TYPE_EN[k]} for k in sorted(set(r["type"] for r in cat))]
data = {"items": items, "places": places, "maps": maps, "types": types, "sources": SRC_NAME, "built": __import__("datetime").date.today().isoformat()}
os.makedirs(os.path.join(SITE, "data"), exist_ok=True)
with open(os.path.join(SITE, "data", "data.js"), "w", encoding="utf-8") as f:
    f.write("window.COLUMBIA_DATA = ")
    json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    f.write(";\n")
print("items", len(items), "bytes", os.path.getsize(os.path.join(SITE, "data", "data.js")))
c2 = collections.Counter((i["p"], i["pb"]) for i in items)
print(sorted(c2.items(), key=lambda x: -x[1])[:40])
print("by stage", collections.Counter(i["st"] for i in items), "placed by stage", collections.Counter(i["st"] for i in items if i["p"]))
