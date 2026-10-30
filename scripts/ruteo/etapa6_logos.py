#!/usr/bin/python3
"""Etapa 6: logos en B.Silkscreen (rc4).

Uso (KiCad cerrado, desde la carpeta del proyecto):
  /usr/bin/python3 -B scripts/ruteo/etapa6_logos.py huella        genera lib/INCLI-VA.pretty/Logo_*.kicad_mod
  /usr/bin/python3 -B scripts/ruteo/etapa6_logos.py placa X Y     coloca LOGO1 (centro en X, Y mm) en la cara inferior
  /usr/bin/python3 -B scripts/ruteo/etapa6_logos.py reserva       marca en User.Comments la zona reservada para Hunter

Fuente: docs/reference/logos/ (ver su README). Imagen monocroma, negro = serigrafía. Equivale a bitmap2component:
la imagen se recorta a la tinta, se escala al ancho pedido y se convierte en polígonos rellenos (unión de tramos
por fila sobre una rejilla de RES mm, simplificada). La huella se dibuja en F.SilkS y se voltea al colocarla, así
se lee bien desde abajo. En la placa: solo de placa (board only, F8 no la borra), fuera del BOM y de la posición,
referencia oculta en Fab. Idempotente.
"""
import sys
from PIL import Image, ImageFilter
import pcbnew as k

LIB = 'lib/INCLI-VA.pretty'
LOGOS = {'Logo_Volnyx_Wordmark': ('docs/reference/logos/volnyx_wordmark.png', 17.0, 'LOGO1')}
RES = 0.025          # mm por píxel de la rejilla
TRAZO_MIN = 0.15     # mm (JLCPCB: ancho mínimo de línea de serigrafía)


def tinta(path, ancho):
    im = Image.open(path).convert('L')
    im = im.point(lambda v: 255 if v < 128 else 0)          # tinta = 255
    im = im.crop(im.getbbox())
    w = round(ancho / RES); h = round(im.height * w / im.width)
    return im.resize((w, h), Image.LANCZOS).point(lambda v: 255 if v >= 128 else 0)


def chequeo_trazo(im):
    """Píxeles que se pierden con una apertura morfológica de TRAZO_MIN (trazos más finos) y que se rellenan con
    un cierre (huecos más finos). Ambos deben ser ~0, salvo el escalonado de bordes."""
    n = round(TRAZO_MIN / RES) | 1
    ab = im.filter(ImageFilter.MinFilter(n)).filter(ImageFilter.MaxFilter(n))
    ce = im.filter(ImageFilter.MaxFilter(n)).filter(ImageFilter.MinFilter(n))
    tot = sum(1 for v in im.get_flattened_data() if v)
    perd = sum(1 for a, b in zip(im.get_flattened_data(), ab.get_flattened_data()) if a and not b)
    rell = sum(1 for a, b in zip(im.get_flattened_data(), ce.get_flattened_data()) if b and not a)
    return tot, perd, rell


def poligono(im):
    ps = k.SHAPE_POLY_SET()
    w, h = im.size; px = im.load(); s = k.FromMM(RES)
    x0, y0 = -w * s // 2, -h * s // 2
    for y in range(h):
        x = 0
        while x < w:
            if px[x, y]:
                a = x
                while x < w and px[x, y]: x += 1
                r = k.SHAPE_LINE_CHAIN()
                for cx, cy in ((a, y), (x, y), (x, y + 1), (a, y + 1)):
                    r.Append(x0 + cx * s, y0 + cy * s)
                r.SetClosed(True); ps.AddOutline(r)
            else:
                x += 1
    ps.Simplify()
    ps.Fracture()
    return ps, w * RES, h * RES


