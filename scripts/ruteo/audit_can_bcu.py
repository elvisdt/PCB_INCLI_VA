"""Prueba prospectiva de GND_CAN en una copia temporal; no agrega planos al PCB.
Respeta ISO_sin_relleno_bajo_U601. Registra cada segmento B.Cu y comprueba
una sola region rellena, ocho vias GND_CAN y ausencia de desconexiones CAN GND.
Ejecutar con /usr/bin/python3 (pcbnew + matplotlib).
"""
from pathlib import Path
from collections import defaultdict
import tempfile, shutil, subprocess, json
import pcbnew as k
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as MPath
from matplotlib.patches import PathPatch
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/layout/ruteo'

def xy(p): return [round(v,6) for v in k.ToMM(p)]
with tempfile.TemporaryDirectory(prefix='incli-can-audit-') as tmp:
    tmp=Path(tmp)
    for ext in ('kicad_pcb','kicad_pro','kicad_dru'):
        shutil.copy2(ROOT/f'INCLI-VA.{ext}',tmp/f'INCLI-VA.{ext}')
    pcb=tmp/'INCLI-VA.kicad_pcb';b=k.LoadBoard(str(pcb))
    segs=[];sums=defaultdict(float)
    for t in b.GetTracks():
        if isinstance(t,k.PCB_VIA) or t.GetLayer()!=k.B_Cu:continue
        a,z=xy(t.GetStart()),xy(t.GetEnd())
        if max(a[0],z[0])<125 and min(a[1],z[1])>112:
            length=k.ToMM(t.GetLength());net=t.GetNetname();sums[net]+=length
            segs.append(dict(net=net,start_mm=a,end_mm=z,length_mm=round(length,4),width_mm=k.ToMM(t.GetWidth())))
    segs.sort(key=lambda s:(s['net'],s['start_mm'],s['end_mm']))
    zone=k.ZONE(b);zone.SetLayer(k.B_Cu);zone.SetNet(b.FindNet('GND_CAN'))
    zone.SetLocalClearance(k.FromMM(.2));zone.SetMinThickness(k.FromMM(.2))
    zone.SetThermalReliefGap(k.FromMM(.3));zone.SetThermalReliefSpokeWidth(k.FromMM(.3))
    zone.SetPadConnection(k.ZONE_CONNECTION_THERMAL);zone.SetIslandRemovalMode(0)
    boundary=[(100.5,112.87),(122.02,112.87),(122.02,125.32),(123.95,125.32),
              (123.95,125.7),(124.55,125.7),(124.55,137.45),(100.5,137.45)]
    poly=zone.Outline();poly.NewOutline()
    for x,y in boundary:poly.Append(k.FromMM(x),k.FromMM(y))
    b.Add(zone);b.BuildConnectivity();k.ZONE_FILLER(b).Fill(b.Zones());b.Save(str(pcb))
    fill=zone.GetFilledPolysList(k.B_Cu)
    assert fill.OutlineCount()==1, 'El plano prospectivo queda dividido'
    vias=[]
    for t in b.GetTracks():
        if isinstance(t,k.PCB_VIA) and t.GetNetname()=='GND_CAN':
            assert fill.Contains(t.GetPosition(),0),xy(t.GetPosition())
            vias.append(xy(t.GetPosition()))
    assert len(vias)==8
    subprocess.run(['kicad-cli','pcb','drc','--severity-all','--format','json','-o',str(tmp/'drc.json'),str(pcb)],check=True,capture_output=True)
    drc=json.loads((tmp/'drc.json').read_text())
    errors=[v for v in drc['violations'] if v['severity']=='error']
    disconnected=[v for v in drc['unconnected_items'] if any('GND_CAN' in x.get('description','') for x in v['items'])]
    assert not errors,errors
    assert not disconnected,disconnected
    out=dict(basis='Relleno B.Cu temporal, no guardado en el proyecto; clearance/min thickness 0.2 mm, thermal gap/spoke 0.3 mm; sin eliminar islas.',
             restriction='Courtyard de U601 y BARRERA_CAN libres; no se afirma cobre bajo el cuerpo aislante.',
             boundary_mm=boundary,segments=segs,total_length_by_net_mm={n:round(d,4) for n,d in sorted(sums.items())},
             filled_regions=fill.OutlineCount(),gnd_can_vias_mm=sorted(vias),drc_errors=len(errors),gnd_can_unconnected=len(disconnected))
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'can-bcu-auditoria.json').write_text(json.dumps(out,indent=2)+'\n')
    fig,ax=plt.subplots(figsize=(9,9));vertices=[];codes=[]
    contours=[fill.Outline(0)]+[fill.Hole(0,j) for j in range(fill.HoleCount(0))]
    for contour in contours:
        points=[xy(contour.CPoint(j)) for j in range(contour.PointCount())]
        vertices.extend(points+[points[0]]);codes.extend([MPath.MOVETO]+[MPath.LINETO]*(len(points)-1)+[MPath.CLOSEPOLY])
    ax.add_patch(PathPatch(MPath(vertices,codes),facecolor='#b8dec1',edgecolor='#368348',lw=.3))
    colors={'/BUS_CAN_H':'#d55e00','/60_can/GNDISO_CAN':'#8c46a3','/60_can/V_SOIN':'#0072b2','Net-(C609-Pad1)':'#9b7600'}
    shown=set()
    for s in segs:
        n=s['net'];a,z=s['start_mm'],s['end_mm'];ax.plot([a[0],z[0]],[a[1],z[1]],color=colors[n],lw=2,label=n if n not in shown else None);shown.add(n)
    for x,y in vias:ax.plot(x,y,'o',ms=4,color='#135e24')
    ax.plot(106,124.32,'o',ms=9,color='#135e24');ax.text(106.5,124.32,'J1.5',va='center')
    ax.axvspan(124.6,126,color='#dadada');ax.text(124.85,126,'BARRERA',rotation=90,fontsize=8)
    ax.text(122.6,119,'Courtyard U601\nsin relleno',rotation=90,ha='center',fontsize=9)
    ax.set(xlim=(100,126),ylim=(138,112),xlabel='X (mm)',ylabel='Y (mm)',title='Auditoría prospectiva CAN · B.Cu\nUna región GND_CAN, ocho vías y J1 conectados; DRC 0 errores')
    ax.set_aspect('equal');ax.grid(alpha=.18);ax.legend(loc='lower left',fontsize=8)
    fig.tight_layout();fig.savefig(OUT/'can-bcu-auditoria.png',dpi=170)
    print(json.dumps({key:out[key] for key in ['total_length_by_net_mm','filled_regions','drc_errors','gnd_can_unconnected']},indent=2))
