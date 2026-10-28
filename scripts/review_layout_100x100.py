#!/usr/bin/python3
"""Verify preserved connectivity and draw a review image of the saved proposal."""
import json
import math
from collections import Counter
from pathlib import Path

import pcbnew as pcb
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, PathPatch, Patch
from matplotlib.path import Path as MplPath
from matplotlib.transforms import Affine2D

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'docs/layout'
data = json.loads((OUT/'posiciones-100x100.json').read_text())
board = pcb.LoadBoard(str(OUT/'INCLI-VA-100x100.kicad_pcb'))
original = pcb.LoadBoard(str(ROOT/'INCLI-VA.kicad_pcb'))

def fingerprint(f):
    return {
        'uuid': f.m_Uuid.AsString(), 'value': f.GetValue(),
        'library': f.GetFPID().GetUniStringLibId(),
        'attributes': f.GetAttributes(), 'fields': dict(f.GetFieldsText()),
        'pads': sorted((p.m_Uuid.AsString(), p.GetNumber(), p.GetNetname(),
                        str(p.GetSize()), str(p.GetDrillSize()), p.GetAttribute())
                       for p in f.Pads()),
    }

old = {f.GetReference(): fingerprint(f) for f in original.GetFootprints()}
excluded_h5 = old.pop('H5', None)  # Four-mounting-hole proposal revision.
new = {f.GetReference(): fingerprint(f) for f in board.GetFootprints()}
assert old == new, [r for r in old.keys() | new.keys() if old.get(r) != new.get(r)]
assert len(new) == 185
assert len(list(board.GetTracks())) == 0
assert len(list(board.Zones())) == 0
fmap = {f.GetReference(): f for f in board.GetFootprints()}
assert sorted(r for r in fmap if r.startswith('H')) == ['H1','H2','H3','H4']
testpoints = {r:f for r,f in fmap.items() if r.startswith('TP')}
assert len(testpoints) == 19
for r,f in testpoints.items():
    assert f.GetLayer() == pcb.B_Cu
    assert f.Reference().GetLayer() == pcb.B_SilkS and f.Reference().IsMirrored()
    assert f.Reference().GetTextSize().x >= pcb.FromMM(1)
    for p in f.Pads():
        assert p.IsOnLayer(pcb.B_Cu) and not p.IsOnLayer(pcb.F_Cu)
rtn = [p.GetNetname() for p in fmap['U101'].Pads() if p.GetNumber() == '25']
assert rtn and set(rtn) == {'/10_power_input/U101_RTN'}
rfzones = list(fmap['U401'].Zones())
assert len(rfzones) == 1 and rfzones[0].GetIsRuleArea()
eb = board.GetBoardEdgesBoundingBox()
# Bounding box includes the 0.1 mm graphic stroke.
assert abs(pcb.ToMM(eb.GetWidth()) - 100.1) < 1e-5
assert abs(pcb.ToMM(eb.GetHeight()) - 100.1) < 1e-5

def gap(a,b):
    return math.hypot(max(a[0]-b[2], b[0]-a[2], 0), max(a[1]-b[3], b[1]-a[3], 0))

