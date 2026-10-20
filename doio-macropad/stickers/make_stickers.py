#!/usr/bin/env python3
"""
Laser-cut stickers for the DOIO KB16: one round sticker for the big dial and three rounded-square
stickers for the keys, on 0.2 mm adhesive cardboard, xTool S1 40 W.

Icons are engraved (fill), outlines are cut (meant as a kiss cut: through the cardboard, not the liner).
Tune ENGRAVE / CUT from the test file, then regenerate.

  /Volumes/SSD2/venvs/keycap-stickers/bin/python make_stickers.py
    -> stickers.xcs        the four stickers
    -> sticker_test.xcs    cut and engrave power ladder, run this first
    -> preview.png         what the stickers look like

Format notes and builders follow ~/dev/diy/builds/business-cards/.../sml-card-laser/make_card_test.py.
"""
import json
import math
import time
import uuid

from shapely import affinity
from shapely.geometry import LineString, MultiPolygon, Point, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

# ----------------------------------------------------------------------------- CONFIG
DEVICE_POWER_W = 40
THICKNESS_MM = 0.2

GAP = 0.5                          # clearance to the edge of each top surface, per side
DIAL_TOP = 29.5                    # measured "just under 30"
KEY_TOP = 11.8                     # measured "just under 12"
KEY_RADIUS = 1.5                   # sticker corner radius
DIAL_D = DIAL_TOP - 2 * GAP        # 28.5
KEY_W = KEY_TOP - 2 * GAP          # 10.8
KEY_ICON = 8.4                     # icon box on a key sticker
DIAL_ICON = 18.0                   # sun on the dial sticker

ENGRAVE = dict(power=12, speed=300, density=150, scan="oneWay")   # placeholder until the test is read
CUT = dict(power=20, speed=200, repeat=1)                         # placeholder until the test is read

ORIGIN = (20.0, 20.0)              # top-left of the layout on the bed
PITCH_GAP = 3.0                    # between stickers

# test ladder
TEST_CUT_POWERS = [10, 15, 20, 25, 30]       # at CUT speed, 6 mm squares, left to right
TEST_ENGRAVE_POWERS = [8, 12, 16, 20]        # at ENGRAVE speed, 5 mm squares, left to right

COL_ENGRAVE, COL_CUT = "#ff6a00", "#0066ff"
# ----------------------------------------------------------------------------- /CONFIG


# ----------------------------------------------------------------------------- icons (unit box, y down)
def stroke(points, w):
    return LineString(points).buffer(w / 2, cap_style="round", join_style="round", quad_segs=8)


def arc(cx, cy, r, a0, a1, n=48):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def icon_sun():
    parts = [Point(0.5, 0.5).buffer(0.2, quad_segs=24)]
    for k in range(8):
        a = math.radians(k * 45)
        parts.append(stroke([(0.5 + 0.31 * math.cos(a), 0.5 + 0.31 * math.sin(a)),
                             (0.5 + 0.46 * math.cos(a), 0.5 + 0.46 * math.sin(a))], 0.085))
    return unary_union(parts)


def icon_floor_lamp():
    shade = Polygon([(0.34, 0.06), (0.62, 0.06), (0.74, 0.34), (0.22, 0.34)]).buffer(0.02, join_style="round")
    pole = stroke([(0.48, 0.34), (0.48, 0.86)], 0.075)
    base = stroke([(0.30, 0.90), (0.66, 0.90)], 0.08)
    rays = [stroke([(0.25, 0.44), (0.16, 0.56)], 0.06),
            stroke([(0.71, 0.44), (0.80, 0.56)], 0.06)]
    return unary_union([shade, pole, base] + rays)


def icon_mic():
    capsule = stroke([(0.5, 0.17), (0.5, 0.43)], 0.26)
    holder = stroke(arc(0.5, 0.40, 0.25, 0, 180), 0.07)
    stem = stroke([(0.5, 0.65), (0.5, 0.86)], 0.07)
    base = stroke([(0.33, 0.90), (0.67, 0.90)], 0.07)
    return unary_union([capsule, holder, stem, base])


