"""Fit lon/lat -> pixel transforms for the six historical maps (Albers conic + affine least squares)."""
import json, math
import numpy as np

def albers(lon, lat, lon0=-96.0, lat0=37.5, p1=29.5, p2=45.5):
    r = math.radians
    n = (math.sin(r(p1)) + math.sin(r(p2))) / 2
    C = math.cos(r(p1)) ** 2 + 2 * n * math.sin(r(p1))
    rho = lambda la: math.sqrt(C - 2 * n * math.sin(r(la))) / n
    th = n * r(lon - lon0)
    return rho(lat) * math.sin(th), rho(lat0) - rho(lat) * math.cos(th)

G = {  # lon, lat
    "boston": (-71.06, 42.36), "newyork": (-74.01, 40.71), "phila": (-75.16, 39.95), "baltimore": (-76.61, 39.29),
    "washington": (-77.04, 38.90), "capecod": (-70.19, 42.05), "capemay": (-74.91, 38.93), "capehenry": (-76.01, 36.93),
    "albany": (-73.75, 42.65), "hatteras": (-75.52, 35.25), "missmouth": (-89.25, 29.15), "michsouth": (-87.25, 41.62),
    "charleston": (-79.93, 32.78), "staugustine": (-81.31, 29.90), "savannah": (-80.85, 32.03), "richmond": (-77.44, 37.54),
    "detroit": (-83.05, 42.33), "sf": (-122.42, 37.78), "neworleans": (-90.07, 29.95), "capesable": (-81.09, 25.12),
    "riogrande": (-97.15, 25.95), "portland": (-70.26, 43.66), "buffalo": (-78.88, 42.89), "sandiego": (-117.16, 32.72),
    "duluth": (-92.10, 46.78), "pittsburgh": (-80.00, 40.44), "chicago": (-87.63, 41.88), "seattle": (-122.33, 47.60),
}
CP = {
    "m1": {"size": (5200, 3569), "pts": {"boston": (3460, 1457), "newyork": (3127, 1685), "phila": (2987, 1790), "baltimore": (2877, 1873),
           "capecod": (3560, 1497), "capehenry": (2920, 2235), "capemay": (3037, 1945), "albany": (3160, 1395),
           "missmouth": (1250, 3400), "michsouth": (1943, 1467), "hatteras": (2940, 2427)}},
    "m2": {"size": (5200, 4453), "pts": {"boston": (3151, 1933), "newyork": (2773, 2188), "phila": (2616, 2309), "baltimore": (2492, 2393),
           "capecod": (3275, 1994), "capemay": (2634, 2463), "albany": (2822, 1843), "missmouth": (1017, 3983),
           "michsouth": (1667, 2017), "hatteras": (2533, 3017), "charleston": (2300, 3283), "staugustine": (2083, 3867)}},
    "m3": {"size": (5200, 3781), "pts": {"boston": (4275, 912), "newyork": (3835, 1282), "phila": (3600, 1465), "baltimore": (3420, 1580),
           "washington": (3285, 1680), "capecod": (4440, 965), "capemay": (3715, 1675), "albany": (3830, 855),
           "hatteras": (3500, 2333), "michsouth": (1800, 1000), "savannah": (2573, 3343)}},
    "m4": {"size": (5200, 4270), "pts": {"boston": (3727, 1023), "newyork": (3570, 1177), "phila": (3503, 1237), "baltimore": (3433, 1317),
           "washington": (3407, 1360), "capecod": (3797, 1023), "richmond": (3413, 1460), "albany": (3540, 1005), "detroit": (2963, 1077),
           "sf": (427, 1317), "neworleans": (2577, 2110), "capesable": (3227, 2483), "michsouth": (2683, 1117), "riogrande": (1993, 2483)}},
    "m5": {"size": (5600, 3167), "pts": {"boston": (5074, 966), "newyork": (4850, 1226), "phila": (4754, 1338), "baltimore": (4614, 1450),
           "capecod": (5154, 986), "capemay": (4798, 1462), "portland": (5098, 790), "buffalo": (4450, 986),
           "sf": (251, 1436), "neworleans": (3357, 2710), "michsouth": (3600, 1256), "riogrande": (2728, 3033), "sandiego": (592, 2226), "duluth": (3123, 682)}},
    "m6": {"size": (5200, 3460), "pts": {"boston": (4801, 866), "newyork": (4610, 1134), "phila": (4515, 1245), "baltimore": (4419, 1355),
           "washington": (4390, 1407), "pittsburgh": (4097, 1269), "buffalo": (4130, 978), "capecod": (4881, 875), "albany": (4559, 901),
           "sf": (310, 1327), "chicago": (3433, 1190), "neworleans": (3367, 2633), "capesable": (4300, 3017), "riogrande": (2567, 3093),
           "sandiego": (633, 2040), "seattle": (550, 317)}},
}
out = {}
for m, d in CP.items():
    names = list(d["pts"])
    A = []; bx = []; by = []
    for n in names:
        x, y = albers(*G[n])
        A.append([x, y, 1]); bx.append(d["pts"][n][0]); by.append(d["pts"][n][1])
    A = np.array(A)
    cx, *_ = np.linalg.lstsq(A, np.array(bx), rcond=None)
    cy, *_ = np.linalg.lstsq(A, np.array(by), rcond=None)
    res = [(n, round(float(A[i] @ cx - bx[i])), round(float(A[i] @ cy - by[i]))) for i, n in enumerate(names)]
    rms = math.sqrt(sum(a * a + b * b for _, a, b in res) / len(res))
    print(m, "rms", round(rms), res)
    out[m] = {"size": d["size"], "ax": [float(v) for v in cx], "ay": [float(v) for v in cy]}
json.dump(out, open("mapfit.json", "w"), indent=1)
