"""Verificacion de la etapa 5 sobre un PCB con zonas rellenas. No modifica el PCB.
Uso: verify_etapa5.py [PCB]  -> JSON en stdout (islas, cobertura, ranuras, exclusiones).
`componentes(board, nets)` tambien lo usa etapa5_planos.py para coser islas.
"""
import json, math, sys
from pathlib import Path
import pcbnew as k

mm, tm = k.FromMM, k.ToMM
F, B = k.F_Cu, k.B_Cu
NETS = ('GND_VEH', 'GND_CAN', '/10_power_input/U101_RTN')


def componentes(b, nets=NETS):
    """Union-find de polígonos rellenos, pistas, vías y pads de cada red.
    Devuelve {red: [(area_mm2, [(zona, capa, idx, area, bbox)], n_items)]} ordenado de mayor a menor."""
    out = {}
    for net in nets:
        nodes, polys = [], []
        for z in b.Zones():
            if z.GetIsRuleArea() or z.GetNetname() != net: continue
            for L in (F, B):
                if not z.IsOnLayer(L): continue
                s = z.GetFilledPolysList(L)
                for i in range(s.OutlineCount()):
                    polys.append(len(nodes)); nodes.append(('poly', z, L, s, i))
        items = []
        for t in b.GetTracks():
            if t.GetNetname() != net: continue
            items.append(len(nodes)); nodes.append(('via' if t.Type() == k.PCB_VIA_T else 'trk', t))
        for f in b.GetFootprints():
            for p in f.Pads():
                if p.GetNetname() == net:
                    items.append(len(nodes)); nodes.append(('pad', p))
        par = list(range(len(nodes)))
        def find(a):
            while par[a] != a: par[a] = par[par[a]]; a = par[a]
            return a
        def join(a, c): par[find(a)] = find(c)
        def inpoly(L, pt):
            return [n for n in polys if nodes[n][2] == L and nodes[n][3].Contains(pt, nodes[n][4])]
        def probes(p):
            bb = p.GetBoundingBox(); c = p.GetPosition(); e = mm(.42)
            return [k.VECTOR2I(int(x), int(y)) for x, y in ((bb.GetLeft() - e, c.y), (bb.GetRight() + e, c.y),
                                                           (c.x, bb.GetTop() - e), (c.x, bb.GetBottom() + e))]
        ends = []
        for n in items:
            kind, it = nodes[n]
            if kind == 'via':
                for L in (F, B):
                    for q in inpoly(L, it.GetPosition()): join(n, q)
                ends.append((n, it.GetPosition(), None, tm(it.GetWidth(F)) / 2))
            elif kind == 'trk':
                L = it.GetLayer()
                for pt in (it.GetStart(), it.GetEnd()):
                    for q in inpoly(L, pt): join(n, q)
                    ends.append((n, pt, L, 0))
            else:
                for L in (F, B):
                    if not it.IsOnLayer(L): continue
                    for pt in probes(it):
                        for q in inpoly(L, pt): join(n, q)
        # contactos entre pistas, vias y pads
        pads = [n for n in items if nodes[n][0] == 'pad']
        for i, (n, pt, L, r) in enumerate(ends):
            for m, qt, L2, r2 in ends[i + 1:]:
                if (L is None or L2 is None or L == L2) and math.hypot(tm(pt.x - qt.x), tm(pt.y - qt.y)) <= max(r, r2) + .01:
                    join(n, m)
            for m in pads:
                p = nodes[m][1]
                if (L is None or p.IsOnLayer(L)) and p.HitTest(pt, mm(r)): join(n, m)
        # Fragmentos de un mismo pad (EP + taladros termicos con el mismo numero) son un solo pad.
        same = {}
        for m in pads:
            p = nodes[m][1]; key = (p.GetParentFootprint().GetReference(), p.GetNumber())
            if key in same: join(m, same[key])
            else: same[key] = m
        groups = {}
        for n in range(len(nodes)): groups.setdefault(find(n), []).append(n)
        res = []
        for g in groups.values():
            ps = [nodes[n] for n in g if nodes[n][0] == 'poly']
            info = []
            for _, z, L, s, i in ps:
                bb = s.Outline(i).BBox()
                info.append((z.GetZoneName(), b.GetLayerName(L), i, abs(s.Outline(i).Area()) / 1e12,
                             tuple(round(tm(v), 2) for v in (bb.GetLeft(), bb.GetTop(), bb.GetRight(), bb.GetBottom()))))
            res.append((sum(x[3] for x in info), info, len(g) - len(ps), [nodes[n] for n in g if nodes[n][0] != 'poly'], ps))
        res.sort(key=lambda r: -r[0])
        out[net] = res
    return out


