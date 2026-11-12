(function () {
  'use strict';
  var D = window.COLUMBIA_DATA;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var esc = function (s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); };

  /* ------------------------------------------------------------ data prep */
  var ITEMS = D.items;
  var Y1 = 1950;
  ITEMS.forEach(function (it) {
    // Commons often records the photograph/upload date for objects; treat such late dates as undated
    if (it.y && it.s === 'Commons' && it.y > Y1) { it.y = null; it.st = 0; }
    if (it.y && it.y > Y1) { it.y = null; it.st = 0; }
  });
  var minY = Math.min.apply(null, ITEMS.filter(function (i) { return i.y; }).map(function (i) { return i.y; }));
  var Y0 = Math.max(1500, Math.floor(minY / 10) * 10);
  var PLACES = D.places, MAPS = D.maps, TYPES = D.types, SOURCES = D.sources;
  var TYPE = {}; TYPES.forEach(function (t) { TYPE[t.k] = t; });
  var BYID = {}; ITEMS.forEach(function (i) { BYID[i.id] = i; });

  var STAGES = [
    { n: 1, from: Y0, to: 1764, zh: '四大洲寓意中的“亚美利加”', en: 'America among the Four Continents',
      pz: '欧洲图像传统把美洲画成头戴羽冠、手持弓箭、身旁伴有鳄鱼或犰狳的印第安女王，与欧、亚、非三洲并列，常见于地图装饰框、书籍扉页和成套版画。这是后来一切美洲女性拟人形象的起点。',
      pe: 'European convention pictured America as an Indian queen in a feathered crown, bow in hand, an alligator or armadillo at her side, set beside Europe, Asia and Africa on map cartouches, title pages and print series. Every later female personification of America starts here.' },
    { n: 2, from: 1765, to: 1783, zh: '讽刺版画中的“印第安公主”', en: 'The Indian Princess of the satires',
      pz: '从印花税危机到独立战争，伦敦的讽刺版画普遍以年轻的印第安女子代表北美殖民地。她多以不列颠尼亚之女的身份出现，或受辱，或反抗，或与母亲和解。',
      pe: 'From the Stamp Act crisis to the War of Independence, London satires cast the colonies as a young Indian woman, usually the daughter of Britannia: abused, defiant, or at last reconciled with her mother.' },
    { n: 3, from: 1784, to: 1815, zh: '新古典化与“哥伦比亚”之名', en: 'A classical goddess named Columbia',
      pz: '独立之后，印第安特征逐渐让位于古典女神装束：长袍、自由帽与自由杖、盾牌、鹰。“自由”“美利坚”“哥伦比亚”三者在图像上常难以区分，“哥伦比亚”一名则经诗歌、歌曲和刊物卷首画普及开来。',
      pe: 'After independence the Indian attributes give way to classical dress: gown, liberty cap and pole, shield, eagle. Liberty, America and Columbia are often indistinguishable, while the name Columbia spreads through verse, song and magazine frontispieces.' },
    { n: 4, from: 1816, to: 1860, zh: '形象定型', en: 'The figure settles',
      pz: '哥伦比亚成为固定的国家象征，出现在石版画、竞选旗帜、证书、纸币和乐谱封面上，通常身披星条、手扶盾牌；乔纳森兄弟则在漫画中承担更具市井气的“美国人”角色。',
      pe: 'Columbia becomes a fixed national emblem on lithographs, campaign banners, certificates, banknotes and sheet music, draped in stars and stripes with her shield, while Brother Jonathan plays the plain-spoken American in cartoons.' },
    { n: 5, from: 1861, to: 1897, zh: '内战、重建与镀金时代的刊物漫画', en: 'Civil War, Reconstruction and the Gilded Age press',
      pz: '内战时期的爱国信封、《哈珀周刊》上纳斯特的作品，以及《顽童》《法官》的彩色石印漫画，使哥伦比亚成为国家良知的化身：哀悼、训诫、主持公道，并与山姆大叔配对出现。',
      pe: 'Patriotic envelopes of the war years, Thomas Nast in Harper’s Weekly, and the chromolithographed cartoons of Puck and Judge make Columbia the conscience of the nation: mourning, admonishing, dispensing justice, and paired with Uncle Sam.' },
    { n: 6, from: 1898, to: Y1, zh: '帝国、世博会与一战动员，及其后的淡出', en: 'Empire, expositions, the Great War, and after',
      pz: '美西战争前后的漫画让她充当古巴、菲律宾等“新属地”的监护人；一战的征兵与公债海报是她最后一次大规模出场。此后国家拟人的功能基本由自由女神像和山姆大叔承担。',
      pe: 'Around the war with Spain she acts as guardian to Cuba, the Philippines and other new possessions; the recruiting and Liberty Loan posters of the Great War are her last mass appearance, before the Statue of Liberty and Uncle Sam take over.' }
  ];
  var ROMAN = ['', 'I', 'II', 'III', 'IV', 'V', 'VI'];

  /* ------------------------------------------------------------ i18n */
  var LANG = 'zh';
  try { LANG = localStorage.getItem('columbia.lang') || 'zh'; } catch (e) {}
  var T = {
    brand: ['哥伦比亚女神图像志', 'Columbia · An Iconographic Atlas'],
    nav_stages: ['六个阶段', 'Six Stages'], nav_atlas: ['时间轴地图', 'Time Atlas'], nav_archive: ['检索库', 'Archive'], nav_about: ['来源说明', 'Sources'],
    hero_kicker: ['美国早期历史图像史料库', 'A Visual Archive of Early American History'],
    hero_title: ['哥伦比亚女神图像志', 'An Iconographic Atlas'],
    hero_sub: ['一个国家拟人形象的生成与演变 · ' + Y0 + '—1930', 'The making and remaking of a national personification · ' + Y0 + '–1930'],
    hero_lede: ['从四大洲寓意里头戴羽冠的“亚美利加”，到英美讽刺版画中的印第安公主，再到身披星条、手扶盾牌的古典女神——本库汇集各大图书馆与博物馆公开的版画、漫画、海报、乐谱封面、钱币与雕塑图像，按类型编目，并以历史地图和时间轴呈现其出版地与年代分布。',
      'From the feather-crowned “America” of the Four Continents, through the Indian Princess of Anglo-American satire, to the classical goddess wrapped in stars and stripes: prints, cartoons, posters, sheet music, coins and sculpture gathered from open library and museum collections, catalogued by type and set upon period maps and a timeline of where and when they were made.'],
    cta_atlas: ['进入时间轴地图', 'Open the Time Atlas'], cta_archive: ['检索全部图像', 'Search the Archive'],
    stages_title: ['形象演变的六个阶段', 'Six Stages of a Figure'], stages_sub: ['点击任一阶段，时间轴与地图将切换到对应年代', 'Choose a stage to move the timeline and the map to its years'],
    atlas_title: ['时间轴地图', 'The Time Atlas'], atlas_sub: ['拖动时间轴选择年份或年段；底图随年代更换为当时的地图，热力图显示图像出版地的数量分布', 'Drag the timeline to pick a year or a span; the base map changes to one of the period, and the heat layer shows where the images were published'],
    from: ['自', 'From'], to: ['至', 'To'], all_years: ['全部年代', 'All years'],
    tl_hint: ['提示：两个滑块重合即为单年；点击直方图上的柱子可直接选中该年。', 'Tip: bring the two handles together for a single year, or click a bar in the histogram.'],
    legend_few: ['少', 'Few'], legend_many: ['多', 'Many'],
    archive_title: ['分类检索库', 'The Archive'], archive_sub: ['按类型、阶段、来源、地点与年代筛选，或直接检索题名、作者与说明', 'Filter by type, stage, source, place and date, or search titles, makers and descriptions'],
    f_type: ['类型', 'Type'], f_stage: ['阶段', 'Stage'], f_year: ['年代', 'Date'], f_place: ['出版地 / 所在地', 'Place'], f_source: ['馆藏来源', 'Source'], f_reset: ['清除全部条件', 'Clear all filters'],
    sort: ['排序', 'Sort'], sort_ya: ['年代由早到晚', 'Oldest first'], sort_yd: ['年代由晚到早', 'Newest first'], sort_id: ['按编号', 'By number'], sort_ti: ['按题名', 'By title'],
    more: ['载入更多', 'Load more'],
    about_title: ['来源与说明', 'Sources & Notes'], about_src_h: ['图像来源', 'Image sources'], about_map_h: ['历史底图', 'Period maps'], about_method_h: ['使用须知', 'Reading the atlas'],
    about_map_note: ['底图均出自美国国会图书馆地理与地图部。为便于屏幕阅读，仅作了轻度的对比度与清晰度调整，未改动图面内容。', 'All base maps come from the Geography and Map Division of the Library of Congress. Contrast and sharpness were adjusted slightly for the screen; nothing on the sheets was altered.'],
    about_m1: ['热力图依据的是图像的出版地（或雕塑、建筑所在地），而不是图像描绘的地点。出版地取自馆藏著录；著录未载时，按所属刊物或出版商推定（如《顽童》《法官》《哈珀周刊》均在纽约）。', 'The heat layer plots where an image was published (or where a sculpture or building stands), not what it depicts. Places come from the holding institution’s record; where the record is silent, the place is inferred from the periodical or publisher (Puck, Judge and Harper’s Weekly, for example, were all New York papers).'],
    about_m3: ['题名、作者与说明照录馆藏方原始著录，未作翻译。年份取著录中的首个四位年份，使用时请以原始页面为准；发表前请核对各件的权利声明。', 'Titles, makers and descriptions are given as catalogued and are not translated. The year is the first four-digit year in the record, so check the source page before citing, and check each item’s rights statement before publishing.'],
    q_ph: ['检索题名、作者、说明、编号…', 'Search title, maker, description, number…'],
    undated: ['年代不详', 'Undated'], all: ['全部', 'All'], unknown_place: ['出版地未详', 'Place unknown'],
    n_items: ['件图像', 'images'], n_types: ['种类型', 'types'], n_sources: ['家馆藏来源', 'sources'], n_places: ['个出版地', 'places'],
    s_total: ['本时段图像', 'In this span'], s_onmap: ['地图上', 'On the map'], s_abroad: ['海外及图外', 'Off the map'], s_unk: ['出版地未详', 'Unlocated'],
    s_types: ['按类型', 'By type'], s_cities: ['出版地排行', 'Leading places'], s_view_all: ['在检索库中查看本时段全部图像 →', 'See every image of this span in the Archive →'],
    s_back: ['← 返回概览', '← Back to overview'], s_view_place: ['在检索库中查看此地全部图像 →', 'See all from this place in the Archive →'],
    s_pick: ['点击地图上的圆点，查看该地的图像', 'Click a marker on the map to see images from that place'],
    s_none: ['这一时段没有可定位的图像。', 'No images in this span can be placed.'],
    overseas_h: ['大西洋彼岸及图外出版地', 'Published across the Atlantic and off the map'], overseas_none: ['本时段没有海外出版的图像。', 'Nothing published abroad in this span.'],
    map_of: ['底图', 'Base map'], view_loc: ['国会图书馆原图 ↗', 'Library of Congress ↗'],
    d_no: ['编号', 'No.'], d_creator: ['作者 / 出版者', 'Maker'], d_date: ['年代', 'Date'], d_type: ['类型', 'Type'], d_stage: ['阶段', 'Stage'], d_medium: ['媒介', 'Medium'],
    d_desc: ['说明', 'Description'], d_subj: ['主题词', 'Subjects'], d_place: ['地点', 'Place'], d_repo: ['馆藏', 'Holding'], d_call: ['馆藏号', 'Call no.'], d_rights: ['权利', 'Rights'], d_file: ['本地原图', 'Local file'],
    d_src: ['原始页面 ↗', 'Source page ↗'], d_big: ['查看大图 ↗', 'Open large image ↗'], d_time: ['在时间轴上定位', 'Show on timeline'],
    b_pub: ['著录出版地', 'place of publication as catalogued'], b_serial: ['按刊物/出版商推定', 'inferred from periodical or publisher'], b_site: ['所在地', 'location of the work'],
    res: ['件', 'results'], res_of: ['共', 'of'],
    colophon: ['资料检索与编目于 ' + D.built + ' · 仅供研究使用', 'Compiled ' + D.built + ' · for research use']
  };
  function t(k) { var v = T[k]; return v ? v[LANG === 'zh' ? 0 : 1] : k; }
  function nm(o) { return o ? (LANG === 'zh' ? o.zh : o.en) : ''; }
  function placeName(k) { return k ? nm(PLACES[k]) : t('unknown_place'); }
  function stageLabel(n) { return n ? ROMAN[n] + ' · ' + nm(STAGES[n - 1]) : t('undated'); }
  function yrs(s) { return s.from + '–' + (s.n === 6 ? '1930s' : s.to); }

  /* ------------------------------------------------------------ state */
  var S = { a: 1765, b: 1783, place: null };
  var F = { q: '', types: {}, stages: {}, y0: null, y1: null, place: '', src: '', sort: 'ya', page: 1 };
  var PAGE = 60;

  /* ------------------------------------------------------------ hero + stages */
  function renderHero() {
    var cand = ITEMS.filter(function (i) { return /Columbia/i.test(i.t) && /Columbia \((Symbolic|personif)/i.test(i.sj) && !/Theatre|Brewing|Yarn/i.test(i.t) && i.y && i.h > i.w * 1.08 && ['02', '03', '04', '05', '11'].indexOf(i.ty) >= 0; });
    var pick = [];
    [3, 4, 5, 5, 6, 6].forEach(function (st, idx) {
      var c = cand.filter(function (i) { return i.st === st && pick.indexOf(i) < 0; });
      if (c.length) pick.push(c[Math.floor(c.length * (idx % 2 ? 0.7 : 0.25))]);
    });
    pick.sort(function (x, y) { return x.y - y.y; });
    $('#heroGallery').innerHTML = pick.slice(0, 5).map(function (i) {
      return '<figure data-id="' + i.id + '"><img src="img/t/' + i.id + '.jpg" alt="' + esc(i.t) + '"><figcaption>' + i.y + '</figcaption></figure>';
    }).join('');
    var located = ITEMS.filter(function (i) { return i.p; });
    var pset = {}; located.forEach(function (i) { pset[i.p] = 1; });
    $('#heroStats').innerHTML = [[ITEMS.length, 'n_items'], [TYPES.length, 'n_types'], [Object.keys(SOURCES).length, 'n_sources'], [Object.keys(pset).length, 'n_places']]
      .map(function (x) { return '<div><b>' + x[0] + '</b><span>' + t(x[1]) + '</span></div>'; }).join('');
  }
  function renderStages() {
    $('#stageGrid').innerHTML = STAGES.map(function (s) {
      var its = ITEMS.filter(function (i) { return i.st === s.n; });
      var th = []; var step = Math.max(1, Math.floor(its.length / 6));
      for (var k = 0; k < its.length && th.length < 6; k += step) th.push(its[k]);
      var on = (S.a === s.from && S.b === s.to) ? ' on' : '';
      return '<article class="stage-card' + on + '" data-stage="' + s.n + '"><span class="num">' + ROMAN[s.n] + '</span><div class="yrs">' + yrs(s) + '</div><h3>' + esc(nm(s)) + '</h3><p>' + esc(LANG === 'zh' ? s.pz : s.pe) + '</p>' +
        '<div class="thumbs">' + th.map(function (i) { return '<img loading="lazy" src="img/t/' + i.id + '.jpg" alt="">'; }).join('') + '</div>' +
        '<div class="meta"><span>' + its.length + ' ' + t('n_items') + '</span><span>' + t('map_of') + ' ' + MAPS[s.n - 1].year + '</span></div></article>';
    }).join('');
    $('#stageBtns').innerHTML = STAGES.map(function (s) {
      return '<button type="button" class="chip' + ((S.a === s.from && S.b === s.to) ? ' on' : '') + '" data-stage="' + s.n + '" title="' + esc(nm(s)) + '">' + ROMAN[s.n] + ' · ' + yrs(s) + '</button>';
    }).join('');
  }

  /* ------------------------------------------------------------ timeline */
  var HIST = {}; var HMAX = 1;
  ITEMS.forEach(function (i) { if (i.y) { HIST[i.y] = (HIST[i.y] || 0) + 1; } });
  Object.keys(HIST).forEach(function (y) { if (HIST[y] > HMAX) HMAX = HIST[y]; });
  var PAD = 10;
  function xOf(y, w) { return PAD + (y - Y0) / (Y1 - Y0) * (w - 2 * PAD); }
  function yearAt(x, w) { return Math.round(Y0 + (x - PAD) / (w - 2 * PAD) * (Y1 - Y0)); }
  function drawHisto() {
    var c = $('#histo'), w = c.clientWidth, h = c.clientHeight, dpr = window.devicePixelRatio || 1;
    c.width = w * dpr; c.height = h * dpr;
    var g = c.getContext('2d'); g.setTransform(dpr, 0, 0, dpr, 0, 0); g.clearRect(0, 0, w, h);
    var base = h - 12;
    STAGES.forEach(function (s) {
      var x0 = xOf(s.from - 0.5, w), x1 = xOf(s.to + 0.5, w);
      g.fillStyle = s.n % 2 ? 'rgba(27,42,74,.06)' : 'rgba(168,130,58,.10)'; g.fillRect(x0, 0, x1 - x0, base);
      g.fillStyle = 'rgba(27,42,74,.55)'; g.font = '600 13px Cinzel, serif'; g.textAlign = 'center'; g.fillText(ROMAN[s.n], (x0 + x1) / 2, 14);
    });
    var x0s = xOf(S.a - 0.5, w), x1s = xOf(S.b + 0.5, w);
    g.fillStyle = 'rgba(138,31,36,.13)'; g.fillRect(x0s, 0, Math.max(2, x1s - x0s), base);
    g.strokeStyle = 'rgba(138,31,36,.8)'; g.lineWidth = 1; g.strokeRect(x0s + .5, .5, Math.max(2, x1s - x0s) - 1, base - 1);
    var bw = Math.max(1, (w - 2 * PAD) / (Y1 - Y0) - 0.6);
    for (var y = Y0; y <= Y1; y++) {
      var n = HIST[y]; if (!n) continue;
      var bh = Math.max(2, Math.sqrt(n / HMAX) * (base - 22));
      g.fillStyle = (y >= S.a && y <= S.b) ? '#8a1f24' : 'rgba(27,42,74,.5)';
      g.fillRect(xOf(y, w) - bw / 2, base - bh, bw, bh);
    }
    g.strokeStyle = '#1b2a4a'; g.lineWidth = 2; g.beginPath(); g.moveTo(PAD, base + 1); g.lineTo(w - PAD, base + 1); g.stroke();
    g.strokeStyle = '#a8823a'; g.lineWidth = 1; g.beginPath(); g.moveTo(PAD, base + 5); g.lineTo(w - PAD, base + 5); g.stroke();
    var ax = $('#tlAxis'), html = '';
    for (var d = Math.ceil(Y0 / 50) * 50; d <= Y1; d += 50) html += '<span style="left:' + xOf(d, w) + 'px">' + d + '</span>';
    ax.innerHTML = html;
  }
  function setRange(a, b, keepPlace) {
    a = Math.max(Y0, Math.min(Y1, a | 0)); b = Math.max(Y0, Math.min(Y1, b | 0));
    if (a > b) { var x = a; a = b; b = x; }
    S.a = a; S.b = b; if (!keepPlace) S.place = null;
    $('#rFrom').value = a; $('#rTo').value = b; $('#yFrom').value = a; $('#yTo').value = b;
    $$('[data-stage]').forEach(function (el) { var s = STAGES[el.getAttribute('data-stage') - 1]; el.classList.toggle('on', s.from === a && s.to === b); });
    $('#allBtn').classList.toggle('on', a === Y0 && b === Y1);
    drawHisto(); updateAtlas();
  }
  var playing = null;
  function stopPlay() { if (playing) { clearInterval(playing); playing = null; $('#playBtn').textContent = '▶'; } }
  function initTimeline() {
    ['rFrom', 'rTo'].forEach(function (id) { var r = $('#' + id); r.min = Y0; r.max = Y1; r.step = 1; });
    $('#yFrom').min = $('#yTo').min = Y0; $('#yFrom').max = $('#yTo').max = Y1;
    $('#rFrom').addEventListener('input', function () { stopPlay(); var a = +this.value; setRange(Math.min(a, S.b), S.b); });
    $('#rTo').addEventListener('input', function () { stopPlay(); var b = +this.value; setRange(S.a, Math.max(b, S.a)); });
    $('#yFrom').addEventListener('change', function () { stopPlay(); setRange(+this.value || Y0, S.b); });
    $('#yTo').addEventListener('change', function () { stopPlay(); setRange(S.a, +this.value || Y1); });
    $('#allBtn').addEventListener('click', function () { stopPlay(); setRange(Y0, Y1); });
    $('#stepBack').addEventListener('click', function () { stopPlay(); if (S.a > Y0) setRange(S.a - 1, S.b - 1); });
    $('#stepFwd').addEventListener('click', function () { stopPlay(); if (S.b < Y1) setRange(S.a + 1, S.b + 1); });
    $('#playBtn').addEventListener('click', function () {
      if (playing) { stopPlay(); return; }
      var span = Math.min(Math.max(S.b - S.a, 4), 24);
      if (S.b >= Y1 - 1 || (S.b - S.a) > 24) setRange(1760, 1760 + span); else setRange(S.a, S.a + span);
      this.textContent = '❚❚';
      playing = setInterval(function () { if (S.b >= 1930) { stopPlay(); return; } setRange(S.a + 1, S.b + 1); }, 260);
    });
    $('#histo').addEventListener('click', function (e) {
      stopPlay(); var r = this.getBoundingClientRect(); var y = yearAt(e.clientX - r.left, r.width);
      // snap to the nearest year that has images within 3 years
      var best = null; for (var d = 0; d <= 3 && best === null; d++) { if (HIST[y - d]) best = y - d; else if (HIST[y + d]) best = y + d; }
      y = best === null ? y : best; setRange(y, y);
    });
    document.addEventListener('click', function (e) {
      var el = e.target.closest ? e.target.closest('[data-stage]') : null; if (!el) return;
      stopPlay(); var s = STAGES[el.getAttribute('data-stage') - 1]; setRange(s.from, s.to);
      if (el.classList.contains('stage-card')) $('#atlas').scrollIntoView();
    });
    window.addEventListener('resize', drawHisto);
  }

  /* ------------------------------------------------------------ map */
  var map, baseLayer = null, baseKey = null, heat = null, markers = null;
  function mapFor(y) {
    for (var i = 0; i < MAPS.length; i++) { var m = MAPS[i]; if ((m.from == null || y >= m.from) && (m.to == null || y <= m.to)) return m; }
    return MAPS[MAPS.length - 1];
  }
  function initMap() {
    map = L.map('map', { crs: L.CRS.Simple, minZoom: -4, maxZoom: 1.5, zoomSnap: 0.25, zoomDelta: 0.5, attributionControl: false, wheelPxPerZoomLevel: 110 });
    map.createPane('basemap'); map.getPane('basemap').style.zIndex = 150;
    markers = L.layerGroup().addTo(map);
  }
  function ll(m, p) { return [m.h - p[1], p[0]]; }
  function setBase(m) {
    if (baseKey === m.k) return;
    var bounds = [[0, 0], [m.h, m.w]];
    var lay = L.imageOverlay('maps/' + m.k + '.jpg', bounds, { pane: 'basemap', opacity: 0, className: 'basemap-img' });
    lay.addTo(map);
    var old = baseLayer; baseLayer = lay; baseKey = m.k;
    var el = lay.getElement(); if (el) { el.style.transition = 'opacity .6s'; }
    setTimeout(function () { lay.setOpacity(1); }, 30);
    if (old) setTimeout(function () { map.removeLayer(old); }, 650);
    map.setMaxBounds([[-m.h * 0.25, -m.w * 0.25], [m.h * 1.25, m.w * 1.25]]);
    map.setMinZoom(-6);
    var zc = map.getBoundsZoom(bounds, false), zi = map.getBoundsZoom(bounds, true);
    var xs = 0, ys = 0, n = 0; Object.keys(m.pts).forEach(function (k) { xs += m.pts[k][0]; ys += m.pts[k][1]; n++; });
    var ctr = n ? [m.h - ys / n, (xs / n + m.w / 2) / 2] : [m.h / 2, m.w / 2];
    map.setView(ctr, Math.min(zi, zc + 0.75), { animate: false });
    map.setMinZoom(zc - 0.25);
    $('#mapCaption').innerHTML = '<b>' + m.year + '</b><i>' + esc(m.title) + '</i><span>' + esc(m.maker) + ' · ' + esc(m.imprint) + '</span><a target="_blank" rel="noopener" href="' + m.url + '">' + t('view_loc') + '</a>';
  }
  function inRange() { return ITEMS.filter(function (i) { return i.y && i.y >= S.a && i.y <= S.b; }); }
  function updateAtlas() {
    if (!map) return;
    var m = mapFor(S.b); setBase(m);
    var its = inRange(), byP = {}, on = 0, off = 0, unk = 0;
    its.forEach(function (i) { if (!i.p) { unk++; return; } (byP[i.p] = byP[i.p] || []).push(i); if (m.pts[i.p]) on++; else off++; });
    var mx = 1; Object.keys(byP).forEach(function (k) { if (m.pts[k] && byP[k].length > mx) mx = byP[k].length; });
    var hp = [];
    markers.clearLayers();
    Object.keys(byP).filter(function (k) { return m.pts[k]; }).sort(function (a, b) { return byP[a].length - byP[b].length; }).forEach(function (k) {
      var n = byP[k].length, p = ll(m, m.pts[k]);
      hp.push([p[0], p[1], 0.3 + 0.7 * Math.sqrt(n / mx)]);
      var sz = Math.round(22 + 26 * Math.sqrt(n / mx));
      var mk = L.marker(p, { icon: L.divIcon({ className: '', iconSize: [sz, sz], html: '<div class="pm' + (S.place === k ? ' sel' : '') + '" style="width:' + sz + 'px;height:' + sz + 'px;font-size:' + (sz > 34 ? 14 : 12) + 'px">' + n + '</div>' }), riseOnHover: true });
      mk.bindTooltip(esc(placeName(k)) + ' · ' + n, { className: 'ptip', direction: 'top', offset: [0, -sz / 2] });
      mk.on('click', function () { S.place = k; updateAtlas(); });
      markers.addLayer(mk);
    });
    if (heat) { map.removeLayer(heat); heat = null; }
    if (hp.length) {
      heat = L.heatLayer(hp, { radius: 52, blur: 38, maxZoom: -8, max: 1, minOpacity: 0.28, gradient: { 0.15: '#2c426e', 0.45: '#b08a3e', 0.72: '#d8572a', 1: '#8a1f24' } }).addTo(map);
    }
    // off-map chips
    var offKeys = Object.keys(byP).filter(function (k) { return !m.pts[k]; }).sort(function (a, b) { return byP[b].length - byP[a].length; });
    $('#overseas').innerHTML = '<h4>' + t('overseas_h') + '</h4>' + (offKeys.length ? '<div class="chips">' + offKeys.map(function (k) {
      return '<button type="button" class="chip' + (S.place === k ? ' on' : '') + '" data-place="' + k + '">' + esc(placeName(k)) + '<b>' + byP[k].length + '</b></button>';
    }).join('') + '</div>' : '<p class="none">' + t('overseas_none') + '</p>');
    renderSide(its, byP, on, off, unk, m);
  }
  function rangeLabel() { return S.a === S.b ? String(S.a) : S.a + ' – ' + S.b; }
  function renderSide(its, byP, on, off, unk, m) {
    var h = '';
    if (S.place && byP[S.place]) {
      var list = byP[S.place].slice().sort(function (a, b) { return a.y - b.y; });
      h += '<div class="range-lbl">' + rangeLabel() + '</div><h3>' + esc(placeName(S.place)) + '</h3>' +
        '<p class="muted">' + list.length + ' ' + t('n_items') + '</p>' +
        '<div class="side-gallery">' + list.slice(0, 90).map(function (i) { return '<figure data-id="' + i.id + '" data-ctx="place"><img loading="lazy" src="img/t/' + i.id + '.jpg" alt="' + esc(i.t) + '" title="' + esc(i.t) + '"><figcaption>' + i.y + '</figcaption></figure>'; }).join('') + '</div>' +
        '<button type="button" class="lnk" id="sidePlaceAll">' + t('s_view_place') + '</button><br><button type="button" class="lnk" id="sideBack">' + t('s_back') + '</button>';
      $('#side').innerHTML = h; $('#side').scrollTop = 0;
      ctxList = list;
      return;
    }
    S.place = null;
    var sn = 0; STAGES.forEach(function (s) { if (S.b >= s.from && S.b <= s.to) sn = s.n; });
    h += '<div class="range-lbl">' + rangeLabel() + '</div><h3>' + (sn ? esc(stageLabel(sn)) : '') + '</h3>';
    h += '<div class="nums"><div><b>' + its.length + '</b><span>' + t('s_total') + '</span></div><div><b>' + on + '</b><span>' + t('s_onmap') + '</span></div><div><b>' + off + '</b><span>' + t('s_abroad') + '</span></div></div>';
    h += '<p class="muted">' + t('s_unk') + '：' + unk + '</p>';
    var pk = Object.keys(byP).sort(function (a, b) { return byP[b].length - byP[a].length; }).slice(0, 8);
    if (pk.length) {
      var mx = byP[pk[0]].length;
      h += '<h4>' + t('s_cities') + '</h4>' + pk.map(function (k) { return '<div class="bar-row" data-place="' + k + '"><div class="bl" style="--w:' + Math.round(byP[k].length / mx * 100) + '%"><span>' + esc(placeName(k)) + '</span></div><div class="bn">' + byP[k].length + '</div></div>'; }).join('');
    } else if (its.length) { h += '<p class="muted">' + t('s_none') + '</p>'; }
    var byT = {}; its.forEach(function (i) { byT[i.ty] = (byT[i.ty] || 0) + 1; });
    var tk = Object.keys(byT).sort(function (a, b) { return byT[b] - byT[a]; });
    if (tk.length) {
      var mt = byT[tk[0]];
      h += '<h4>' + t('s_types') + '</h4>' + tk.map(function (k) { return '<div class="bar-row" data-type="' + k + '"><div class="bl" style="--w:' + Math.round(byT[k] / mt * 100) + '%"><span>' + esc(nm(TYPE[k])) + '</span></div><div class="bn">' + byT[k] + '</div></div>'; }).join('');
    }
    var sample = its.slice().sort(function (a, b) { return a.y - b.y; });
    var st = Math.max(1, Math.floor(sample.length / 9)), sm = [];
    for (var k2 = 0; k2 < sample.length && sm.length < 9; k2 += st) sm.push(sample[k2]);
    if (sm.length) h += '<div class="side-gallery" style="margin-top:14px">' + sm.map(function (i) { return '<figure data-id="' + i.id + '" data-ctx="range"><img loading="lazy" src="img/t/' + i.id + '.jpg" alt="' + esc(i.t) + '" title="' + esc(i.t) + '"><figcaption>' + i.y + '</figcaption></figure>'; }).join('') + '</div>';
    h += '<p class="muted" style="margin-top:10px">' + t('s_pick') + '</p><button type="button" class="lnk" id="sideAll">' + t('s_view_all') + '</button>';
    $('#side').innerHTML = h;
    ctxList = sample;
  }
  var ctxList = [];
  function initAtlasEvents() {
    document.addEventListener('click', function (e) {
      var c = e.target.closest ? e.target : null; if (!c) return;
      var pl = c.closest('[data-place]');
      if (pl && (pl.closest('#side') || pl.closest('#overseas'))) { S.place = pl.getAttribute('data-place'); updateAtlas(); return; }
      var ty = c.closest('#side [data-type]');
      if (ty) { resetFilters(true); F.types[ty.getAttribute('data-type')] = 1; F.y0 = S.a; F.y1 = S.b; syncFilterUI(); renderArchive(); $('#archive').scrollIntoView(); return; }
      if (c.id === 'sideBack') { S.place = null; updateAtlas(); return; }
      if (c.id === 'sideAll') { resetFilters(true); F.y0 = S.a; F.y1 = S.b; syncFilterUI(); renderArchive(); $('#archive').scrollIntoView(); return; }
      if (c.id === 'sidePlaceAll') { resetFilters(true); F.y0 = S.a; F.y1 = S.b; F.place = S.place; syncFilterUI(); renderArchive(); $('#archive').scrollIntoView(); return; }
      var fig = c.closest('figure[data-id]');
      if (fig) { var id = fig.getAttribute('data-id'); var ctx = fig.getAttribute('data-ctx'); openItem(BYID[id], ctx ? ctxList : [BYID[id]]); }
    });
  }

  /* ------------------------------------------------------------ archive */
  ITEMS.forEach(function (i) {
    var p = i.p ? PLACES[i.p] : null;
    i._s = [i.id, i.t, i.c, i.ds, i.sj, i.m, i.rp, i.d, p ? p.en + ' ' + p.zh : '', TYPE[i.ty].zh, TYPE[i.ty].en].join(' ').toLowerCase();
  });
  function filtered() {
    var qs = F.q.toLowerCase().split(/\s+/).filter(Boolean);
    var tys = Object.keys(F.types), sts = Object.keys(F.stages);
    var r = ITEMS.filter(function (i) {
      if (tys.length && !F.types[i.ty]) return false;
      if (sts.length && !F.stages[i.st]) return false;
      if (F.src && i.s !== F.src) return false;
      if (F.place === '__none') { if (i.p) return false; } else if (F.place && i.p !== F.place) return false;
      if (F.y0 != null && !(i.y && i.y >= F.y0)) return false;
      if (F.y1 != null && !(i.y && i.y <= F.y1)) return false;
      for (var k = 0; k < qs.length; k++) if (i._s.indexOf(qs[k]) < 0) return false;
      return true;
    });
    var s = F.sort;
    r.sort(function (a, b) {
      if (s === 'id') return a.id < b.id ? -1 : 1;
      if (s === 'ti') return a.t.localeCompare(b.t);
      var ay = a.y || (s === 'ya' ? 99999 : -1), by = b.y || (s === 'ya' ? 99999 : -1);
      return (s === 'ya' ? ay - by : by - ay) || (a.id < b.id ? -1 : 1);
    });
    return r;
  }
  var lastRes = [];
  function cardHTML(i) {
    return '<article class="card" data-card="' + i.id + '"><div class="im"><img loading="lazy" src="img/t/' + i.id + '.jpg" alt="' + esc(i.t) + '"><span class="yr-tag">' + (i.y || '—') + '</span></div>' +
      '<div class="tx"><div class="ti">' + esc(i.t) + '</div>' + (i.c ? '<div class="cr">' + esc(i.c) + '</div>' : '') +
      '<div class="mt"><span>' + i.id + '</span><span>' + esc(nm(TYPE[i.ty]).split(/[（(,&]/)[0].slice(0, 26)) + '</span></div></div></article>';
  }
  function renderArchive() {
    lastRes = filtered();
    var n = lastRes.length, show = lastRes.slice(0, F.page * PAGE);
    $('#resCount').innerHTML = '<b>' + n + '</b> ' + t('res') + ' <span style="opacity:.6">/ ' + t('res_of') + ' ' + ITEMS.length + '</span>';
    $('#grid').innerHTML = show.length ? show.map(cardHTML).join('') : '<div class="empty">' + (LANG === 'zh' ? '没有符合条件的图像。试着放宽筛选条件。' : 'Nothing matches. Try loosening the filters.') + '</div>';
    $('#more').style.display = n > show.length ? '' : 'none';
    var ch = [];
    if (F.q) ch.push(['q', '“' + F.q + '”']);
    Object.keys(F.types).forEach(function (k) { ch.push(['t:' + k, nm(TYPE[k])]); });
    Object.keys(F.stages).forEach(function (k) { ch.push(['s:' + k, stageLabel(+k)]); });
    if (F.y0 != null || F.y1 != null) ch.push(['y', (F.y0 || '…') + '–' + (F.y1 || '…')]);
    if (F.place) ch.push(['p', F.place === '__none' ? t('unknown_place') : placeName(F.place)]);
    if (F.src) ch.push(['r', SOURCES[F.src][LANG === 'zh' ? 0 : 1]]);
    $('#activeFilters').innerHTML = ch.map(function (c) { return '<button type="button" class="chip" data-rm="' + c[0] + '">' + esc(c[1]) + '</button>'; }).join('');
  }
  function resetFilters(silent) { F.q = ''; F.types = {}; F.stages = {}; F.y0 = F.y1 = null; F.place = ''; F.src = ''; F.page = 1; if (!silent) { syncFilterUI(); renderArchive(); } }
  function syncFilterUI() {
    $('#q').value = F.q; $('#fy0').value = F.y0 == null ? '' : F.y0; $('#fy1').value = F.y1 == null ? '' : F.y1;
    $$('#fTypes input').forEach(function (c) { c.checked = !!F.types[c.value]; });
    $$('#fStages input').forEach(function (c) { c.checked = !!F.stages[c.value]; });
    $('#fPlace').value = F.place; $('#fSrc').value = F.src; $('#sort').value = F.sort; F.page = 1;
  }
  function buildFilterUI() {
    var ct = {}, cs = {}, cp = {}, cr = {}, none = 0;
    ITEMS.forEach(function (i) { ct[i.ty] = (ct[i.ty] || 0) + 1; cs[i.st] = (cs[i.st] || 0) + 1; cr[i.s] = (cr[i.s] || 0) + 1; if (i.p) cp[i.p] = (cp[i.p] || 0) + 1; else none++; });
    $('#fTypes').innerHTML = TYPES.map(function (x) { return '<label><input type="checkbox" value="' + x.k + '"><span>' + esc(nm(x)) + '</span><em>' + (ct[x.k] || 0) + '</em></label>'; }).join('');
    $('#fStages').innerHTML = STAGES.map(function (s) { return '<label><input type="checkbox" value="' + s.n + '"><span>' + ROMAN[s.n] + ' · ' + yrs(s) + ' ' + esc(nm(s)) + '</span><em>' + (cs[s.n] || 0) + '</em></label>'; }).join('') +
      '<label><input type="checkbox" value="0"><span>' + t('undated') + '</span><em>' + (cs[0] || 0) + '</em></label>';
    $('#fPlace').innerHTML = '<option value="">' + t('all') + '</option>' + Object.keys(cp).sort(function (a, b) { return cp[b] - cp[a]; }).map(function (k) { return '<option value="' + k + '">' + esc(placeName(k)) + '（' + cp[k] + '）</option>'; }).join('') + '<option value="__none">' + t('unknown_place') + '（' + none + '）</option>';
    $('#fSrc').innerHTML = '<option value="">' + t('all') + '</option>' + Object.keys(cr).sort(function (a, b) { return cr[b] - cr[a]; }).map(function (k) { return '<option value="' + k + '">' + esc(SOURCES[k][LANG === 'zh' ? 0 : 1]) + '（' + cr[k] + '）</option>'; }).join('');
    $('#q').placeholder = t('q_ph'); $('#fy0').placeholder = Y0; $('#fy1').placeholder = Y1;
    syncFilterUI();
  }
  function initArchiveEvents() {
    var tm = null;
    $('#q').addEventListener('input', function () { var v = this.value; clearTimeout(tm); tm = setTimeout(function () { F.q = v.trim(); F.page = 1; renderArchive(); }, 180); });
    $('#qClear').addEventListener('click', function () { F.q = ''; $('#q').value = ''; F.page = 1; renderArchive(); });
    $('#fTypes').addEventListener('change', function (e) { if (e.target.checked) F.types[e.target.value] = 1; else delete F.types[e.target.value]; F.page = 1; renderArchive(); });
    $('#fStages').addEventListener('change', function (e) { if (e.target.checked) F.stages[e.target.value] = 1; else delete F.stages[e.target.value]; F.page = 1; renderArchive(); });
    $('#fy0').addEventListener('change', function () { F.y0 = this.value === '' ? null : +this.value; F.page = 1; renderArchive(); });
    $('#fy1').addEventListener('change', function () { F.y1 = this.value === '' ? null : +this.value; F.page = 1; renderArchive(); });
    $('#fPlace').addEventListener('change', function () { F.place = this.value; F.page = 1; renderArchive(); });
    $('#fSrc').addEventListener('change', function () { F.src = this.value; F.page = 1; renderArchive(); });
    $('#sort').addEventListener('change', function () { F.sort = this.value; F.page = 1; renderArchive(); });
    $('#fReset').addEventListener('click', function () { resetFilters(); });
    $('#more').addEventListener('click', function () { F.page++; renderArchive(); });
    $('#grid').addEventListener('click', function (e) { var c = e.target.closest('[data-card]'); if (c) openItem(BYID[c.getAttribute('data-card')], lastRes); });
    $('#activeFilters').addEventListener('click', function (e) {
      var c = e.target.closest('[data-rm]'); if (!c) return; var k = c.getAttribute('data-rm');
      if (k === 'q') F.q = ''; else if (k === 'y') F.y0 = F.y1 = null; else if (k === 'p') F.place = ''; else if (k === 'r') F.src = '';
      else if (k.charAt(0) === 't') delete F.types[k.slice(2)]; else if (k.charAt(0) === 's') delete F.stages[k.slice(2)];
      syncFilterUI(); renderArchive();
    });
  }

  /* ------------------------------------------------------------ modal */
  var mList = [], mIdx = 0;
  function openItem(it, list) {
    if (!it) return; mList = list && list.length ? list : [it]; mIdx = Math.max(0, mList.indexOf(it)); showItem();
    $('#modal').classList.add('open'); $('#modal').setAttribute('aria-hidden', 'false'); document.body.style.overflow = 'hidden';
  }
  function closeModal() { $('#modal').classList.remove('open'); $('#modal').setAttribute('aria-hidden', 'true'); document.body.style.overflow = ''; }
  function row(k, v) { return v ? '<dt>' + t(k) + '</dt><dd>' + v + '</dd>' : ''; }
  function showItem() {
    var i = mList[mIdx]; if (!i) return;
    var img = $('#mImg'); img.src = 'img/t/' + i.id + '.jpg'; img.alt = i.t;
    var big = new Image(); big.onload = function () { if (mList[mIdx] === i) img.src = big.src; }; big.src = 'img/l/' + i.id + '.jpg';
    var place = i.p ? esc(placeName(i.p)) + ' <span class="desc">（' + t('b_' + i.pb) + (i.pe ? '：' + esc(i.pe) : '') + '）</span>' : '<span class="desc">' + t('unknown_place') + '</span>';
    $('#mInfo').innerHTML = '<div class="no">' + i.id + ' · ' + (mIdx + 1) + ' / ' + mList.length + '</div><h3>' + esc(i.t) + '</h3><dl>' +
      row('d_creator', esc(i.c)) + row('d_date', esc(i.d || (i.y ? String(i.y) : t('undated')))) + row('d_type', esc(nm(TYPE[i.ty]))) + row('d_stage', esc(stageLabel(i.st))) +
      row('d_medium', esc(i.m)) + row('d_place', place) + row('d_desc', i.ds ? '<span class="desc">' + esc(i.ds) + '</span>' : '') + row('d_subj', i.sj ? '<span class="desc">' + esc(i.sj) + '</span>' : '') +
      row('d_repo', esc(i.rp)) + row('d_call', esc(i.cn)) + row('d_rights', esc(i.lc)) + row('d_file', '<span class="desc">' + esc(i.f) + '</span>') + '</dl>' +
      '<div class="acts">' + (i.u ? '<a class="btn" target="_blank" rel="noopener" href="' + esc(i.u) + '">' + t('d_src') + '</a>' : '') +
      '<a class="btn ghost" target="_blank" rel="noopener" href="img/l/' + i.id + '.jpg">' + t('d_big') + '</a>' +
      (i.y ? '<button type="button" class="btn ghost" id="mTime">' + t('d_time') + '</button>' : '') + '</div>';
    $('#mInfo').scrollTop = 0;
    $('#mPrev').style.display = $('#mNext').style.display = mList.length > 1 ? '' : 'none';
    var tb = $('#mTime'); if (tb) tb.addEventListener('click', function () { closeModal(); stopPlay(); S.place = i.p || null; setRange(i.y, i.y, true); $('#atlas').scrollIntoView(); });
  }
  function initModal() {
    $('#modal').addEventListener('click', function (e) { if (e.target.getAttribute('data-close')) closeModal(); });
    $('#mPrev').addEventListener('click', function () { mIdx = (mIdx - 1 + mList.length) % mList.length; showItem(); });
    $('#mNext').addEventListener('click', function () { mIdx = (mIdx + 1) % mList.length; showItem(); });
    document.addEventListener('keydown', function (e) {
      if (!$('#modal').classList.contains('open')) return;
      if (e.key === 'Escape') closeModal(); else if (e.key === 'ArrowLeft') $('#mPrev').click(); else if (e.key === 'ArrowRight') $('#mNext').click();
    });
  }

  /* ------------------------------------------------------------ about + language */
  function renderAbout() {
    var cr = {}; ITEMS.forEach(function (i) { cr[i.s] = (cr[i.s] || 0) + 1; });
    $('#aboutSources').innerHTML = Object.keys(cr).sort(function (a, b) { return cr[b] - cr[a]; }).map(function (k) { return '<li>' + esc(SOURCES[k][LANG === 'zh' ? 0 : 1]) + ' — ' + cr[k] + '</li>'; }).join('');
    $('#aboutMaps').innerHTML = MAPS.map(function (m, x) { return '<li>' + ROMAN[x + 1] + ' · <a target="_blank" rel="noopener" href="' + m.url + '">' + m.year + ' — ' + esc(m.title) + '</a>（' + esc(m.maker) + '，' + esc(m.imprint) + '）</li>'; }).join('');
    var loc = ITEMS.filter(function (i) { return i.p; }).length, n = ITEMS.length, und = ITEMS.filter(function (i) { return !i.y; }).length;
    $('#aboutCoverage').textContent = LANG === 'zh'
      ? '当前共收 ' + n + ' 件图像，其中 ' + loc + ' 件（' + Math.round(loc / n * 100) + '%）能够确定出版地或所在地，其余 ' + (n - loc) + ' 件未计入热力图；另有 ' + und + ' 件年代不详，不出现在时间轴上，但都可以在检索库中找到。'
      : 'The archive holds ' + n + ' images. ' + loc + ' of them (' + Math.round(loc / n * 100) + '%) can be placed and so appear in the heat layer; the other ' + (n - loc) + ' cannot. ' + und + ' are undated and stay off the timeline, though all are in the Archive.';
    $('#colophon').textContent = t('colophon');
  }
  function applyLang() {
    document.documentElement.lang = LANG === 'zh' ? 'zh-CN' : 'en';
    document.body.classList.toggle('zh', LANG === 'zh'); document.body.classList.toggle('en', LANG !== 'zh');
    $$('[data-i18n]').forEach(function (el) { el.textContent = t(el.getAttribute('data-i18n')); });
    $('#langBtn').textContent = LANG === 'zh' ? 'EN' : '中文';
    renderHero(); renderStages(); buildFilterUI(); renderArchive(); renderAbout();
    baseKey0 = baseKey; if (map) { var m = mapFor(S.b); baseKey = null; if (baseLayer) { map.removeLayer(baseLayer); baseLayer = null; } updateAtlas(); }
    drawHisto();
  }
  var baseKey0 = null;
  $('#langBtn').addEventListener('click', function () { LANG = LANG === 'zh' ? 'en' : 'zh'; try { localStorage.setItem('columbia.lang', LANG); } catch (e) {} applyLang(); });
  $('#heroGallery').addEventListener('click', function (e) { var f = e.target.closest('figure[data-id]'); if (f) { e.stopPropagation(); openItem(BYID[f.getAttribute('data-id')], $$('#heroGallery figure').map(function (x) { return BYID[x.getAttribute('data-id')]; })); } });

  /* ------------------------------------------------------------ boot */
  initTimeline(); initMap(); initAtlasEvents(); initArchiveEvents(); initModal();
  applyLang();
  setRange(S.a, S.b);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(drawHisto);
})();
