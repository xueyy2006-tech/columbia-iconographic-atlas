import json, os, sys, collections, datetime
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import docx.opc.constants

OUT = sys.argv[1]
cat = json.load(open("catalog.json", encoding="utf-8"))
doc = Document()
sec = doc.sections[0]
sec.orientation = WD_ORIENT.LANDSCAPE
sec.page_width, sec.page_height = Cm(29.7), Cm(21.0)
for a in ("left_margin", "right_margin"):
    setattr(sec, a, Cm(1.8))
sec.top_margin = sec.bottom_margin = Cm(1.8)

def setfont(run, size=10.5, bold=False, east="宋体", west="Times New Roman", color=None):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.name = west
    rpr = run._element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts"); rpr.append(rf)
    rf.set(qn("w:eastAsia"), east); rf.set(qn("w:ascii"), west); rf.set(qn("w:hAnsi"), west)
    if color:
        run.font.color.rgb = RGBColor(*color)

st = doc.styles["Normal"]
st.font.name = "Times New Roman"; st.font.size = Pt(10.5)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
for name, size in (("Heading 1", 16), ("Heading 2", 14), ("Heading 3", 12)):
    h = doc.styles[name]
    h.font.name = "Times New Roman"; h.font.size = Pt(size); h.font.bold = True; h.font.color.rgb = RGBColor(0, 0, 0)
    h.element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")

def para(text, size=10.5, bold=False, indent=True, align=None, east="宋体", after=4):
    p = doc.add_paragraph()
    if indent:
        p.paragraph_format.first_line_indent = Pt(size * 2)
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.line_spacing = 1.35
    if align:
        p.alignment = align
    setfont(p.add_run(text), size, bold, east)
    return p

def link(p, url, text, size=8):
    rid = p.part.relate_to(url, docx.opc.constants.RELATIONSHIP_TYPE.HYPERLINK, is_external=True)
    h = OxmlElement("w:hyperlink"); h.set(qn("r:id"), rid)
    r = OxmlElement("w:r"); rpr = OxmlElement("w:rPr")
    c = OxmlElement("w:color"); c.set(qn("w:val"), "1F4E9A"); rpr.append(c)
    u = OxmlElement("w:u"); u.set(qn("w:val"), "single"); rpr.append(u)
    sz = OxmlElement("w:sz"); sz.set(qn("w:val"), str(int(size * 2))); rpr.append(sz)
    r.append(rpr)
    t = OxmlElement("w:t"); t.text = text; t.set(qn("xml:space"), "preserve"); r.append(t)
    h.append(r); p._p.append(h)

def cell(c, text, size=8.5, bold=False, align=None):
    p = c.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    if align:
        p.alignment = align
    setfont(p.add_run(text or ""), size, bold)
    return p

def shade(c, color="D9D9D9"):
    tcPr = c._tc.get_or_add_tcPr()
    s = OxmlElement("w:shd"); s.set(qn("w:val"), "clear"); s.set(qn("w:color"), "auto"); s.set(qn("w:fill"), color); tcPr.append(s)

def repeat_header(row):
    trPr = row._tr.get_or_add_trPr()
    e = OxmlElement("w:tblHeader"); e.set(qn("w:val"), "true"); trPr.append(e)

def no_split(row):
    trPr = row._tr.get_or_add_trPr()
    e = OxmlElement("w:cantSplit"); e.set(qn("w:val"), "true"); trPr.append(e)

def widths(table, ws):
    table.autofit = False
    for row in table.rows:
        for c, w in zip(row.cells, ws):
            c.width = Cm(w)

# ---------- title
p = para("哥伦比亚女神（Columbia）图像资料目录", 22, True, False, WD_ALIGN_PARAGRAPH.CENTER, "黑体", 6)
para("美国早期历史图像史研究 · 形象及其演变", 14, False, False, WD_ALIGN_PARAGRAPH.CENTER, "黑体", 6)
para("检索与编目日期：%s　　共收图像 %d 件" % (datetime.date.today().strftime("%Y年%m月%d日"), len(cat)), 10.5, False, False, WD_ALIGN_PARAGRAPH.CENTER, after=14)

