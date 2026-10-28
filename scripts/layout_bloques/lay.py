"""Herramientas de reubicacion INCLI-VA: place / check / metrics / render.
Coordenadas locales: (0,0) = esquina superior izquierda del contorno = (100,50) mm en KiCad."""
import pcbnew, sys, json, math, itertools
OX, OY = 100.0, 50.0
mm, FMM = pcbnew.ToMM, pcbnew.FromMM

def load(p):
    return pcbnew.LoadBoard(p)

def loc(pt):
    return (mm(pt.x) - OX, mm(pt.y) - OY)

def short(n):
    return n.split('/')[-1]

# ------------------------------------------------------------------ place
def place(b, plan):
    for ref, v in plan.items():
        f = b.FindFootprintByReference(ref)
        if f is None:
            raise SystemExit('falta ' + ref)
        x, y, rot = v[0], v[1], v[2]
        f.SetOrientationDegrees(rot)
        f.SetPosition(pcbnew.VECTOR2I(FMM(x + OX), FMM(y + OY)))

# ------------------------------------------------------------------ geometry
def court(f):
    c = f.GetCourtyard(f.GetLayer())
    if c.OutlineCount():
        return c
    s = pcbnew.SHAPE_POLY_SET()
    bb = f.GetBoundingBox(False)
    s.NewOutline()
    for x, y in ((bb.GetLeft(), bb.GetTop()), (bb.GetRight(), bb.GetTop()), (bb.GetRight(), bb.GetBottom()), (bb.GetLeft(), bb.GetBottom())):
        s.Append(x, y)
    return s

def poly_dist(a, b):
    if a.Collide(b, 0):
        return -1.0
    d = 1e18
    for i in range(a.OutlineCount()):
        oa = a.Outline(i)
        for j in range(b.OutlineCount()):
            ob = b.Outline(j)
            d = min(d, min(oa.SquaredDistance(ob.CPoint(k)) for k in range(ob.PointCount())))
            d = min(d, min(ob.SquaredDistance(oa.CPoint(k)) for k in range(oa.PointCount())))
    return mm(int(math.sqrt(d)))

def board_poly(b):
    s = pcbnew.SHAPE_POLY_SET()
    b.GetBoardPolygonOutlines(s, True)
    return s

ISO = {'GND_CAN', 'BUS_CAN_H', 'BUS_CAN_L', 'V_SOIN', 'V_SOOUT', 'GNDISO_CAN', 'CAN_RS', 'Net-(C609-Pad1)'}

def check(b, gap=1.0):
    fps = list(b.GetFootprints())
    cs = {f.GetReference(): court(f) for f in fps}
    out = []
    for f, g in itertools.combinations(fps, 2):
        if f.GetLayer() != g.GetLayer():
            continue
        a, c = cs[f.GetReference()], cs[g.GetReference()]
        ba, bc = a.BBox(), c.BBox()
        m = FMM(gap + 0.01)
        if ba.GetRight() + m < bc.GetLeft() or bc.GetRight() + m < ba.GetLeft() or ba.GetBottom() + m < bc.GetTop() or bc.GetBottom() + m < ba.GetTop():
            continue
        d = poly_dist(a, c)
        if d < gap:
            out.append(('courtyard', f.GetReference(), g.GetReference(), round(d, 2)))
    # dentro del contorno (courtyard), salvo conectores de borde
    bp = board_poly(b)
    for f in fps:
        r = f.GetReference()
        if r in ('J401', 'U401'):
            continue
        c = cs[r]
        for i in range(c.OutlineCount()):
            o = c.Outline(i)
            for k in range(o.PointCount()):
                p = o.CPoint(k)
                if not bp.Contains(p):
                    out.append(('fuera_contorno', r, '', [round(v, 1) for v in loc(p)]))
                    break
            else:
                continue
            break
    # keep-out de antena
    u = b.FindFootprintByReference('U401')
    ko = [z for z in u.Zones()][0].Outline()
    for f in fps:
        if f.GetReference() == 'U401':
            continue
        if cs[f.GetReference()].Collide(ko, 0) and f.GetLayer() == pcbnew.F_Cu:
            out.append(('keepout_antena', f.GetReference(), '', ''))
    # zonas de regla (barrera) contra pads ajenos
    for z in b.Zones():
        if not z.GetIsRuleArea():
            continue
        for f in fps:
            if f.GetReference() == 'U601':
                continue
            for p in f.Pads():
                if z.Outline().Collide(p.GetEffectivePolygon(pcbnew.F_Cu), 0):
                    out.append(('pad_en_barrera', f.GetReference(), p.GetNumber(), z.GetZoneName()))
    return out

# ------------------------------------------------------------------ metrics
def pads_of(b, net):
    return [p for p in b.GetPads() if short(p.GetNetname()) == net]

