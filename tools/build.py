"""Classify records, copy cached images into typed folders, write catalog.json / xlsx."""
import json, os, re, sys, hashlib, shutil, collections, unicodedata
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
OUT = sys.argv[1] if len(sys.argv) > 1 else None
recs = json.load(open("records.json", encoding="utf-8"))

TYPES = [
    ("01", "寓意版画_雕版蚀刻木刻", "寓意版画（雕版、蚀刻、木刻等）"),
    ("02", "石版画与彩色石印", "石版画与彩色石印"),
    ("03", "政治漫画与讽刺画", "政治漫画与讽刺画"),
    ("04", "海报与宣传画", "海报与宣传画"),
    ("05", "乐谱封面", "乐谱封面与歌曲印刷品"),
    ("06", "书刊插图与卷首画", "书刊插图、卷首画、扉页与杂志封面"),
    ("07", "地图装饰与四大洲寓意", "地图装饰框与四大洲寓意"),
    ("08", "绘画与素描", "绘画、素描与壁画稿"),
    ("09", "雕塑与建筑装饰", "雕塑、纪念碑与建筑装饰（含天顶画）"),
    ("10", "钱币纪念章与票证", "钱币、纪念章、纸币与票证"),
    ("11", "日用印刷品", "日用印刷品（信封、商业卡片、明信片、广告、传单）"),
    ("12", "装饰艺术与器物", "装饰艺术与器物（陶瓷、织物等）"),
    ("13", "照片与扮装", "照片（扮装、游行、活人画）"),
    ("14", "其他与未细分", "其他与未细分"),
]
PERIODS = [(0, 1764, "A 1764年以前：四大洲寓意与“印第安女王”"), (1765, 1783, "B 1765–1783：革命时期"), (1784, 1815, "C 1784–1815：建国初期"),
           (1816, 1860, "D 1816–1860：战前时期"), (1861, 1877, "E 1861–1877：内战与重建"), (1878, 1900, "F 1878–1900：镀金时代"),
           (1901, 1920, "G 1901–1920：进步时代与一战"), (1921, 9999, "H 1921年以后")]

def period(y):
    if not y:
        return "年代不详"
    for a, b, n in PERIODS:
        if a <= y <= b:
            return n
    return "年代不详"