# ---------- 1 说明
doc.add_heading("一、编目说明", 1)
srcs = collections.Counter(r["src"] for r in cat)
SRCN = {"LOC": "美国国会图书馆（Library of Congress）版画与照片部在线目录", "Commons": "维基共享资源（Wikimedia Commons），其中多数文件转自 LOC、NYPL、大英博物馆、荷兰国立博物馆、耶鲁等馆藏",
        "JCB": "约翰·卡特·布朗图书馆（John Carter Brown Library）早期美洲图像库与政治漫画库", "DC": "Digital Commonwealth（波士顿公共图书馆等马萨诸塞州馆藏）",
        "MET": "大都会艺术博物馆（The Met Open Access）", "AIC": "芝加哥艺术博物馆（Art Institute of Chicago）", "SI": "史密森尼学会开放获取（Smithsonian Open Access）"}
para("本目录围绕美国的女性国家拟人形象“哥伦比亚”（Columbia）编制，同时收入与其形成和演变直接相关的几类图像：欧洲“四大洲”寓意传统中的“亚美利加”，革命时期英美讽刺版画里作为印第安女子出现的“美洲”，建国初期与哥伦比亚重叠的“自由女神”（Liberty），以及长期与她并行或配对的乔纳森兄弟（Brother Jonathan）和山姆大叔。")
para("图像按载体与体裁分为 %d 类，每类一个文件夹；类内按年代先后排列。编号格式为“类号-序号”，例如 03-0125 即第 3 类第 125 件，文件名以编号开头，后接年份、来源代码与题名缩写，可与本目录及同目录下的 Excel 表逐条对应。" % len(set(r["type"] for r in cat)))
para("题名、作者、媒介与说明均照录馆藏方的原始著录（多为英文），未作翻译，便于回查与引用。年份取自著录中的首个四位年份，凡“年代不详”或著录含糊者请以原始页面为准；维基共享资源的文件日期著录不稳定，个别条目的年份可能是拍摄或上传年份。")
para("分类由程序依据著录关键词判定，体裁优先于技法（例如石版印制的政治漫画归入“政治漫画与讽刺画”）。著录信息不足的条目归入最后一类“其他与未细分”，其中仍有不少刊物漫画和版画，使用时宜逐件核看。")
para("版权方面：所收图像绝大多数作于 1930 年以前，在美国已进入公有领域，但各馆权利声明不一。正式发表前请点开“原始页面”核对该件的权利说明，并按馆方要求署明馆藏。本地保存的是 1000–2000 像素的研究用图，出版级高清图（TIFF）可从原始页面下载。")
para("各来源收录数量如下：", indent=True)
t = doc.add_table(rows=1, cols=3); t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
for c, x in zip(t.rows[0].cells, ["代码", "来源", "件数"]):
    cell(c, x, 9.5, True, WD_ALIGN_PARAGRAPH.CENTER); shade(c)
for s, n in srcs.most_common():
    row = t.add_row().cells
    cell(row[0], s, 9.5, align=WD_ALIGN_PARAGRAPH.CENTER); cell(row[1], SRCN.get(s, s), 9.5); cell(row[2], str(n), 9.5, align=WD_ALIGN_PARAGRAPH.CENTER)
widths(t, [2.2, 19, 2.2])
para("另有几家重要馆藏因接口限制未能批量抓取，需要时可人工补检：美国古物学会（American Antiquarian Society）、费城图书馆公司（Library Company of Philadelphia）、纽约公共图书馆数字馆藏、耶鲁大学刘易斯·沃波尔图书馆（英国讽刺版画）、大英博物馆版画部、Winterthur 与 HarpWeek（《哈珀周刊》漫画）。", after=10)