def mst_len(pts):
    if len(pts) < 2:
        return 0.0
    inside = [pts[0]]
    rest = pts[1:]
    tot = 0.0
    while rest:
        best = None
        for i, q in enumerate(rest):
            d = min(math.dist(q, p) for p in inside)
            if best is None or d < best[0]:
                best = (d, i)
        tot += best[0]
        inside.append(rest.pop(best[1]))
    return tot

def net_len(b, net):
    pts = []
    seen = set()
    for p in pads_of(b, net):
        key = (p.GetParentFootprint().GetReference(), round(mm(p.GetPosition().x), 1), round(mm(p.GetPosition().y), 1))
        if key in seen:
            continue
        seen.add(key)
        pts.append(loc(p.GetPosition()))
    # pads de una misma huella cuentan como un solo nodo (EP, VBUS doble, etc.)
    byfp = {}
    for p in pads_of(b, net):
        byfp.setdefault(p.GetParentFootprint().GetReference(), []).append(loc(p.GetPosition()))
    nodes = [v[0] for v in byfp.values()]
    return round(mst_len(nodes), 1), len(byfp)

def pad_gap(p, q):
    a = p.GetEffectivePolygon(pcbnew.F_Cu if p.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu)
    c = q.GetEffectivePolygon(pcbnew.F_Cu if q.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu)
    return max(0.0, poly_dist(a, c))

def decap(b, ic, cap, pins=None):
    u = b.FindFootprintByReference(ic)
    c = b.FindFootprintByReference(cap)
    if u is None or c is None:
        return None
    res = {}
    for cp in c.Pads():
        n = short(cp.GetNetname())
        for p in u.Pads():
            if p.GetNetCode() != cp.GetNetCode() or p.GetNetCode() <= 0:
                continue
            if pins and p.GetNumber() not in pins and not n.startswith('GND'):
                continue
            d = pad_gap(cp, p)
            if n not in res or d < res[n][0]:
                res[n] = (round(d, 2), p.GetNumber())
    return res

CRIT = ['ILIM', 'SW', '+VPROT', 'BUCK_SW', 'MCU_RST_N', 'BUS_CAN_H', 'BUS_CAN_L', 'USB_D+', 'USB_D-']
DEC = [  # (ic, pieza, pines de interes o None)
    ('U101', 'R106', ['3']), ('U101', 'R110', ['11']), ('U101', 'R107', ['4']), ('U101', 'R109', ['5']),
    ('U101', 'C102', ['6', '7', '22']), ('U101', 'C103', ['18', '24']), ('U101', 'C108', ['23']), ('U101', 'C110', ['9']),
    ('U101', 'C104', ['19']), ('U101', 'R104', ['20']), ('L101', 'C107', None), ('L101', 'C106', None),
    ('U201', 'C202', ['2', '3']), ('U201', 'C201', ['2', '3']), ('U201', 'C203', ['7']), ('U201', 'L201', ['8']),
    ('U201', 'C204', None), ('U201', 'C205', None), ('U201', 'C206', None),
    ('U301', 'C302', None), ('U301', 'C301', None), ('U301', 'L301', None), ('U302', 'C307', None), ('U302', 'C306', None),
    ('U401', 'C402', ['2']), ('U401', 'C401', ['2']), ('U401', 'C403', ['3']), ('U401', 'C309', ['39']), ('U401', 'C310', ['38']),
    ('U501', 'C501', None), ('U501', 'C504', None), ('U501', 'C502', None), ('U501', 'C503', None),
    ('U502', 'C505', None), ('U502', 'C506', None), ('U502', 'C508', None), ('U503', 'C507', None),
    ('U601', 'C601', ['4']), ('U601', 'C602', ['4']), ('U601', 'C605', ['4']), ('U601', 'C603', ['3']), ('U601', 'C604', ['3']),
    ('U601', 'C606', ['19']), ('U601', 'C610', ['19']), ('U601', 'C607', ['16']), ('U601', 'C608', ['16']),
    ('U701', 'C702', None), ('U751', 'C752', None), ('U801', 'C801', None),
]

def metrics(b):
    nets = {n: net_len(b, n) for n in CRIT}
    dec = {}
    for ic, c, pins in DEC:
        r = decap(b, ic, c, pins)
        if r is not None:
            dec[f'{c}->{ic}'] = r
    return {'nets': nets, 'decap': dec}

# ------------------------------------------------------------------ render
COL = {'/': '#9e9e9e', '10_power_input': '#e07b39', '20_buck_5v': '#c9a227', '30_regulation': '#7da33c',
       '40_mcu': '#3b82c4', '50_sensors': '#1f9e89', '60_can': '#8e5cc2', '70_output_DO1': '#d64f6b',
       '70_output_DO2': '#d64f6b', '80_supervision': '#4a6fa5'}
NAME = {'/': 'Raíz (fijaciones)', '10_power_input': '10 Entrada y protección', '20_buck_5v': '20 Buck 5 V',
        '30_regulation': '30 Regulación 3,3 V', '40_mcu': '40 MCU / USB', '50_sensors': '50 Sensores',
        '60_can': '60 CAN aislado', '70_output_DO1': '70 Salidas DO', '80_supervision': '80 Supervisión'}

