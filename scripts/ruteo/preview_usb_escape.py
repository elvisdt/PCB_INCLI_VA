"""Evalua el cuello USB pendiente de autorizacion EN UNA COPIA TEMPORAL.
Nunca guarda el cuello en el proyecto. No equivale a cerrar la etapa 3.
"""
from pathlib import Path
import shutil,subprocess,json,math
import pcbnew as k
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Polygon,Circle
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/layout/ruteo';TMP=Path('/tmp/incli-etapa3-propuesta');TMP.mkdir(exist_ok=True)
for ext in ('kicad_pcb','kicad_pro','kicad_dru'):shutil.copy2(ROOT/f'INCLI-VA.{ext}',TMP/f'INCLI-VA.{ext}')
b=k.LoadBoard(str(TMP/'INCLI-VA.kicad_pcb'));net=b.FindNet('/40_mcu/USB_D-')
points=[(173.,107.5),(173.2825,107.7825),(173.6,107.7825),(174.8,107.9)]
for a,z in zip(points,points[1:]):
 t=k.PCB_TRACK(b);t.SetStart(k.VECTOR2I(k.FromMM(a[0]),k.FromMM(a[1])));t.SetEnd(k.VECTOR2I(k.FromMM(z[0]),k.FromMM(z[1])));t.SetLayer(k.F_Cu);t.SetWidth(k.FromMM(.15));t.SetNet(net);b.Add(t)
b.Save(str(TMP/'INCLI-VA.kicad_pcb'))
report=OUT/'etapa3-propuesta-usb-drc.json'
subprocess.run(['kicad-cli','pcb','drc','--severity-all','--format','json','-o',str(report),str(TMP/'INCLI-VA.kicad_pcb')],check=True,capture_output=True)
j=json.loads(report.read_text());errors=[v for v in j['violations'] if v['severity']=='error'];assert not errors,errors
fig,ax=plt.subplots(figsize=(9,7))
for p in b.FindFootprintByReference('U401').Pads():
 x,y=k.ToMM(p.GetPosition())
 if not 171<x<177 or not 105<y<110:continue
 box=p.GetBoundingBox();(xx,yy),(w,h)=k.ToMM(box.GetPosition()),k.ToMM(box.GetSize())
 ax.add_patch(Rectangle((xx,yy),w,h,facecolor='#ead6a5',edgecolor='#91782e',lw=.6))
 ax.text(x,y,p.GetNumber()+'\n'+('D−' if p.GetNumber()=='13' else 'D+' if p.GetNumber()=='14' else 'NC' if p.GetNumber()=='15' else ''),ha='center',va='center',fontsize=10)
for t in b.GetTracks():
 if isinstance(t,k.PCB_VIA) or t.GetLayer()!=k.F_Cu or t.GetNetname() not in ['/40_mcu/USB_D-','/40_mcu/USB_D+']:continue
 a,z=k.ToMM(t.GetStart()),k.ToMM(t.GetEnd());r=k.ToMM(t.GetWidth())/2;dx,dy=z[0]-a[0],z[1]-a[1];d=math.hypot(dx,dy);nx,ny=-dy/d*r,dx/d*r;color='#d45636' if t.GetNetname().endswith('-') else '#247b57'
 ax.add_patch(Polygon([(a[0]+nx,a[1]+ny),(z[0]+nx,z[1]+ny),(z[0]-nx,z[1]-ny),(a[0]-nx,a[1]-ny)],facecolor=color,lw=0))
 for p in [a,z]:ax.add_patch(Circle(p,r,facecolor=color,lw=0))
ax.annotate('Propuesta: 0.15 mm durante 1.923 mm\nSeparación ≥0.2 mm; sin vías',xy=(173.6,107.7825),xytext=(174.2,109.25),arrowprops=dict(arrowstyle='->'),ha='center',fontsize=10)
ax.set(xlim=(171.7,176.5),ylim=(109.6,105.45),xlabel='X (mm)',ylabel='Y (mm)',title='Escape USB en U401 · propuesta pendiente\nDRC de la copia temporal: 0 errores');ax.set_aspect('equal');ax.grid(alpha=.18);fig.tight_layout();fig.savefig(OUT/'etapa3-propuesta-usb-escape.png',dpi=180)
print('Propuesta temporal DRC 0 errores; PCB del proyecto sin cuello. Longitud:',sum(math.dist(a,z) for a,z in zip(points,points[1:])))