# ---------- 2 演变线索
doc.add_heading("二、形象演变线索（检索导引）", 1)
para("以下六段只是帮助在目录中定位图像的时间框架，不是结论。各段末尾标出可重点翻检的类别。")
stages = [
    ("1. 十六至十八世纪中叶：四大洲寓意中的“亚美利加”", "欧洲图像传统把美洲画成头戴羽冠、手持弓箭、身旁伴有鳄鱼或犰狳的印第安女王，与欧、亚、非三洲并列，常见于地图装饰框、书籍扉页和成套版画。这是后来一切美洲女性拟人形象的起点。重点类别：07、06。"),
    ("2. 1765–1783 年：英美讽刺版画中的“印第安公主”", "印花税危机到独立战争期间，伦敦的讽刺版画普遍以年轻的印第安女子代表北美殖民地，她多以不列颠尼亚（Britannia）之女的身份出现，或受辱，或反抗，或与母亲和解。《能干的医生，或美洲吞下苦药》（The able doctor, 1774）及其美洲翻刻本是这一阶段流传最广的图像。重点类别：03（JCB 政治漫画库条目集中于此）。"),
    ("3. 1770 年代末至 1810 年代：新古典化与“哥伦比亚”之名", "独立之后，印第安特征逐渐让位于古典女神装束：长袍、自由帽与自由杖、盾牌、鹰。这一时期“自由”“美利坚”“哥伦比亚”三者在图像上常难以区分；“哥伦比亚”一名经诗歌和歌曲（如 1798 年的《Hail, Columbia》）普及开来，也出现在《哥伦比亚杂志》等刊物的卷首画中。重点类别：01、06、05、12。"),
    ("4. 1816–1860 年：形象定型", "哥伦比亚成为固定的国家象征，出现在石版画、竞选旗帜、证书、纸币和乐谱封面上，通常身披星条、手扶盾牌；男性形象乔纳森兄弟则在漫画中承担更具市井气的“美国人”角色。重点类别：02、10、11、05。"),
    ("5. 1861–1900 年：内战、重建与镀金时代的刊物漫画", "内战时期的爱国信封、《哈珀周刊》上托马斯·纳斯特的作品，以及此后《顽童》（Puck）、《法官》（Judge）的彩色石印漫画，使哥伦比亚成为国家良知的化身：哀悼、训诫、主持公道，并与山姆大叔配对出现。涉及重建、移民、排华、印第安政策和海外扩张的图像尤其多。重点类别：03、11、02。"),
    ("6. 1890 年代至 1920 年代：世博会、帝国与一战动员，及其后的淡出", "1893 年芝加哥哥伦布纪念博览会把哥伦比亚推上纪念性雕塑的高峰；美西战争前后的漫画让她充当古巴、菲律宾等“新属地”的监护人；一战的征兵与公债海报则是她最后一次大规模出场。此后国家拟人的功能基本由自由女神像和山姆大叔承担。重点类别：04、09、03、13。"),
]
for h, b in stages:
    para(h, 11, True, False, east="黑体", after=2)
    para(b, after=6)

# ---------- 3 统计
doc.add_heading("三、类型与时期统计", 1)
labels = []
for r in cat:
    if (r["type"], r["type_label"]) not in labels:
        labels.append((r["type"], r["type_label"]))
labels.sort()
pers = sorted(set(r["period"] for r in cat), key=lambda x: (x == "年代不详", x))
short = lambda s: s.split("：")[0]
t = doc.add_table(rows=1, cols=len(pers) + 2); t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
hdr = ["类型"] + [short(x) for x in pers] + ["合计"]
for c, x in zip(t.rows[0].cells, hdr):
    cell(c, x, 8.5, True, WD_ALIGN_PARAGRAPH.CENTER); shade(c)