def huella():
    for nombre, (path, ancho, _) in LOGOS.items():
        im = tinta(path, ancho)
        tot, perd, rell = chequeo_trazo(im)
        print(f'{nombre}: trazos < {TRAZO_MIN} mm: {perd}/{tot} px ({100*perd/tot:.2f} %), '
              f'huecos < {TRAZO_MIN} mm: {rell} px')
        ps, w, h = poligono(im)
        fp = k.FOOTPRINT(None)
        fp.SetFPIDAsString(f'INCLI-VA:{nombre}')
        fp.SetLibDescription(f'Logo en serigrafía, {w:.2f} x {h:.2f} mm, desde {path} (rejilla {RES} mm)')
        fp.SetKeywords('logo')
        fp.SetReference('LOGO**'); fp.SetValue(nombre)
        for t, y in ((fp.Reference(), -h / 2 - 1), (fp.Value(), h / 2 + 1)):
            t.SetLayer(k.F_Fab); t.SetPosition(k.VECTOR2I(0, k.FromMM(y)))
        fp.Reference().SetVisible(False); fp.Value().SetVisible(False)   # sin texto en la placa
        for i in range(ps.OutlineCount()):     # fp_poly guarda un solo contorno: una forma por contorno
            uno = k.SHAPE_POLY_SET(); uno.AddOutline(ps.COutline(i))
            sh = k.PCB_SHAPE(fp, k.SHAPE_T_POLY)
            sh.SetPolyShape(uno); sh.SetFilled(True); sh.SetWidth(0); sh.SetLayer(k.F_SilkS)
            fp.Add(sh)
        fp.SetAttributes(k.FP_BOARD_ONLY | k.FP_EXCLUDE_FROM_BOM | k.FP_EXCLUDE_FROM_POS_FILES)
        k.FootprintSave(LIB, fp)
        print(f'{LIB}/{nombre}.kicad_mod: {w:.2f} x {h:.2f} mm, {ps.FullPointCount()} puntos')


def placa(x, y):
    b = k.LoadBoard('INCLI-VA.kicad_pcb')
    for nombre, (_, _, ref) in LOGOS.items():
        viejo = b.FindFootprintByReference(ref)
        if viejo: b.Delete(viejo)
        f = k.FootprintLoad(LIB, nombre)
        f.SetReference(ref)
        f.SetFPIDAsString(f'INCLI-VA:{nombre}')
        b.Add(f)
        f.SetPosition(k.VECTOR2I(k.FromMM(x), k.FromMM(y)))
        f.Flip(f.GetPosition(), k.FLIP_DIRECTION_LEFT_RIGHT)
        print(ref, nombre, x, y, f.GetLayerName())
    b.Save('INCLI-VA.kicad_pcb')


# Zona libre de la cara inferior para el logo de Hunter (rc5): 16 x 6 mm sin TP, pads, vías, courtyards, serigrafía,
# arandelas de H1–H5 ni APOYO_CAJA_B, con 0.3 mm de margen; arriba de BARRERA_CAN (y 110.37). Solo User.Comments.
RESERVA = (123.5, 106.5, 16.0, 6.0)


def reserva():
    b = k.LoadBoard('INCLI-VA.kicad_pcb')
    for g in list(b.Groups()):
        if g.GetName() == 'CLAUDE_RESERVA_HUNTER':
            for it in list(g.GetItems()): b.Delete(it)
            b.Delete(g)
    g = k.PCB_GROUP(b); g.SetName('CLAUDE_RESERVA_HUNTER'); b.Add(g)
    cx, cy, w, h = RESERVA
    r = k.PCB_SHAPE(b, k.SHAPE_T_RECT)
    r.SetStart(k.VECTOR2I(k.FromMM(cx - w / 2), k.FromMM(cy - h / 2)))
    r.SetEnd(k.VECTOR2I(k.FromMM(cx + w / 2), k.FromMM(cy + h / 2)))
    r.SetWidth(k.FromMM(0.1)); r.SetLayer(k.Cmts_User); b.Add(r); g.AddItem(r)
    t = k.PCB_TEXT(b); t.SetText('RESERVA LOGO HUNTER (B.Silkscreen, <= 16 x 6 mm)')
    t.SetPosition(k.VECTOR2I(k.FromMM(cx), k.FromMM(cy))); t.SetTextSize(k.VECTOR2I(k.FromMM(0.6), k.FromMM(0.6)))
    t.SetTextThickness(k.FromMM(0.1)); t.SetLayer(k.Cmts_User); b.Add(t); g.AddItem(t)
    b.Save('INCLI-VA.kicad_pcb')
    print('reserva Hunter:', RESERVA)


if __name__ == '__main__':
    if sys.argv[1] == 'huella': huella()
    elif sys.argv[1] == 'reserva': reserva()
    else: placa(float(sys.argv[2]), float(sys.argv[3]))
