import json, os, sys, time, hashlib, io, threading, collections
import requests
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36 image-history-research"}
CACHE = "cache"
os.makedirs(CACHE, exist_ok=True)
recs = json.load(open("records.json", encoding="utf-8"))
DELAY = {"Commons": 1.2, "LOC": 0.6, "JCB": 0.5, "DC": 0.5, "MET": 0.5, "AIC": 1.0, "SI": 0.5}
lock = threading.Lock()
stat = collections.Counter()

def key(r):
    return hashlib.sha1((r["src"] + "|" + r["sid"]).encode("utf-8")).hexdigest()[:16]

def fetch(r):
    k = key(r)
    out = os.path.join(CACHE, k + ".jpg")
    if os.path.exists(out) and os.path.getsize(out) > 3000:
        return "have"
    urls = [u for u in r["img"] if u]
    if r["src"] == "MET":
        urls = urls[::-1]
    for u in urls:
        for attempt in range(3):
            try:
                resp = requests.get(u, headers=H, timeout=90)
                if resp.status_code == 429 or resp.status_code >= 500:
                    time.sleep(20 * (attempt + 1))
                    continue
                if resp.status_code != 200 or len(resp.content) < 3000:
                    break
                im = Image.open(io.BytesIO(resp.content))
                im.load()
                fmt = (im.format or "").upper()
                if fmt == "JPEG" and max(im.size) <= 4000:
                    open(out, "wb").write(resp.content)
                else:
                    if im.mode not in ("RGB", "L"):
                        im = im.convert("RGB")
                    if max(im.size) > 3000:
                        im.thumbnail((3000, 3000))
                    im.save(out, "JPEG", quality=90)
                return "ok"
            except Exception as e:
                time.sleep(5)
        time.sleep(0.5)
    return "fail"

def worker(src, items):
    for r in items:
        s = fetch(r)
        with lock:
            stat[(src, s)] += 1
        if s != "have":
            time.sleep(DELAY.get(src, 0.5))
    print("finished", src, flush=True)

by = collections.defaultdict(list)
for r in recs:
    if r["src"] == "Commons":
        continue
    by[r["src"]].append(r)
ths = []
for src, items in by.items():
    n = 2 if src in ("LOC", "JCB") else 1
    for i in range(n):
        t = threading.Thread(target=worker, args=(src, items[i::n]))
        t.start()
        ths.append(t)
while any(t.is_alive() for t in ths):
    time.sleep(60)
    print(dict(stat), flush=True)
print("DONE", dict(stat))