def icon_laser():
    head = box(0.25, 0.04, 0.75, 0.32).buffer(0.03, join_style="round")
    nozzle = Polygon([(0.40, 0.33), (0.60, 0.33), (0.545, 0.46), (0.455, 0.46)])
    beam = stroke([(0.5, 0.50), (0.5, 0.76)], 0.05)
    surface = stroke([(0.10, 0.92), (0.90, 0.92)], 0.06)
    sparks = [stroke([(0.5 + 0.07 * math.cos(math.radians(a)), 0.84 + 0.07 * math.sin(math.radians(a))),
                      (0.5 + 0.15 * math.cos(math.radians(a)), 0.84 + 0.15 * math.sin(math.radians(a)))], 0.045)
              for a in (-165, -130, -50, -15)]
    return unary_union([head, nozzle, beam, surface] + sparks)


def place(geom, size, cx, cy):
    """Unit-box icon -> size x size mm, centred on (cx, cy)."""
    g = affinity.scale(geom, size, size, origin=(0, 0))
    return affinity.translate(g, cx - size / 2, cy - size / 2)


# ----------------------------------------------------------------------------- xcs builders
def uid():
    return str(uuid.uuid4())


def polys(geom):
    return list(geom.geoms) if isinstance(geom, MultiPolygon) else [geom]


def to_d(geom):
    """Polygon(s) -> SVG path; exterior and holes wound oppositely so nonzero fill keeps the holes."""
    out = []
    for p in polys(geom):
        p = orient(p, 1.0)
        for ring in [p.exterior] + list(p.interiors):
            c = list(ring.coords)[:-1]
            out.append("M%.4f %.4f" % c[0] + "".join("L%.4f %.4f" % xy for xy in c[1:]) + "Z")
    return "".join(out)


def path_display(geom, color, is_fill, name):
    x0, y0, x1, y1 = geom.bounds
    w, h = round(x1 - x0, 4), round(y1 - y0, 4)
    return {
        "id": uid(), "name": name, "type": "PATH", "x": round(x0, 4), "y": round(y0, 4), "angle": 0,
        "scale": {"x": 1, "y": 1}, "skew": {"x": 0, "y": 0}, "pivot": {"x": 0, "y": 0},
        "localSkew": {"x": 0, "y": 0}, "offsetX": round(x0, 4), "offsetY": round(y0, 4),
        "lockRatio": False, "isClosePath": True, "isCompoundPath": True, "zOrder": 1,
        "groupTags": [], "groupTag": uid(), "layerTag": color, "layerColor": color,
        "visible": True, "originColor": "#000000", "enableTransform": True,
        "visibleState": True, "lockState": False, "resourceOrigin": "",
        "customData": {"tabBreaks": {}, "startPoint": {}},
        "rootComponentId": "", "minCanvasVersion": "0.0.0", "alpha": 1,
        "fill": {"paintType": "color", "visible": is_fill, "color": 0, "alpha": 1},
        "stroke": {"paintType": "color", "visible": True, "color": 0, "alpha": 1,
                   "width": 1, "cap": "butt", "join": "miter", "miterLimit": 4, "alignment": 0.5},
        "effects": [], "width": w, "height": h, "isFill": is_fill,
        "lineColor": 0, "fillColor": "#000000",
        "dPath": to_d(geom), "graphicX": 0.0, "graphicY": 0.0,
        "fillRule": "nonzero", "points": [],
    }


def base(power, speed, repeat):
    return {"processingLightSource": "blue", "power": power, "speed": speed, "repeat": repeat,
            "pulseWidth": 200, "mopaFrequency": 65}


