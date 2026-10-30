#!/usr/bin/python3
"""Etapa 6: movimientos de pasivos aprobados por el usuario (hallazgo 4, courtyards < 1 mm).

Uso (KiCad cerrado, una sola vez, sobre el PCB de 18f17ae): /usr/bin/python3 -B scripts/ruteo/etapa6_mover_pasivos.py [PCB]
Después: etapa6_teardrops.py (rellena zonas y teardrops), DRC y etapa6_fab.py.
De los 6 movimientos aprobados, solo C401 pasa el DRC sin rerutear pistas de otras redes (probado uno por
uno, en copia aislada y con zonas rellenas). C404, C507, R502 y C506 chocan con USB D±, el tronco +3V3_A o
IMU_INT1/INT2: esperan decisión del usuario. C402 no se mueve: alejarlo 0.22 mm de U401 (lo necesario para
0.5 mm de courtyard) llevaría la pista al pin 3V3 de 1.97 a ~2.2 mm, por encima del límite de 2 mm.
Reconexión de cada extremo de pista que estaba en un pad (o vía en pad) movido:
  - si el extremo viejo sigue dentro del pad movido, no se toca;
  - si la pista va en el eje del desplazamiento, se estira (o acorta) ese extremo;
  - si no, se agrega un tramo corto en la misma capa y ancho, del extremo viejo al nuevo.
Las vías que están dentro de un pad movido se mueven con él. Los tramos nuevos van al grupo CLAUDE_ETAPA6_MOV.
"""
import sys
import pcbnew as k

pcb = sys.argv[1] if len(sys.argv) > 1 else 'INCLI-VA.kicad_pcb'
MOV = {'C401': ((189.2, 100.6), (0, -0.8))}
iu = k.FromMM

b = k.LoadBoard(pcb)
g = k.PCB_GROUP(b); g.SetName('CLAUDE_ETAPA6_MOV'); b.Add(g)
log = []
for ref, ((x0, y0), (dx, dy)) in MOV.items():
    f = b.FindFootprintByReference(ref)
    p0 = f.GetPosition()
    assert abs(p0.x - iu(x0)) < iu(0.01) and abs(p0.y - iu(y0)) < iu(0.01), f'{ref} ya no está en la posición original'
    d = k.VECTOR2I(iu(dx), iu(dy))
    pads = list(f.Pads())
    viejos = {p.GetNumber(): k.PAD(p) for p in pads}          # copia en la posición original (para HitTest)
    vias = [t for t in b.GetTracks() if t.Type() == k.PCB_VIA_T
            and any(t.GetNetCode() == p.GetNetCode() and p.HitTest(t.GetPosition()) for p in pads)]
    puntos = [(viejos[p.GetNumber()], p.GetNetCode()) for p in pads] + [(v, v.GetNetCode()) for v in vias]
    pistas = [t for t in b.GetTracks() if t.Type() == k.PCB_TRACE_T]
    f.Move(d)
    for v in vias: v.Move(d)
    for t in pistas:
        for extremo in ('Start', 'End'):
            e = getattr(t, 'Get' + extremo)()
            dueño = next((o for o, nc in puntos if nc == t.GetNetCode()
                          and (o.HitTest(e) if isinstance(o, k.PAD) else o.GetPosition() == e)), None)
            if dueño is None: continue
            nuevo = k.VECTOR2I(e.x + d.x, e.y + d.y)
            pad_nuevo = next((p for p in f.Pads() if p.GetNetCode() == t.GetNetCode() and p.HitTest(e)), None)
            if isinstance(dueño, k.PAD) and pad_nuevo is not None:
                log.append(f'{ref}: {t.GetNetname()} extremo dentro del pad movido, sin cambio'); continue
            o = t.GetEnd() if extremo == 'Start' else t.GetStart()
            tx, ty = o.x - e.x, o.y - e.y
            if (tx * d.y - ty * d.x) == 0:                         # colineal: estirar
                getattr(t, 'Set' + extremo)(nuevo)
                log.append(f'{ref}: {t.GetNetname()} {b.GetLayerName(t.GetLayer())} estirada')
            else:                                                  # tramo corto
                s = k.PCB_TRACK(b); s.SetStart(e); s.SetEnd(nuevo); s.SetLayer(t.GetLayer())
                s.SetWidth(t.GetWidth()); s.SetNetCode(t.GetNetCode()); b.Add(s); g.AddItem(s)
                log.append(f'{ref}: {t.GetNetname()} {b.GetLayerName(t.GetLayer())} tramo de {(dx ** 2 + dy ** 2) ** .5:.2f} mm')
    np = f.GetPosition(); log.append(f'{ref}: ({x0}, {y0}) -> ({np.x / 1e6:.2f}, {np.y / 1e6:.2f}); vías movidas: {len(vias)}')
b.Save(pcb)
print('\n'.join(log))
