# 哥伦比亚女神图像志 · Columbia: An Iconographic Atlas

美国早期历史图像史研究用的本地图像史料网站，围绕美国的女性国家拟人形象“哥伦比亚”（Columbia）及其演变编制。

A local image-history site on Columbia, the female personification of the United States, and how the figure changed between the sixteenth century and the 1920s.

## 内容 / What is here

- **时间轴地图 / Time Atlas**：六幅历史地图（1755、1783、1804、1850、1876、1901）随年代切换，热力图显示所选年份或年段内图像出版地的数量分布。Six period maps that change with the selected years, with a heat layer of where the images were published.
- **分类检索库 / Archive**：按类型、阶段、年代、出版地和馆藏来源筛选，可检索题名、作者与说明。Search and filter by type, stage, date, place and holding institution.
- **中英双语界面 / Bilingual interface**（右上角切换 / toggle at top right）。
- `catalog/`：Word 与 Excel 版图像目录。The catalogue as a Word document and a spreadsheet.
- `tools/`：检索、筛选、下载与生成网站数据的 Python 脚本。Python scripts used to harvest, filter and build.

## 本地打开 / Running locally

Windows 下双击 `启动网站.bat`，或在本目录运行：

```bash
python -m http.server 8811 --bind 127.0.0.1
```

然后访问 <http://127.0.0.1:8811/>。

## 图像来源 / Sources

美国国会图书馆（Library of Congress）、维基共享资源（Wikimedia Commons）、约翰·卡特·布朗图书馆（John Carter Brown Library）、Digital Commonwealth、大都会艺术博物馆（The Met Open Access）、芝加哥艺术博物馆（Art Institute of Chicago）、史密森尼学会（Smithsonian Open Access）。六幅底图均出自美国国会图书馆地理与地图部，仅作轻度对比度与清晰度调整。

每件图像在详情中都给出馆藏、原始页面链接与权利说明。Every item links back to its source record and carries the rights note given there.

## 权利说明 / Rights

- 本仓库的代码与编目数据供研究使用。Code and catalogue data are offered for research use.
- 图像版权不属于本仓库。绝大多数图像作于 1930 年以前，在美国已进入公有领域；来自维基共享资源的部分现代照片（雕塑、建筑等）采用 CC BY 或 CC BY-SA 等许可，使用时须按其原始页面的要求署名。
- Images are not owned by this repository. Most were made before 1930 and are in the public domain in the United States; some modern photographs from Wikimedia Commons (of sculpture and buildings) are under CC BY or CC BY-SA and must be credited as their source pages require.
- 发表或再利用任何图像前，请以原始页面的权利声明为准。Check the source page before publishing or reusing any image. 如权利人认为某件图像不应在此出现，请提交 issue，将予移除。Rights holders may open an issue to request removal.

## 使用须知 / Caveats

- 热力图依据的是出版地（或雕塑、建筑所在地），不是图像描绘的地点；约半数图像的著录没有出版地，未计入热力图。The heat layer plots place of publication, not subject; about half the items have no recorded place and are left out of it.
- 部分出版地按所属刊物或出版商推定，详情中标明依据。Some places are inferred from the periodical or publisher, and the detail view says so.
- 题名、作者与说明照录馆藏方原始著录；年份取著录中的首个四位年份，引用前请核对原始页面。Titles and descriptions are as catalogued; the year is the first four-digit year in the record, so verify before citing.
- 分类由程序依据著录关键词判定，个别条目可能归类不当。Types are assigned by keyword rules and a few items may be misfiled.