def classify(r):
    med = (r.get("medium") or "")
    if r["src"] == "Commons":
        d = r.get("desc") or ""
        mm = re.search(r"(Abstract/medium|Physical description|Medium|Objecttype):\s*([^.]{3,90})", d)
        if mm:
            med = mm.group(2)
            r["medium"] = med.strip()
        full = (r.get("title") or "") + " | " + d + " | " + (r.get("subjects") or "")
        f = lambda p: re.search(p, full, re.I)
        if f(r"banknotes and coins|on medals"):
            return "10"
        if f(r"on posters|poster"):
            return "04"
        if f(r"decorative and applied arts|porcelain|Meissen|Kaendler|Kändler|Porzellan|creamware|pitcher|Plate with|transferware|weather ?vane|figurine|tapestr|textile"):
            return "12"
        if f(r"stereograph|negative|photoprint|costume of|pageant|tableau|Hedwig|albumen"):
            return "13"
        if f(r"Sculptures of|Skulptur|Est.tua|jard[ií]|Garten|Brunnen|fontaine|fountain|Memorial Hall|roof|façade|facade|relief|Statue|Estatua|sculpture|Deckengem|Pfarrkirche|Kanzel|Schloss|Pałac|church|ceiling|Great Hall|Capitol|Chamber|Haus Zur|Borglum|Konti|Millet|Martiny|Leherb|buste|cúpula|Maximilianmuseum|Barockgarten|Albert Memorial|Powers|John Bell") and not f(r"chromolithograph|1 print|engraving|etching"):
            return "09"
        if f(r"Puck|Judge|Pughe|Keppler|Kep|Ehrhart|Nankivell|Dalrymple|Glackens|Berryman|DPLA|cartoon|Nast|Harper|Wasp|satire|BMSat|caricature|Sykes|Kawaraban"):
            return "03"
        if f(r"patriotic cover|envelope|post ?card|Cartolina|Brewing|trade card|advertis|enamel of America"):
            return "11"
        if f(r"sheet music|Schottisch|musical composition|Anthems|hymn|song|Hail, Columbia|Gem of the Ocean"):
            return "05"
        if f(r"Magazine|Leslie|cover|Identifier ?:|Courtship|Cyclopedia|Titelpagina|title page|frontispiece|Review of reviews|Bulletin|booklet|souvenir|Willard|Crofutt"):
            return "06"
        if f(r"Tiepolo|van Kessel|van de Velde|oil on|Kemmelmeyer|Yvon|painting|Anônimo|Art Museum|Hiroshige") and not f(r"RP-P|prent"):
            return "08"
        if f(r"Vier Werelddelen|cuatro partes|four continents|quatre parties|Kaartspel|Allegorie op|Personifications of the Americas|Allegories of America"):
            return "07"
    T = " | ".join([r.get("title") or "", med, r.get("subjects") or "", r.get("repo") or "", (r.get("desc") or "")[:300]])
    s = lambda p: re.search(p, T, re.I)
    m = lambda p: re.search(p, med, re.I)
    if s(r"banknotes and coins|on medals|\bcoins?\b|\bmedals?\b|medallion|bank ?note|\bcurrency\b|postage stamp|stock certificate|\bcent\b.*pattern|half dollar|numismat"):
        return "10"
    if s(r"Sculptures? of|\bsculptures?\b|\bstatues?\b|monument|memorial|fountain|pediment|by Hiram Powers|by John Bell|\bmarble\b|\bbronze\b|bas-relief|Hiolle|Guérin|Kundmann|Galleria") and not m(r"print|lithograph|engraving|drawing"):
        return "09"
    if s(r"\bposters?\b|Liberty Loan|war bonds|Enlist|Sow the Seeds|Weapons for Liberty|Over There \(poster"):
        return "04"
    if s(r"Music title pages|sheet music|Sheet music covers|notated music|Hail, Columbia|Columbia, the Gem|\bsong\b|\bmarch\b.*\bpiano\b|songster"):
        return "05"
    if r.get("coll") == "JCB Map Collection" or s(r"\bcartouche|\batlas\b") or re.search(r"\bmap\b|\bcarte\b|\bkaart\b|\bmapa\b", r.get("title") or "", re.I):
        return "07"
    if r.get("coll") == "JCB Political Cartoons" or s(r"Cartoons \(Commentary\)|Political cartoons|\bcartoons?\b|Satires|caricatur|Periodical illustrations|\bPuck\b|Judge ?Magazine|\bJudge\b.*18|Harper'?s Weekly|\bPunch\b|\bNast\b|Keppler|Dalrymple|Gillam|American revolution cow|able doctor|political concert|Shelb|savages let loose|American river Ganges|Easter Bonnet|Brother Jonathan"):
        return "03"
    if s(r"envelope|trade cards?|post ?cards?|\blabels?\b|advertis|broadside|\bticket|calendar|Covers \(Philately\)|ephemera|valentine|banners?, campaign|campaign banner|handbill|cigar|tobacco"):
        return "11"
    if s(r"textile|ceramic|pitcher|creamware|earthenware|porcelain|transfer.?print|weather ?vane|\bquilt|handkerchief|tapestr|\bjug\b|\bglass\b.*(flask|bottle)|decorative and applied arts|figurine|Meissen|needlework|sampler"):
        return "12"
    if r.get("coll") == "JCB Archive of Early American Images" or s(r"title pages?|frontispiece|book illustration|\balmanac|Columbian Magazine|Illustrations\b"):
        if s(r"four continents|quatre parties|vier (Erd|werelddelen)|continents"):
            return "07"
        return "06"
    if s(r"four continents|Allegories of America$|Personifications of the Americas|quatre parties du monde|Allegory of America|America, from"):
        if m(r"oil|canvas|fresco|watercolor|drawing|chalk|\bpen\b"):
            return "08"
        return "07"
    if m(r"negative|photograph|stereograph|transparency|carte de visite|glass") or s(r"Costumes|Pageants|Tableaux"):
        return "13"
    if m(r"drawing|painting|watercolor|oil on|sketch|\bink\b|crayon|pencil|graphite|gouache|fresco|chalk") or s(r"\bmural|\bfresco|oil on canvas|\bpainting"):
        return "08"
    if m(r"lithograph|chromolithograph") or s(r"Lithographs|Currier"):
        return "02"
    if m(r"engraving|etching|woodcut|mezzotint|aquatint|\bprint\b|stipple|intaglio") or s(r"Engravings|Etchings|Woodcuts|Mezzotints|Allegorical prints|engraved|\bengraving|\betching"):
        return "01"
    return "14"