def entry_engrave(d, power, speed, density, scan):
    data = {"FILL_VECTOR_ENGRAVING": {"materialType": "customize", "planType": "blue",
                                      "parameter": {"customize": {
                                          "bitmapEngraveMode": "normal", "speed": speed,
                                          "density": density, "needGapNumDensity": True,
                                          "dotDuration": 100, "dpi": int(round(density * 2.54)),
                                          "processingLightSource": "blue", "power": power,
                                          "repeat": 1, "bitmapScanMode": scan,
                                          "pulseWidth": 200, "mopaFrequency": 65,
                                          "scanAngle": 90, "angleType": 1, "crossAngle": False,
                                          "enableDelayPerLine": False, "delayPerLine": 0.3,
                                          "outlineTrace": False, "enableKerf": False, "kerfDistance": 0}}}}
    return [d["id"], {"isFill": True, "type": "PATH", "processingType": "FILL_VECTOR_ENGRAVING",
                      "data": data, "processIgnore": False, "isWhiteModel": True}]


def entry_cut(d, power, speed, repeat):
    data = {"VECTOR_CUTTING": {"materialType": "customize", "planType": "blue",
                               "parameter": {"customize": {
                                   **base(power, speed, repeat),
                                   "cuttingDrop": False, "sinkingMethod": "one",
                                   "firstCuttingDropValue": 0.01, "cuttingDropValue": 0.01,
                                   "descentIntervalDescent": 1, "descentPerStep": 0.01,
                                   "enableKerf": False, "kerfDistance": 0,
                                   "enableBreakPoint": False, "breakPointGenMode": "auto",
                                   "breakPointSize": 0.5, "breakPointCount": 2, "breakPointMode": "count",
                                   "breakPointDistance": 100, "breakPointPower": 0,
                                   "wobbleEnable": False, "wobbleDiameter": 0.05, "wobbleSpacing": 0.015}}}}
    return [d["id"], {"isFill": False, "type": "PATH", "processingType": "VECTOR_CUTTING",
                      "data": data, "processIgnore": False, "isWhiteModel": True}]


def write_xcs(path, displays, entries, layers):
    canvas_id = uid()
    now = int(time.time() * 1000)
    doc = {
        "canvasId": canvas_id,
        "canvas": [{"id": canvas_id, "title": "{panel}1",
                    "layerData": {c: {"name": n, "order": i, "visible": True} for i, (c, n) in enumerate(layers, 1)},
                    "groupData": {}, "displays": displays,
                    "extendInfo": {"version": "2.15.108", "minCanvasVersion": "0.0.0",
                                   "displayProcessConfigMap": {}, "rulerPluginData": {"rulerGuide": []},
                                   "type": "2d", "gridOptions": {"color": "normal", "isShow": True}}}],
        "extId": "S1", "extName": "S1",
        "device": {"id": "S1", "power": DEVICE_POWER_W,
                   "data": {"dataType": "Map", "value": [[canvas_id, {
                       "mode": "LASER_PLANE",
                       "data": {"LASER_PLANE": {"material": 0, "lightSourceMode": "blue",
                                                "thickness": THICKNESS_MM, "isProcessByLayer": True,
                                                "pathPlanning": "auto", "fillPlanning": "separate",
                                                "dreedyTsp": False, "avoidSmokeModal": False,
                                                "scanDirection": "topToBottom", "enableOddEvenKerf": True,
                                                "xcsUsed": []}},
                       "displays": {"dataType": "Map", "value": entries}}]]},
                   "materialList": [], "materialTypeList": [], "customProjectData": {}},
        "version": "1.6.6", "created": now, "modify": now, "ua": "kb16-sticker-generator/1.0",
        "meta": [],
        "cover": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAC0lEQVQIHWNgAAIABQABNjN9GQAAAABJRUeErkJggg==",
        "minRequiredVersion": "2.6.0", "appMinRequiredVersion": "", "webMinRequiredVersion": "",
        "projectTraceID": uid(),
    }
    with open(path, "w") as f:
        json.dump(doc, f, separators=(",", ":"))
    print("wrote %s: %d objects" % (path, len(displays)))


# ----------------------------------------------------------------------------- layout
def rounded_square(cx, cy, w, r):
    return box(cx - w / 2 + r, cy - w / 2 + r, cx + w / 2 - r, cy + w / 2 - r).buffer(r, quad_segs=16)


