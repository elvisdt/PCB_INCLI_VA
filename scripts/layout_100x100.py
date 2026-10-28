#!/usr/bin/python3
"""Build the review-only 100 mm proposal from the saved 120 x 80 mm board.

Historical: the 120 x 80 mm inputs were removed on 2026-10-28 (user decision).
To rerun, restore them with `git checkout aa0a41b -- docs/layout/INCLI-VA-120x80.*
docs/layout/posiciones-120x80.json`. The saved 100 x 100 board no longer needs it.

Uses KiCad's pcbnew API; never writes the main board. Run from project root.
Coordinates in the placement JSON are relative to (100, 50) mm in KiCad.
"""
import json
import math
import gc
from pathlib import Path
import shutil

# Retain SWIG wrapper lifetimes throughout this short-lived batch process.
gc.disable()
import pcbnew as pcb

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/layout'
STEM = 'INCLI-VA-100x100'
old = json.loads((OUT / 'posiciones-120x80.json').read_text())
board = pcb.LoadBoard(str(OUT / 'INCLI-VA-120x80.kicad_pcb'))
fps = {f.GetReference(): f for f in board.GetFootprints()}
removed_h5 = fps.pop('H5')
board.Remove(removed_h5)
groups = {r: g for r, g in old['groups'].items() if r != 'H5'}
positions = {r: list(v) for r, v in old['positions'].items() if r != 'H5'}

def shift(group, dx, dy):
    for ref, pos in positions.items():
        if groups[ref] == group:
            pos[0] += dx
            pos[1] += dy

shift('2', -28, 30)
shift('3', -27, 35)
shift('6', -1, 5)
shift('5', -11, 17)
# Identical output channels get the same relative placement, side by side.
for ref in list(positions):
    if groups[ref] == 'DO2':
        source = ref.rstrip('0123456789') + str(int(''.join(filter(str.isdigit, ref))) - 50)
        x, y, a = positions[source]
        positions[ref] = [x + 22, y, a]

positions.update({
    'H1': [5, 5, 0], 'H2': [95, 5, 0], 'H3': [5, 95, 0],
    'H4': [87, 95, 0],
    'U401': [84.94, 70.25, -90],
    'U503': [50, 50, 0], 'C507': [56, 50, 90], 'R503': [43.5, 50, 0],
    'J401': [75, 94.5, 0], 'U402': [66.5, 97, 0],
    'J402': [43.5, 94, 90], 'SW401': [81, 5, 0], 'SW402': [86, 39, 0],
    'C401': [84, 56, 0], 'C402': [89, 56, 0], 'C403': [79, 56, 0],
    'R401': [74, 56, 0], 'R402': [74, 82, 0],
    'R403': [84, 52, 0], 'R404': [74, 58.5, 0],
    'TP401': [79, 82, 0], 'TP402': [83, 82, 0], 'TP403': [87, 82, 0],
    'TP404': [75, 86, 0], 'TP405': [79, 86, 0],
    'U801': [86, 86, 0], 'C801': [81, 86, 0],
    'R801': [89, 53, 90], 'R802': [85.5, 89.5, 0],
    'D801': [77, 50, 0], 'D802': [82, 50, 0],
    'R803': [77, 53, 0], 'R804': [82, 53, 0],
    'R805': [86, 47, 0], 'R806': [86, 50, 0], 'R807': [89, 53, 90],
    'U501': [63, 49, 0], 'C501': [65, 55.5, 0], 'C502': [60, 55.5, 0],
    'C503': [60, 42, 0], 'C504': [65, 42, 0], 'R501': [70, 52.5, 0],
    'U502': [76, 42, 0], 'C505': [76, 38, 0], 'C506': [80.5, 42, 0],
    'C508': [75, 46.5, 0], 'R502': [70.5, 44, 0],
    'TP501': [60, 59, 0], 'TP502': [64, 59, 0], 'TP503': [68, 59, 0],
    'TP504': [80, 46.5, 0],
})

def vector(x, y):
    return pcb.VECTOR2I(pcb.FromMM(x), pcb.FromMM(y))

def setpos(ref, value):
    x, y, a = value
    f = fps[ref]
    f.SetOrientationDegrees(a)
    f.SetPosition(vector(x + 100, y + 50))

def item_box(item):
    b = item.GetBoundingBox()
    return [pcb.ToMM(b.GetX()) - 100, pcb.ToMM(b.GetY()) - 50,
            pcb.ToMM(b.GetRight()) - 100, pcb.ToMM(b.GetBottom()) - 50]

