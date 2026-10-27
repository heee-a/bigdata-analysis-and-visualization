#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成自包含动画 SVG（无需任何第三方库），作为“视频/动图演示”。
动画：2015->2024 林业产业总产值(绿) 与 木材产量(橙) 逐年绘制 + 行进标记点。
用法：python tools/make_demo.py  ->  assets/forest_demo.svg
"""
import os

years = list(range(2015, 2025))
output_value = [59363,64886,71267,76273,80751,81176,86764,90719,92800,101700]  # 亿元
timber       = [6832,6683,7682,8432,9028,8727,9888,10693,11944,13740]        # 万m³
timberImport = [7117,8025,9280,9633,9868,9348,9242,8124,6581,6284]           # 进口量 万m³
timberDependency = [51.02,54.56,54.71,53.32,52.22,51.72,48.31,43.17,35.52,31.38]  # 对外依存度 %

X0, X1 = 110, 892          # 绘图区左右
Y_TOP, Y_BOT = 80, 420     # 绘图区上下
W = X1 - X0
def x(i): return X0 + i * (W / (len(years)-1))

# 左轴：产值 [55000,105000]；右轴：木材 [6000,14000]
def y_ov(v): return Y_BOT - (v-55000)/(105000-55000)*(Y_BOT-Y_TOP)
def y_tk(v): return Y_BOT - (v-6000)/(14000-6000)*(Y_BOT-(Y_TOP+40))

def path(vals, yf):
    pts = [(x(i), yf(v)) for i,v in enumerate(vals)]
    d = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px,py in pts)
    return d, pts

d_ov, p_ov = path(output_value, y_ov)
d_tk, p_tk = path(timber, y_tk)

# 网格 + 左轴刻度
left_ticks = [55000,65000,75000,85000,95000,105000]
right_ticks = [6000,8000,10000,12000,14000]
grid = ""
for v in left_ticks:
    yy = y_ov(v)
    grid += f'<line x1="{X0}" y1="{yy:.1f}" x2="{X1}" y2="{yy:.1f}" stroke="rgba(120,160,220,.12)" stroke-width="1"/>'
    grid += f'<text x="{X0-8}" y="{yy+4:.1f}" fill="#9fb0cc" font-size="11" text-anchor="end">{v//1000}k</text>'
for v in right_ticks:
    yy = y_tk(v)
    grid += f'<text x="{X1+8}" y="{yy+4:.1f}" fill="#ff9f5a" font-size="11" text-anchor="start">{v//1000}k</text>'

# 年份刻度
xlabels = ""
for i,yr in enumerate(years):
    xx = x(i)
    xlabels += f'<text x="{xx:.1f}" y="{Y_BOT+22:.1f}" fill="#9fb0cc" font-size="11" text-anchor="middle">{yr}</text>'

# 数据点（序列出现）
def dots(pts, color):
    s=""
    for i,(px,py) in enumerate(pts):
        begin = 0.4 + i*0.78
        s += (f'<circle cx="{px:.1f}" cy="{py:.1f}" r="4" fill="{color}">'
              f'<animate attributeName="opacity" from="0" to="1" begin="{begin:.2f}s" dur="0.3s" fill="freeze"/>'
              f'<animate attributeName="r" values="3;6;4" begin="{begin:.2f}s" dur="0.5s" fill="freeze"/>'
              f'</circle>')
    return s

DUR = 8.0  # 绘制+行进时长
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 540" font-family="Segoe UI, PingFang SC, Microsoft YaHei, sans-serif">
  <defs>
    <linearGradient id="gO" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="rgba(46,230,160,.45)"/><stop offset="1" stop-color="rgba(46,230,160,0)"/>
    </linearGradient>
    <linearGradient id="gT" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="rgba(255,159,90,.35)"/><stop offset="1" stop-color="rgba(255,159,90,0)"/>
    </linearGradient>
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>

  <rect width="1000" height="540" fill="#0a0e1a"/>
  <text x="40" y="44" fill="#2ee6a0" font-size="24" font-weight="800">中国林业资源 · 十年增长动画演示</text>
  <text x="40" y="66" fill="#9fb0cc" font-size="13">2015 → 2024  林业产业总产值(绿) 与 木材产量(橙) 逐年绘制（循环播放）</text>

  {grid}
  <line x1="{X0}" y1="{Y_TOP}" x2="{X0}" y2="{Y_BOT}" stroke="rgba(120,160,220,.3)"/>
  <line x1="{X0}" y1="{Y_BOT}" x2="{X1}" y2="{Y_BOT}" stroke="rgba(120,160,220,.3)"/>
  <line x1="{X1}" y1="{Y_TOP}" x2="{X1}" y2="{Y_BOT}" stroke="rgba(120,160,220,.3)"/>
  {xlabels}
  <text x="{X0-40}" y="{Y_TOP-14}" fill="#2ee6a0" font-size="12">产值(亿元)</text>
  <text x="{X1+10}" y="{Y_TOP-14}" fill="#ff9f5a" font-size="12">木材(万m³)</text>

  <!-- 背景完整线（淡） -->
  <path d="{d_ov}" fill="none" stroke="rgba(46,230,160,.18)" stroke-width="2"/>
  <path d="{d_tk}" fill="none" stroke="rgba(255,159,90,.18)" stroke-width="2"/>

  <!-- 面积填充（动画裁剪） -->
  <clipPath id="clipO"><rect x="{X0}" y="{Y_TOP}" width="0" height="{Y_BOT-Y_TOP}">
     <animate attributeName="width" from="0" to="{W}" dur="{DUR}s" repeatCount="indefinite"/></rect></clipPath>
  <path d="{d_ov} L {X1} {Y_BOT} L {X0} {Y_BOT} Z" fill="url(#gO)" clip-path="url(#clipO)"/>

  <!-- 动画绘制线 -->
  <path d="{d_ov}" fill="none" stroke="#2ee6a0" stroke-width="3.5" pathLength="1000"
        stroke-dasharray="1000" stroke-dashoffset="1000" filter="url(#glow)">
    <animate attributeName="stroke-dashoffset" from="1000" to="0" dur="{DUR}s" repeatCount="indefinite"/>
  </path>
  <path d="{d_tk}" fill="none" stroke="#ff9f5a" stroke-width="3.5" pathLength="1000"
        stroke-dasharray="1000" stroke-dashoffset="1000" filter="url(#glow)">
    <animate attributeName="stroke-dashoffset" from="1000" to="0" dur="{DUR}s" repeatCount="indefinite"/>
  </path>

  <!-- 行进标记点 -->
  <circle r="6" fill="#2ee6a0" filter="url(#glow)"><animateMotion dur="{DUR}s" repeatCount="indefinite" path="{d_ov}"/></circle>
  <circle r="6" fill="#ff9f5a" filter="url(#glow)"><animateMotion dur="{DUR}s" repeatCount="indefinite" path="{d_tk}"/></circle>

  {dots(p_ov,"#2ee6a0")}
  {dots(p_tk,"#ff9f5a")}

  <!-- 图例 + 结论 -->
  <rect x="40" y="470" width="14" height="14" rx="3" fill="#2ee6a0"/><text x="62" y="482" fill="#e8eefb" font-size="13">林业产业总产值（亿元）</text>
  <rect x="300" y="470" width="14" height="14" rx="3" fill="#ff9f5a"/><text x="322" y="482" fill="#e8eefb" font-size="13">木材产量（万 m³）</text>
  <text x="40" y="512" fill="#9fb0cc" font-size="13">十年间林业产值由 5.94 万亿增至 10.17 万亿（+71%），木材产量由 6832 万 m³ 增至 13740 万 m³（+101%）。</text>
  <text x="40" y="532" fill="#ffd166" font-size="12">数据来源：国家统计局 / 国家林草局 / 中国林业信息网（详见仓库 README）。</text>
</svg>'''

out = os.path.join(os.path.dirname(__file__), "..", "assets", "forest_demo.svg")
out = os.path.abspath(out)
with open(out, "w", encoding="utf-8") as f:
    f.write(svg)
print("written:", out, "bytes:", len(svg))


# ---------------------------------------------------------------------------
# 第二个动画：木材供需与对外依存度（柱状 + 折线，clip 揭示 + 描边动画）
# ---------------------------------------------------------------------------
GREEN="#2ee6a0"; CYAN="#36d3ff"; ORANGE="#ff9f5a"; SUB="#9fb0cc"
DUR=8.0

def make_timber():
    Y_TOP, Y_BOT = 80, 420
    W = X1 - X0
    maxv = 16000
    def yv(v): return Y_BOT - (v/maxv)*(Y_BOT-Y_TOP)
    def y2(v): return Y_BOT - (v/60)*(Y_BOT-Y_TOP)
    bars = ""
    pts = []
    for i,(p,imp,d) in enumerate(zip(timber, timberImport, timberDependency)):
        gx = X0 + i*(W/9)
        yp = yv(p); bars += f'<rect x="{gx:.1f}" y="{yp:.1f}" width="30" height="{Y_BOT-yp:.1f}" fill="{GREEN}" rx="2"/>'
        yi = yv(imp); bars += f'<rect x="{gx+34:.1f}" y="{yi:.1f}" width="30" height="{Y_BOT-yi:.1f}" fill="{CYAN}" rx="2"/>'
        pts.append((gx+17, y2(d)))
    d_line = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x,y in pts)
    grid = ""
    for v in [0,4000,8000,12000,16000]:
        yy = yv(v)
        grid += f'<line x1="{X0}" y1="{yy:.1f}" x2="{X1}" y2="{yy:.1f}" stroke="rgba(120,160,220,.12)"/>'
        grid += f'<text x="{X0-8}" y="{yy+4:.1f}" fill="{SUB}" font-size="11" text-anchor="end">{v//1000}k</text>'
    for v in [0,20,40,60]:
        yy = y2(v)
        grid += f'<text x="{X1+8}" y="{yy+4:.1f}" fill="{ORANGE}" font-size="11" text-anchor="start">{v}%</text>'
    xlab = ""
    for i,yr in enumerate(years):
        xlab += f'<text x="{X0+i*(W/9)+17:.1f}" y="{Y_BOT+22:.1f}" fill="{SUB}" font-size="11" text-anchor="middle">{yr}</text>'
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 540" font-family="Segoe UI, PingFang SC, Microsoft YaHei, sans-serif">
  <defs>
    <linearGradient id="gL" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="rgba(255,159,90,.35)"/><stop offset="1" stop-color="rgba(255,159,90,0)"/></linearGradient>
    <filter id="glow2" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <clipPath id="clipT"><rect x="{X0}" y="{Y_TOP}" width="0" height="{Y_BOT-Y_TOP}"><animate attributeName="width" from="0" to="{W}" dur="{DUR}s" repeatCount="indefinite"/></rect></clipPath>
  </defs>
  <rect width="1000" height="540" fill="#0a0e1a"/>
  <text x="40" y="44" fill="#ff9f5a" font-size="24" font-weight="800">中国木材供需 · 对外依存度动画演示</text>
  <text x="40" y="66" fill="#9fb0cc" font-size="13">2015 → 2024  木材产量(绿)/进口量(青) 柱状 + 对外依存度(橙) 折线（循环播放）</text>
  {grid}
  <line x1="{X0}" y1="{Y_TOP}" x2="{X0}" y2="{Y_BOT}" stroke="rgba(120,160,220,.3)"/>
  <line x1="{X0}" y1="{Y_BOT}" x2="{X1}" y2="{Y_BOT}" stroke="rgba(120,160,220,.3)"/>
  <line x1="{X1}" y1="{Y_TOP}" x2="{X1}" y2="{Y_BOT}" stroke="rgba(120,160,220,.3)"/>
  {xlab}
  <text x="{X0-40}" y="{Y_TOP-14}" fill="#2ee6a0" font-size="12">产量/进口(万m³)</text>
  <text x="{X1+10}" y="{Y_TOP-14}" fill="#ff9f5a" font-size="12">依存度(%)</text>
  <g clip-path="url(#clipT)">{bars}
    <path d="{d_line} L {X1} {Y_BOT} L {X0} {Y_BOT} Z" fill="url(#gL)"/></g>
  <path d="{d_line}" fill="none" stroke="{ORANGE}" stroke-width="3.5" pathLength="1000" stroke-dasharray="1000" stroke-dashoffset="1000" filter="url(#glow2)">
    <animate attributeName="stroke-dashoffset" from="1000" to="0" dur="{DUR}s" repeatCount="indefinite"/></path>
  <circle r="6" fill="{ORANGE}" filter="url(#glow2)"><animateMotion dur="{DUR}s" repeatCount="indefinite" path="{d_line}"/></circle>
  <rect x="40" y="470" width="14" height="14" rx="3" fill="{GREEN}"/><text x="62" y="482" fill="#e8eefb" font-size="13">木材产量（万 m³）</text>
  <rect x="260" y="470" width="14" height="14" rx="3" fill="{CYAN}"/><text x="282" y="482" fill="#e8eefb" font-size="13">进口量（万 m³）</text>
  <rect x="480" y="470" width="14" height="14" rx="3" fill="{ORANGE}"/><text x="502" y="482" fill="#e8eefb" font-size="13">对外依存度（%）</text>
  <text x="40" y="512" fill="#9fb0cc" font-size="13">十年间木材产量翻倍增长，对外依存度由 51% 降至 31.4%，国内木材供给保障能力显著增强。</text>
  <text x="40" y="532" fill="#ffd166" font-size="12">数据来源：观研天下 2010–2024 全国木材市场（详见仓库 README）。</text>
</svg>'''
    out = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "forest_demo_timber.svg"))
    with open(out, "w", encoding="utf-8") as f:
        f.write(svg)
    print("written:", out, "bytes:", len(svg))

def make_region():
    """第三个动画：七大区域平均森林覆盖率（树木成长动画）。"""
    regions = ["华北","东北","华东","华中","华南","西南","西北","港澳台"]
    means   = [25.04, 41.5, 37.54, 37.81, 57.02, 38.42, 15.54, 38.59]
    X0, X1 = 110, 892
    YB, YT = 430, 90
    W = X1 - X0
    slot = W / len(regions)
    k = (YB - YT) / 62.0          # 覆盖率 60% 对应满高
    tree = "M0 0 L-3 0 L-3 -18 L3 -18 L3 0 Z M0 -100 L-20 -24 L20 -24 Z M0 -72 L-13 -32 L13 -32 Z"
    T = 7.0
    bars = ""
    for i,(name,val) in enumerate(zip(regions, means)):
        cx = X0 + slot*(i+0.5)
        H = val * k
        kt0 = i / len(regions)
        kt1 = kt0 + 0.1
        bars += (f'<g transform="translate({cx:.1f},{YB})">'
                 f'<path d="{tree}" fill="#2ee6a0" stroke="#19c37d" stroke-width="1" '
                 f'transform="scale(1,0)">'
                 f'<animateTransform attributeName="transform" type="scale" '
                 f'values="1 0;1 1;1 1" keyTimes="{kt0:.3f};{kt1:.3f};1" '
                 f'dur="{T}s" repeatCount="indefinite"/></path>'
                 f'<text x="0" y="20" fill="#9fb0cc" font-size="12" text-anchor="middle">{name}</text>'
                 f'<text x="0" y="-{H+10:.1f}" fill="#e8eefb" font-size="13" text-anchor="middle" '
                 f'opacity="0"><animate attributeName="opacity" values="0;0;1;1" '
                 f'keyTimes="{kt0:.3f};{kt1:.3f};{kt1+0.05:.3f};1" dur="{T}s" repeatCount="indefinite"/>'
                 f'{val}%</text>'
                 f'</g>')
    grid = f'<line x1="{X0}" y1="{YB}" x2="{X1}" y2="{YB}" stroke="rgba(120,160,220,.3)"/>'
    for v in [0,10,20,30,40,50,60]:
        yy = YB - v*k
        grid += f'<line x1="{X0}" y1="{yy:.1f}" x2="{X1}" y2="{yy:.1f}" stroke="rgba(120,160,220,.10)"/>'
        grid += f'<text x="{X0-8}" y="{yy+4:.1f}" fill="#9fb0cc" font-size="11" text-anchor="end">{v}%</text>'
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 540" font-family="Segoe UI, PingFang SC, Microsoft YaHei, sans-serif">
  <rect width="1000" height="540" fill="#0a0e1a"/>
  <text x="40" y="44" fill="#2ee6a0" font-size="24" font-weight="800">中国林业 · 七大区域森林覆盖率</text>
  <text x="40" y="66" fill="#9fb0cc" font-size="13">各区域平均覆盖率“树木成长”动画（循环播放）· 直观呈现“南高北低”格局</text>
  {grid}
  {bars}
  <text x="40" y="500" fill="#9fb0cc" font-size="13">华南（57.0%）最高，西北（15.5%）最低；南方集体林区整体远高于北方与西北。</text>
  <text x="40" y="522" fill="#ffd166" font-size="12">数据来源：第九次全国森林资源清查分省结果（详见仓库 README）。</text>
</svg>'''
    out = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "forest_demo_region.svg"))
    with open(out, "w", encoding="utf-8") as f:
        f.write(svg)
    print("written:", out, "bytes:", len(svg))

make_region()
make_timber()