def sheet(f):
    s = f.GetSheetname().strip('/')
    return s or '/'

def draw(ax, b, title):
    import matplotlib.patches as mp
    for d in b.GetDrawings():
        if d.GetLayer() != pcbnew.Edge_Cuts:
            continue
        if d.GetShapeStr() == 'Line':
            (x1, y1), (x2, y2) = loc(d.GetStart()), loc(d.GetEnd())
            ax.plot([x1, x2], [y1, y2], color='#222', lw=1.4)
        else:
            pts = [loc(p) for p in d.GetPolyPoints()] if d.GetShapeStr() == 'Poly' else None
            c = loc(d.GetCenter()); r = mm(d.GetRadius())
            a1 = math.degrees(math.atan2(loc(d.GetStart())[1] - c[1], loc(d.GetStart())[0] - c[0]))
            a2 = math.degrees(math.atan2(loc(d.GetEnd())[1] - c[1], loc(d.GetEnd())[0] - c[0]))
            th = [math.radians(a1 + (((a2 - a1) % 360) * t / 20)) for t in range(21)]
            ax.plot([c[0] + r * math.cos(t) for t in th], [c[1] + r * math.sin(t) for t in th], color='#222', lw=1.4)
    u = b.FindFootprintByReference('U401')
    for z in u.Zones():
        o = z.Outline().Outline(0)
        ax.add_patch(mp.Polygon([loc(o.CPoint(i)) for i in range(o.PointCount())], closed=True, fill=False, hatch='///', ec='#c0392b', lw=0.6, alpha=0.6))
    for z in b.Zones():
        if z.GetIsRuleArea():
            o = z.Outline().Outline(0)
            ax.add_patch(mp.Polygon([loc(o.CPoint(i)) for i in range(o.PointCount())], closed=True, fc='#8e5cc2', alpha=0.18, ec='#8e5cc2', lw=0.8, ls='--'))
    for f in b.GetFootprints():
        bot = f.GetLayer() == pcbnew.B_Cu
        col = COL.get(sheet(f), '#666')
        c = court(f)
        for i in range(c.OutlineCount()):
            o = c.Outline(i)
            ax.add_patch(mp.Polygon([loc(o.CPoint(k)) for k in range(o.PointCount())], closed=True,
                                    fc='none' if bot else col, alpha=0.9 if bot else 0.28, ec=col, lw=0.7, ls=':' if bot else '-'))
        if not bot:
            for p in f.Pads():
                s = p.GetEffectivePolygon(pcbnew.F_Cu)
                if s.OutlineCount():
                    o = s.Outline(0)
                    ax.add_patch(mp.Polygon([loc(o.CPoint(k)) for k in range(o.PointCount())], closed=True, fc='#b5651d', ec='none', alpha=0.85))
        x, y = loc(f.GetPosition())
        bb = c.BBox(); cx, cy = loc(bb.GetCenter())
        small = mm(bb.GetWidth()) * mm(bb.GetHeight()) < 12
        ax.text(cx, cy, f.GetReference(), fontsize=3.2 if small else 4.2, ha='center', va='center',
                color='#555' if bot else '#111', style='italic' if bot else 'normal')
    ax.set_xlim(-3, 115); ax.set_ylim(103, -3); ax.set_aspect('equal')
    ax.set_title(title, fontsize=11)
    ax.set_xticks(range(0, 101, 10)); ax.set_yticks(range(0, 101, 10)); ax.tick_params(labelsize=6)
    ax.grid(color='#ddd', lw=0.3)

def render(pairs, out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.patches as mp
    fig, axs = plt.subplots(1, len(pairs), figsize=(9.5 * len(pairs), 10.5), dpi=170)
    if len(pairs) == 1:
        axs = [axs]
    for ax, (b, t) in zip(axs, pairs):
        draw(ax, b, t)
    hs = [mp.Patch(fc=COL[k], alpha=0.5, ec=COL[k], label=NAME[k]) for k in NAME]
    hs.append(mp.Patch(fc='none', ec='#555', ls=':', label='Cara inferior (TP)'))
    fig.legend(handles=hs, loc='lower center', ncol=5, fontsize=9, frameon=False)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(out)

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'place':
        b = load(sys.argv[2]); place(b, json.load(open(sys.argv[4]))); b.Save(sys.argv[3])
    elif cmd == 'check':
        for r in check(load(sys.argv[2])):
            print(*r)
    elif cmd == 'metrics':
        json.dump(metrics(load(sys.argv[2])), open(sys.argv[3], 'w'), indent=1)
    elif cmd == 'render':
        args = sys.argv[3:]
        render([(load(args[i]), args[i + 1]) for i in range(0, len(args), 2)], sys.argv[2])