def envelope(ref):
    f = fps[ref]
    if ref == 'U401':
        # The official courtyard includes a 48 x 21 mm RF reserve. Separate
        # the module body from that reserve rather than using their convex hull.
        x, y, _ = positions[ref]
        return [x-13.47, y-9.78, x+6.75, y+9.78]
    parts = [item_box(p) for p in f.Pads()]
    parts += [item_box(g) for g in f.GraphicalItems()
              if g.GetLayer() in (pcb.F_CrtYd, pcb.B_CrtYd)]
    return [min(p[0] for p in parts), min(p[1] for p in parts),
            max(p[2] for p in parts), max(p[3] for p in parts)]

for ref, value in positions.items():
    setpos(ref, value)

def gap(a, b):
    dx = max(b[0]-a[2], a[0]-b[2], 0)
    dy = max(b[1]-a[3], a[1]-b[3], 0)
    return math.hypot(dx, dy)

rf = [91.69, 46.25, 112.69, 94.25]
notch = [92, 53, 100, 88]
boxes = {r: envelope(r) for r in fps}

def fits(box, ref, placed):
    if min(box[:2]) < 0.8 or max(box[2:]) > 99.2:
        return False
    if ref != 'U401' and gap(box, rf) < 1.01:
        return False
    if ref != 'U401' and gap(box, notch) < 0.8:
        return False
    # Four radius-4 corners; require the bounding-box corners inside FR4.
    for x in (box[0], box[2]):
        for y in (box[1], box[3]):
            cx, cy = min(max(x, 4), 96), min(max(y, 4), 96)
            if math.hypot(x-cx, y-cy) > 3.9:
                return False
    return all(gap(box, b) >= 1.0099 for r, b in placed.items() if r != ref)

# Preserve the mechanically significant anchors and the existing input/CAN
# arrangements. Resolve conflicts among remaining parts near their target.
fixed = ['U401', 'U503', 'H1', 'H2', 'H3', 'H4', 'J1', 'J2', 'J401']
fixed += [r for r in fps if groups[r] in ('1', '6', '5') and r not in fixed]
placed = {}
for r in fixed:
    if not fits(boxes[r], r, placed):
        raise RuntimeError(f'Fixed component does not fit: {r}')
    placed[r] = boxes[r]

regions = {
    '2': [13, 77, 40, 99], '3': [40, 63, 65, 91],
    'DO1': [54, 12, 76, 37], 'DO2': [76, 12, 99, 37],
    '5': [42, 37, 88, 61], '4': [60, 1, 92, 99], '8': [58, 38, 91, 91],
}
remaining = [r for r in fps if r not in placed]
remaining.sort(key=lambda r: (-(boxes[r][2]-boxes[r][0])*(boxes[r][3]-boxes[r][1]), r))
adjusted = []
for ref in remaining:
    box = boxes[ref]
    if not fits(box, ref, placed):
        x, y, a = positions[ref]
        reg = regions[groups[ref]]
        candidates = []
        for ix in range(math.ceil(reg[0]*4), math.floor(reg[2]*4)+1):
            for iy in range(math.ceil(reg[1]*4), math.floor(reg[3]*4)+1):
                nx, ny = ix/4, iy/4
                dx, dy = nx-x, ny-y
                candidates.append((dx*dx+dy*dy, dx, dy))
        candidates.sort()
        for _, dx, dy in candidates:
            candidate = [box[0]+dx, box[1]+dy, box[2]+dx, box[3]+dy]
            if fits(candidate, ref, placed):
                positions[ref] = [x+dx, y+dy, a]
                setpos(ref, positions[ref])
                box = envelope(ref)
                adjusted.append(ref)
                break
        else:
            raise RuntimeError(f'No position for {ref}')
    placed[ref] = box

# Rebuild the outline, retaining the established 8 x 35 mm antenna notch and
# radius-4 corners. Footprint-contained antenna keep-out moves with U401.
removed_drawings = list(board.GetDrawings())
for d in removed_drawings:
    if d.GetLayer() == pcb.Edge_Cuts:
        board.Remove(d)

def line(a, b):
    s = pcb.PCB_SHAPE(board)
    s.SetShape(pcb.SHAPE_T_SEGMENT)
    s.SetStart(vector(a[0]+100, a[1]+50))
    s.SetEnd(vector(b[0]+100, b[1]+50))
    s.SetLayer(pcb.Edge_Cuts)
    s.SetWidth(pcb.FromMM(0.1))
    board.Add(s)