def slug(t, n=60):
    t = unicodedata.normalize("NFKD", t or "untitled")
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"[^A-Za-z0-9]+", "-", t).strip("-")
    return (t[:n].rstrip("-")) or "untitled"

def key(r):
    return hashlib.sha1((r["src"] + "|" + r["sid"]).encode("utf-8")).hexdigest()[:16]

# dedupe by src+sid
seen = set(); R = []
LOCIDS = {r["sid"] for r in recs if r["src"] == "LOC"}
for r in recs:
    if r["src"] == "Commons":
        _m = re.search(r"LCCN(\d{8,10})", r["sid"])
        if _m and _m.group(1) in LOCIDS:
            continue  # same sheet already held from the Library of Congress itself
    k = key(r)
    if k in seen:
        continue
    seen.add(k)
    if re.search(r"Disney|Nicaragua|Columbia City|771insig|Krewe of|group photos", (r.get("title") or "") + (r.get("subjects") or "")):
        continue
    r["key"] = k
    r["type"] = classify(r)
    r["period"] = period(r.get("year"))
    R.append(r)

cnt = collections.Counter((r["type"], r["src"]) for r in R)
for code, folder, label in TYPES:
    print(code, label, {s: cnt[(code, s)] for s in ["LOC", "Commons", "JCB", "DC", "MET", "AIC", "SI"] if cnt[(code, s)]})
have = sum(os.path.exists(os.path.join("cache", r["key"] + ".jpg")) for r in R)
print("total", len(R), "cached", have)
if not OUT:
    sys.exit()

IMG = os.path.join(OUT, "图像")
TH = "thumbs"
os.makedirs(TH, exist_ok=True)
if os.path.isdir(IMG):
    shutil.rmtree(IMG)
catalog = []
for code, folder, label in TYPES:
    items = [r for r in R if r["type"] == code and os.path.exists(os.path.join("cache", r["key"] + ".jpg"))]
    items.sort(key=lambda r: (r.get("year") or 9999, r["title"]))
    d = os.path.join(IMG, code + "_" + folder)
    os.makedirs(d, exist_ok=True)
    for i, r in enumerate(items, 1):
        cid = "%s-%04d" % (code, i)
        fn = "%s_%s_%s_%s.jpg" % (cid, r.get("year") or "nd", r["src"], slug(r["title"]))
        src = os.path.join("cache", r["key"] + ".jpg")
        shutil.copyfile(src, os.path.join(d, fn))
        tp = os.path.join(TH, r["key"] + ".jpg")
        if not os.path.exists(tp):
            try:
                im = Image.open(src)
                im = im.convert("RGB")
                im.thumbnail((260, 260))
                im.save(tp, "JPEG", quality=72)
            except Exception as e:
                print("thumb fail", fn, e)
        r2 = dict(r)
        r2.update(cid=cid, file="图像/%s_%s/%s" % (code, folder, fn), type_label=label, thumb=tp)
        catalog.append(r2)
json.dump(catalog, open("catalog.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
wb = Workbook(); ws = wb.active; ws.title = "图像目录"
cols = ["编号", "类型", "时期", "年份", "年代（原著录）", "题名", "作者/出版者", "媒介", "说明（原著录）", "主题词", "馆藏/来源", "馆藏号", "来源代码", "原始页面", "权利说明", "本地文件"]
ws.append(cols)
for c in ws[1]:
    c.font = Font(bold=True)
for r in catalog:
    ws.append([r["cid"], r["type_label"], r["period"], r.get("year"), r.get("date"), r["title"], r.get("creator"), r.get("medium"), r.get("desc"), r.get("subjects"), r.get("repo"), r.get("call"), r["src"], r.get("url"), r.get("lic"), r["file"]])
    row = ws.max_row
    if r.get("url"):
        ws.cell(row=row, column=14).hyperlink = r["url"]
for col, w in zip("ABCDEFGHIJKLMNOP", [10, 22, 26, 7, 16, 60, 30, 28, 60, 40, 36, 18, 9, 40, 24, 60]):
    ws.column_dimensions[col].width = w
ws.freeze_panes = "B2"
ws.auto_filter.ref = ws.dimensions
wb.save(os.path.join(OUT, "哥伦比亚女神图像目录.xlsx"))
print("copied", len(catalog))