boxes = data['boxes']
minimum = min((gap(a,b),r,s) for r,a in boxes.items() for s,b in boxes.items() if r<s)
assert minimum[0] >= 1.0099
summary = {
    'footprints':len(new), 'footprint_identity_fields_pads_nets_DNP_preserved':True,
    'nominal_size_mm':[100,100], 'minimum_envelope_gap_mm':minimum[0],
    'minimum_pair':list(minimum[1:]), 'tracks':0, 'board_zones':0,
    'U101_pad25_net':rtn[0], 'U101_pad25_instances':len(rtn),
    'U401_rule_areas':len(rfzones),
    'mounting_holes':['H1','H2','H3','H4'], 'testpoints_bottom':len(testpoints),
    'reference_board_exclusions':['H5'] if excluded_h5 else [],
    'testpoint_map':{r:next(iter(f.Pads())).GetNetname() for r,f in sorted(testpoints.items())},
    'scope':'Placement review only; electrical loop optimization and routing pending.',
}
(OUT/'reports/integridad-100x100.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))

colors = {'1':'#dc8d29','2':'#bfa337','3':'#8b9f45','4':'#398eb0',
          '5':'#159d87','6':'#9568b0','DO1':'#d56675','DO2':'#d56675',
          '8':'#597daa','mechanical':'#87919a','connectors':'#87919a'}
for side in (pcb.F_Cu, pcb.B_Cu):
    fig, ax = plt.subplots(figsize=(12,13.8),dpi=160)
    fig.patch.set_facecolor('#f5f7fa')
    ax.set_facecolor('#f5f7fa')
    fig.subplots_adjust(left=.035,right=.985,bottom=.10,top=.90)
    verts=[(4,0),(96,0),(100,0),(100,4),(100,53),(92,53),(92,88),(100,88),
           (100,96),(100,100),(96,100),(4,100),(0,100),(0,96),(0,4),(0,0),(4,0),(4,0)]
    codes=[MplPath.MOVETO,MplPath.LINETO,MplPath.CURVE3,MplPath.CURVE3,MplPath.LINETO,
           MplPath.LINETO,MplPath.LINETO,MplPath.LINETO,MplPath.LINETO,MplPath.CURVE3,
           MplPath.CURVE3,MplPath.LINETO,MplPath.CURVE3,MplPath.CURVE3,MplPath.LINETO,
           MplPath.CURVE3,MplPath.CURVE3,MplPath.CLOSEPOLY]
    ax.add_patch(PathPatch(MplPath(verts,codes),fc='white',ec='#263c4b',lw=1.7,zorder=0))
    x0,y0,x1,y1=data['rf_keepout']
    ax.add_patch(Rectangle((x0,y0),x1-x0,y1-y0,fc='#f4e7e5',ec='#c4837f',hatch='////',alpha=.55,lw=.7))
    ax.text(103.5,71,'ANTENA\nSIN COBRE\nNI PIEZAS',ha='center',va='center',fontsize=8,color='#a74848')

    for ref, f in fmap.items():
        visible_pads = [p for p in f.Pads() if p.IsOnLayer(side)]
        if not visible_pads:
            continue
        x0,y0,x1,y1=boxes[ref]
        group=data['groups'][ref]
        dnp=f.IsDNP()
        color=colors[group]
        if side == pcb.F_Cu or ref.startswith(('TP','H')):
            ax.add_patch(Rectangle((x0,y0),x1-x0,y1-y0,facecolor=color,alpha=.12,
                                   edgecolor=color,linewidth=.65,linestyle='--' if dnp else '-'))
        for p in visible_pads:
            x,y=pcb.ToMM(p.GetPosition());x-=100;y-=50
            w,h=pcb.ToMM(p.GetSize()); angle=-p.GetOrientationDegrees()
            if p.GetShape() == pcb.PAD_SHAPE_CIRCLE:
                ax.add_patch(Circle((x,y),w/2,fc='#b96f5e',ec='none',zorder=2))
            else:
                patch=Rectangle((x-w/2,y-h/2),w,h,fc='#b96f5e',ec='none',zorder=2)
                patch.set_transform(Affine2D().rotate_deg_around(x,y,angle)+ax.transData)
                ax.add_patch(patch)
            drill=pcb.ToMM(p.GetDrillSize())[0]
            if drill:
                ax.add_patch(Circle((x,y),drill/2,fc='white',ec='#405565',lw=.6,zorder=3))
        if side == pcb.B_Cu and ref.startswith('TP'):
            tx,ty=pcb.ToMM(f.Reference().GetPosition())
            ax.text(tx-100,ty-50,ref,ha='center',va='center',fontsize=6.5,color='#294358',zorder=4)
        elif side == pcb.F_Cu or ref.startswith('H') or ref in ('J1','J2','J402'):
            ax.text((x0+x1)/2,y0-.32,ref,ha='center',va='bottom',fontsize=4.8,color='#294358',zorder=4)

    # ROT center mark and nominal dimensions are outside routing data.
    if side == pcb.F_Cu:
        ax.plot([48,52],[50,50],color='#087a69',lw=.6,alpha=.5)
        ax.plot([50,50],[48,52],color='#087a69',lw=.6,alpha=.5)
    ax.annotate('',(0,105),(100,105),arrowprops=dict(arrowstyle='|-|',lw=.8,color='#4d6476'))
    ax.text(50,108,'100 mm',ha='center',fontsize=10)
    ax.annotate('',(-4,0),(-4,100),arrowprops=dict(arrowstyle='|-|',lw=.8,color='#4d6476'))
    ax.text(-7,50,'100 mm',ha='center',va='center',rotation=90,fontsize=10)
    ax.set_xlim((-9,114) if side == pcb.F_Cu else (114,-9));ax.set_ylim(111,-3);ax.set_aspect('equal');ax.axis('off')
    fig.suptitle(('CARA SUPERIOR' if side == pcb.F_Cu else 'CARA INFERIOR')+' · 100 × 100 mm',fontsize=18,fontweight='bold',color='#19394e',y=.965)
    fig.text(.5,.936,('185 huellas totales · 4 fijaciones · puntos de prueba en la cara inferior' if side == pcb.F_Cu else 'Vista desde abajo (espejada) · 19 puntos de prueba · sin pistas ni planos'),ha='center',fontsize=10,color='#567186')
    legend=[('1','Entrada y protección'),('2','Buck 5 V'),('3','Regulación 3,3 V'),('4','MCU / USB'),
            ('5','Sensores / ROT'),('6','CAN aislado'),('DO1','Salidas DO'),('8','Supervisión')]
    fig.legend(handles=[Patch(fc=colors[k],label=t) for k,t in legend],loc='lower center',
               bbox_to_anchor=(.5,.055),ncol=4,frameon=False,fontsize=9,handlelength=1.2,columnspacing=2.5)
    fig.text(.05,.028,'Ubicación preliminar. Falta afinar desacoples, retornos y mecánica antes del ruteo.',fontsize=9,color='#647481')
    name = 'ubicacion-100x100' if side == pcb.F_Cu else 'ubicacion-100x100-bottom'
    fig.savefig(OUT/(name+'.png'),dpi=160)
    fig.savefig(OUT/(name+'.svg'))
    svg_path = OUT/(name+'.svg')
    svg_path.write_text('\n'.join(line.rstrip() for line in svg_path.read_text().splitlines())+'\n')
    plt.close(fig)