def arc(a, mid, b):
    s = pcb.PCB_SHAPE(board)
    s.SetShape(pcb.SHAPE_T_ARC)
    s.SetArcGeometry(vector(a[0]+100,a[1]+50), vector(mid[0]+100,mid[1]+50), vector(b[0]+100,b[1]+50))
    s.SetLayer(pcb.Edge_Cuts)
    s.SetWidth(pcb.FromMM(0.1))
    board.Add(s)

d = 4-4/math.sqrt(2)
line((4,0),(96,0)); arc((96,0),(100-d,d),(100,4))
line((100,4),(100,53)); line((100,53),(92,53)); line((92,53),(92,88))
line((92,88),(100,88)); line((100,88),(100,96))
arc((100,96),(100-d,100-d),(96,100)); line((96,100),(4,100))
arc((4,100),(d,100-d),(0,96)); line((0,96),(0,4)); arc((0,4),(d,d),(4,0))

for ref, f in fps.items():
    if ref.startswith('TP') and f.GetLayer() != pcb.B_Cu:
        f.Flip(f.GetPosition(), pcb.FLIP_DIRECTION_LEFT_RIGHT)
    positions[ref][2] = f.GetOrientationDegrees()
    b = placed[ref]
    label = f.Reference()
    if not hasattr(label, 'SetLayer'):
        field = pcb.PCB_FIELD.__new__(pcb.PCB_FIELD)
        field.this = label
        label = field
    label.SetLayer(pcb.B_SilkS if ref.startswith('TP') else pcb.F_Fab)
    label.SetVisible(True)
    label.SetMirrored(ref.startswith('TP'))
    label.SetTextAngle(pcb.EDA_ANGLE(0, pcb.DEGREES_T))
    label.SetTextSize(vector(0.7, 0.7))
    label.SetTextThickness(pcb.FromMM(0.12))
    label.SetPosition(vector(100+(b[0]+b[2])/2, 50+b[1]-0.6))
    value = f.Value()
    if not hasattr(value, 'SetVisible'):
        field = pcb.PCB_FIELD.__new__(pcb.PCB_FIELD)
        field.this = value
        value = field
    value.SetVisible(False)

# Readable bottom-side TP identifiers. Keep ink clear of bottom pads, existing
# silkscreen and earlier TP identifiers; use the native DRC as final authority.
obstacles = []
for f in fps.values():
    obstacles += [item_box(p) for p in f.Pads() if p.IsOnLayer(pcb.B_Cu)]
    obstacles += [item_box(g) for g in f.GraphicalItems() if g.GetLayer() == pcb.B_SilkS]
for ref in sorted(r for r in fps if r.startswith('TP')):
    f = fps[ref]
    label = f.Reference()
    if not hasattr(label, 'SetLayer'):
        field = pcb.PCB_FIELD.__new__(pcb.PCB_FIELD)
        field.this = label
        label = field
    label.SetTextSize(vector(1,1))
    label.SetTextThickness(pcb.FromMM(0.15))
    x,y,_ = positions[ref]
    candidates = [(dx*dx+dy*dy,dx,dy) for dy in (-2,2,-2.5,2.5,-3,3,-4,4)
                  for dx in (0,-1,1,-2,2,-3,3)]
    for _,dx,dy in sorted(candidates):
        label.SetPosition(vector(100+x+dx,50+y+dy))
        lb = item_box(label)
        if (min(lb[:2]) >= .5 and max(lb[2:]) <= 99.5
                and gap(lb, notch) >= .3 and gap(lb,rf) >= .3
                and all(gap(lb,ob) >= .2 for ob in obstacles)):
            obstacles.append(lb)
            break
    else:
        raise RuntimeError(f'No clear bottom identifier position for {ref}')

pcb.SaveBoard(str(OUT / (STEM + '.kicad_pcb')), board)
for ext in ('.kicad_pro', '.kicad_dru'):
    shutil.copyfile(ROOT / ('INCLI-VA'+ext), OUT / (STEM+ext))

pairs = [(gap(a,b), r,s) for r,a in placed.items() for s,b in placed.items() if r<s]
minimum = min(pairs)
data = {'positions': positions, 'boxes': placed, 'groups': groups,
        'layers': {r:f.GetLayerName() for r,f in fps.items()},
        'origin_mm': [100,50], 'size_mm': [100,100], 'rf_keepout': rf,
        'notch': notch, 'minimum_envelope_gap_mm': minimum[0],
        'minimum_pair': list(minimum[1:]), 'adjusted_from_targets': adjusted}
(OUT/'posiciones-100x100.json').write_text(json.dumps(data,indent=2)+'\n')
print(json.dumps({'footprints':len(fps), 'min_gap_mm':minimum, 'adjusted':adjusted},indent=2))