def stickers():
    """[(name, outline, art)] in bed coordinates."""
    out = []
    ox, oy = ORIGIN
    cx, cy = ox + DIAL_D / 2, oy + DIAL_D / 2
    dial_art = place(icon_sun(), DIAL_ICON, cx, cy)   # rotation-symmetric: the sticker turns with the knob
    out.append(("dial: brightness", Point(cx, cy).buffer(DIAL_D / 2, quad_segs=64), dial_art))
    x = ox + DIAL_D + PITCH_GAP
    for name, icon in [("top-right: corner light", icon_floor_lamp()),
                       ("bottom-left: dictation", icon_mic()),
                       ("bottom-right: laser", icon_laser())]:
        kx, ky = x + KEY_W / 2, cy
        out.append((name, rounded_square(kx, ky, KEY_W, KEY_RADIUS), place(icon, KEY_ICON, kx, ky)))
        x += KEY_W + PITCH_GAP
    for name, outline, art in out:
        assert outline.buffer(-0.6).contains(art), "%s: art closer than 0.6 mm to the cut" % name
    return out


def build_stickers():
    displays, entries = [], []
    for name, outline, art in stickers():
        d = path_display(art, COL_ENGRAVE, True, name + " (engrave)")
        displays.append(d); entries.append(entry_engrave(d, **ENGRAVE))
        c = path_display(outline, COL_CUT, False, name + " (cut)")
        displays.append(c); entries.append(entry_cut(c, CUT["power"], CUT["speed"], CUT["repeat"]))
    write_xcs("stickers.xcs", displays, entries, [(COL_ENGRAVE, "engrave icons"), (COL_CUT, "cut outlines")])


def build_test():
    """Row 1: 6 mm cut squares at TEST_CUT_POWERS. Row 2: 5 mm engraved squares at TEST_ENGRAVE_POWERS."""
    displays, entries = [], []
    ox, oy = ORIGIN
    for i, p in enumerate(TEST_CUT_POWERS):
        sq = box(ox + i * 8.0, oy, ox + i * 8.0 + 6.0, oy + 6.0)
        c = path_display(sq, COL_CUT, False, "cut P%d S%d" % (p, CUT["speed"]))
        displays.append(c); entries.append(entry_cut(c, p, CUT["speed"], 1))
    for i, p in enumerate(TEST_ENGRAVE_POWERS):
        sq = box(ox + i * 8.0, oy + 9.0, ox + i * 8.0 + 5.0, oy + 14.0)
        d = path_display(sq, COL_ENGRAVE, True, "engrave P%d S%d" % (p, ENGRAVE["speed"]))
        displays.append(d); entries.append(entry_engrave(d, p, ENGRAVE["speed"], ENGRAVE["density"], ENGRAVE["scan"]))
    write_xcs("sticker_test.xcs", displays, entries, [(COL_ENGRAVE, "engrave ladder"), (COL_CUT, "cut ladder")])


def preview():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import PathPatch
    from matplotlib.path import Path

    def patch(geom, **kw):
        verts, codes = [], []
        for p in polys(geom):
            for ring in [p.exterior] + list(p.interiors):
                c = list(ring.coords)
                verts += c; codes += [Path.MOVETO] + [Path.LINETO] * (len(c) - 2) + [Path.CLOSEPOLY]
        return PathPatch(Path(verts, codes), **kw)

    fig, ax = plt.subplots(figsize=(10, 4), dpi=200)
    for name, outline, art in stickers():
        ax.add_patch(patch(outline, facecolor="#e8d9b5", edgecolor="#0066ff", lw=0.8))
        ax.add_patch(patch(art, facecolor="#3a2a1a", edgecolor="none"))
    ax.set_xlim(ORIGIN[0] - 2, ORIGIN[0] + DIAL_D + 3 * (KEY_W + PITCH_GAP) + 1)
    ax.set_ylim(ORIGIN[1] + DIAL_D + 2, ORIGIN[1] - 2)
    ax.set_aspect("equal"); ax.axis("off")
    fig.savefig("preview.png", bbox_inches="tight", facecolor="white")
    print("wrote preview.png")


if __name__ == "__main__":
    build_stickers()
    build_test()
    preview()