M = collections.Counter((r["type"], r["period"]) for r in cat)
for code, lab in labels:
    row = t.add_row().cells
    cell(row[0], code + " " + lab, 8.5)
    tot = 0
    for i, pn in enumerate(pers):
        n = M[(code, pn)]; tot += n
        cell(row[i + 1], str(n) if n else "", 8.5, align=WD_ALIGN_PARAGRAPH.CENTER)
    cell(row[-1], str(tot), 8.5, True, WD_ALIGN_PARAGRAPH.CENTER)
row = t.add_row().cells
cell(row[0], "合计", 8.5, True)
for i, pn in enumerate(pers):
    cell(row[i + 1], str(sum(M[(c, pn)] for c, _ in labels)), 8.5, True, WD_ALIGN_PARAGRAPH.CENTER)
cell(row[-1], str(len(cat)), 8.5, True, WD_ALIGN_PARAGRAPH.CENTER)
widths(t, [7.2] + [2.0] * len(pers) + [1.8])
para("时期划分：" + "；".join(x for x in pers if x != "年代不详") + "。", 9, indent=False, after=8)

# ---------- 4 分类目录
doc.add_heading("四、分类目录", 1)
W = [1.7, 3.3, 7.6, 2.2, 6.6, 4.7]
for code, lab in labels:
    items = [r for r in cat if r["type"] == code]
    doc.add_heading("%s　%s（%d 件）" % (code, lab, len(items)), 2)
    para("文件夹：图像/%s" % os.path.basename(os.path.dirname(items[0]["file"])), 9, indent=False, after=4)
    t = doc.add_table(rows=1, cols=6); t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for c, x in zip(t.rows[0].cells, ["编号", "缩略图", "题名 / 作者", "年代", "媒介与说明", "馆藏与链接"]):
        cell(c, x, 9, True, WD_ALIGN_PARAGRAPH.CENTER); shade(c)
    repeat_header(t.rows[0])
    for r in items:
        rw = t.add_row(); no_split(rw); cs = rw.cells
        cell(cs[0], r["cid"], 8.5, True, WD_ALIGN_PARAGRAPH.CENTER)
        p = cs[1].paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_after = Pt(0)
        try:
            from PIL import Image
            w, h = Image.open(r["thumb"]).size
            if h > w * 1.25:
                p.add_run().add_picture(r["thumb"], height=Cm(3.4))
            else:
                p.add_run().add_picture(r["thumb"], width=Cm(2.9))
        except Exception:
            setfont(p.add_run("（无缩略图）"), 8)
        cell(cs[2], (r["title"] or "")[:260], 9, True)
        if r.get("creator"):
            q = cs[2].add_paragraph(); q.paragraph_format.space_after = Pt(0)
            setfont(q.add_run(r["creator"][:160]), 8.5)
        cell(cs[3], (r.get("date") or "")[:40] or (str(r["year"]) if r.get("year") else "不详"), 8.5, align=WD_ALIGN_PARAGRAPH.CENTER)
        med = (r.get("medium") or "")[:140]
        cell(cs[4], med, 8.5)
        d = (r.get("desc") or "")
        if d:
            d = d[:330] + ("…" if len(d) > 330 else "")
            q = cs[4].add_paragraph() if med else cs[4].paragraphs[0]
            q.paragraph_format.space_after = Pt(0)
            setfont(q.add_run(d), 8)
        cell(cs[5], (r.get("repo") or "")[:120], 8.5)
        if r.get("call"):
            q = cs[5].add_paragraph(); q.paragraph_format.space_after = Pt(0)
            setfont(q.add_run(r["call"][:60]), 8)
        if r.get("url"):
            q = cs[5].add_paragraph(); q.paragraph_format.space_after = Pt(0)
            link(q, r["url"], "原始页面")
    widths(t, W)
    doc.add_paragraph()
doc.save(os.path.join(OUT, "哥伦比亚女神图像资料目录.docx"))
print("docx saved", len(cat))