def cobertura(b, net, L, rect, step=.25):
    """Fraccion de puntos de una ventana cubiertos por el relleno de `net` en la capa L."""
    ss = [z.GetFilledPolysList(L) for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() == net and z.IsOnLayer(L)]
    x0, y0, x1, y1 = rect; tot = hit = 0
    y = y0
    while y <= y1:
        x = x0
        while x <= x1:
            tot += 1; pt = k.VECTOR2I(mm(x), mm(y))
            if any(s.Contains(pt) for s in ss): hit += 1
            x += step
        y += step
    return round(hit / tot, 3)


def main():
    root = Path(__file__).resolve().parents[2]
    b = k.LoadBoard(str(Path(sys.argv[1]) if len(sys.argv) > 1 else root / 'INCLI-VA.kicad_pcb'))
    rep = {'islas': {}, 'zonas': {}}
    for z in b.Zones():
        if z.GetIsRuleArea() or not z.GetZoneName().startswith('E5_'): continue
        for L in (F, B):
            if z.IsOnLayer(L):
                s = z.GetFilledPolysList(L)
                rep['zonas'][z.GetZoneName()] = {'net': z.GetNetname(), 'capa': b.GetLayerName(L), 'poligonos': s.OutlineCount(),
                                                 'area_mm2': round(s.Area() / 1e12, 1), 'rellena': z.IsFilled()}
    for net, comps in componentes(b).items():
        rep['islas'][net] = [{'area_mm2': round(a, 1), 'items': n, 'poligonos': [
            {'zona': i[0], 'capa': i[1], 'area_mm2': round(i[3], 2), 'bbox': i[4]} for i in info] if len(comps) > 1 or len(info) < 6 else len(info)}
            for a, info, n, *_ in comps]
    # Cobertura del plano B.Cu bajo los lazos de conmutacion y los sensores.
    def bb(ref):
        f = b.FindFootprintByReference(ref); c = f.GetCourtyard(k.F_CrtYd).BBox()
        return tuple(tm(v) for v in (c.GetLeft(), c.GetTop(), c.GetRight(), c.GetBottom()))
    def union(*refs):
        r = [bb(x) for x in refs]
        return (min(a[0] for a in r), min(a[1] for a in r), max(a[2] for a in r), max(a[3] for a in r))
    rep['cobertura_BCu'] = {name: {'ventana': [round(v, 2) for v in w], 'GND_VEH': cobertura(b, 'GND_VEH', B, w)}
                            for name, w in (('U201_L201', union('U201', 'L201')), ('U301_L301', union('U301', 'L301')),
                                            ('U501', bb('U501')), ('U502', bb('U502')), ('U503', bb('U503')))}
    # Ranuras bajo pistas de senal: tramo continuo mas largo sin GND en la capa opuesta.
    ref_nets = ('GND_VEH', 'GND_CAN')
    ss = {L: [z.GetFilledPolysList(L) for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() in ref_nets and z.IsOnLayer(L)] for L in (F, B)}
    worst = {}
    for t in b.GetTracks():
        if t.Type() == k.PCB_VIA_T or t.GetNetname() in NETS: continue
        if t.GetNetClassName() in ('HV', 'PROT', 'DO', '5V'): continue
        other = B if t.GetLayer() == F else F
        a, z = t.GetStart(), t.GetEnd(); L = tm(t.GetLength())
        n = max(1, int(L / .2)); run = best = 0
        for i in range(n + 1):
            pt = k.VECTOR2I(int(a.x + (z.x - a.x) * i / n), int(a.y + (z.y - a.y) * i / n))
            if any(s.Contains(pt) for s in ss[other]): run = 0
            else:
                run += L / n; best = max(best, run)
        key = t.GetNetname()
        if best > worst.get(key, (0,))[0]:
            worst[key] = (round(best, 2), b.GetLayerName(t.GetLayer()), [round(tm(a.x), 2), round(tm(a.y), 2)], [round(tm(z.x), 2), round(tm(z.y), 2)])
    rep['ranuras_bajo_senal_mm'] = dict(sorted(((n, w) for n, w in worst.items() if w[0] > 3.0), key=lambda kv: -kv[1][0]))
    # Exclusiones: antena, iman, area B.
    def polys_in(rect):
        x0, y0, x1, y1 = rect; win = k.SHAPE_POLY_SET(); win.NewOutline()
        for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)): win.Append(mm(x), mm(y))
        a = 0
        for z in b.Zones():
            if z.GetIsRuleArea(): continue
            for L in (F, B):
                if z.IsOnLayer(L):
                    s = z.GetFilledPolysList(L).CloneDropTriangulation(); s.BooleanIntersection(win); a += s.Area() / 1e12
        return round(a, 3)
    rep['cobre_relleno_en_antena_mm2'] = polys_in((191.94, 91.5, 212.94, 139.5))
    vi = []
    for t in b.GetTracks():
        if t.Type() != k.PCB_VIA_T: continue
        x, y = tm(t.GetPosition().x), tm(t.GetPosition().y)
        if math.hypot(x - 150, y - 100) < 8.95: vi.append([round(x, 2), round(y, 2), t.GetNetname(), t.GetFrontTentingMode() == k.TENTING_MODE_TENTED or t.GetFrontTentingMode() == k.TENTING_MODE_FROM_BOARD])
        if math.hypot(x - 163.5, y - 99) < 4.3: rep.setdefault('vias_en_area_B', []).append([round(x, 2), round(y, 2)])
    rep['vias_en_circulo_iman'] = vi
    # Distancia de cada punto del relleno GND a la via o taladro GND mas cercano (costura).
    holes = [(tm(t.GetPosition().x), tm(t.GetPosition().y), t.GetNetname()) for t in b.GetTracks() if t.Type() == k.PCB_VIA_T and t.GetNetname() in ('GND_VEH', 'GND_CAN')]
    holes += [(tm(p.GetPosition().x), tm(p.GetPosition().y), p.GetNetname()) for f in b.GetFootprints() for p in f.Pads()
              if p.GetNetname() in ('GND_VEH', 'GND_CAN') and p.GetAttribute() == k.PAD_ATTRIB_PTH]
    for net in ('GND_VEH', 'GND_CAN'):
        hs = [(x, y) for x, y, n in holes if n == net]
        sb = [z.GetFilledPolysList(B) for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() == net and z.IsOnLayer(B)]
        ds = []
        for i in range(101):
            for j in range(101):
                x, y = 100 + i, 50 + j
                if any(s.Contains(k.VECTOR2I(mm(x), mm(y))) for s in sb):
                    ds.append((min(math.hypot(x - a, y - c) for a, c in hs), x, y))
        ds.sort()
        rep.setdefault('costura', {})[net] = {'vias_y_taladros': len(hs), 'puntos_1mm': len(ds),
            'dist_max_mm': round(ds[-1][0], 2), 'en': ds[-1][1:], 'p95_mm': round(ds[int(.95 * (len(ds) - 1))][0], 2),
            'frac_hasta_5mm': round(sum(d <= 5 for d, *_ in ds) / len(ds), 3)}
    # Poligonos F.Cu de GND_VEH en la ventana de sensores (x143-173, y88-118).
    win = k.SHAPE_POLY_SET(); win.NewOutline()
    for x, y in ((143, 88), (173, 88), (173, 118), (143, 118)): win.Append(mm(x), mm(y))
    for z in b.Zones():
        if z.GetZoneName() == 'E5_GND_VEH_F':
            s = z.GetFilledPolysList(F).CloneDropTriangulation(); s.BooleanIntersection(win)
            rep['sensores_FCu'] = {'regiones': s.OutlineCount(), 'area_mm2': round(s.Area() / 1e12, 1)}
    rep['vias_costura_CLAUDE_ETAPA5'] = sum(1 for g in b.Groups() if g.GetName() == 'CLAUDE_ETAPA5' for i in g.GetItems() if i.Type() == k.PCB_VIA_T)
    print(json.dumps(rep, indent=1, ensure_ascii=False))


if __name__ == '__main__':
    main()
