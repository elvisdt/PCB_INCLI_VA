"""Medidas finales de etapa 3 sobre el PCB guardado; incluye regresion CAN.
Falla si el USB esta abierto. Nunca sustituye el PCB por una copia temporal.
"""
from pathlib import Path
import sys,io,contextlib,importlib.util,json,math
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('verify_can',Path(__file__).with_name('verify_etapa2.py'))
v=importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()):spec.loader.exec_module(v)
out={'basis':'PCB guardado; centros y bordes reales de pads; vias con 1.6 mm de altura','paths':{}}
for name,a,n,z,m in [('EN_C403','U401',3,'C403',1),('EN_R401','U401',3,'R401',2),
                   ('RESET_SW401','U401',3,'SW401',2),('RESET_R802','U401',3,'R802',2),
                   ('BOOT_SW402','U401',27,'SW402',2),('BOOT_R402','U401',27,'R402',2),
                   ('UART_TX','U401',37,'J402',1),('UART_RX','U401',36,'J402',2),
                   ('3V3_MCU','C304',1,'U401',2),('3V3_CAN','C304',1,'U601',4),
                   ('CC1','J401','A5','R403',1),('CC2','J401','B5','R404',1),
                   ('VBUS_A4','J401','A4','U402',5),('VBUS_A9','J401','A9','U402',5)]:
    r=v.route(v.pad(a,n),v.pad(z,m));assert r,name;out['paths'][name]=r
assert out['paths']['EN_C403']['centerline_mm']<=5
assert out['paths']['EN_R401']['pad_edge_path_mm']<=5
out['decoupling']=[]
for ref,ic,pin in [('C402','U401',2),('C401','U401',2),('C404','U402',5),('C801','U801',5)]:
    r=v.route(v.pad(ic,pin),v.pad(ref,1));assert r,ref
    r.update(reference=ref,value=v.b.FindFootprintByReference(ref).GetValue(),ic=ic,pin=pin)
    if ref in ['C402','C404']:assert r['pad_edge_path_mm']<=1
    if ref=='C401':assert any(v.inside(v.pad('C402',1),p,p[2]) for p in r['path'])
    out['decoupling'].append(r)
usb={s:v.route(v.pad('J401',p),v.pad('U401',n)) for s,p,n in [('D-','A7',13),('D+','A6',14)]}
for s,r in usb.items():assert r and r['via_vertical_mm']==0,s
usb['delta_mm']=round(abs(usb['D-']['centerline_mm']-usb['D+']['centerline_mm']),4);assert usb['delta_mm']<=.5
usb['via_count_by_net']={n:sum(isinstance(t,v.k.PCB_VIA) and t.GetNetname()=='/40_mcu/USB_'+n for t in v.b.GetTracks()) for n in ['D-','D+']}
assert usb['via_count_by_net']=={'D-':2,'D+':2}
usb['branches']={}
for sign,pin,upin in [('D+','B6',14),('D-','B7',13)]:
    path=v.route(v.pad('J401',pin),v.pad('U401',upin))['path'];main=set(usb[sign]['path']);length=0.;via=0.
    for a,z in zip(path,path[1:]):
        if a in main:break
        if a[2]!=z[2]:length+=v.VIA_HEIGHT;via+=v.VIA_HEIGHT
        else:length+=math.dist(a[:2],z[:2])
    usb['branches'][pin]={'to_main_junction_total_mm':round(length,4),'planar_mm':round(length-via,4),'via_vertical_mm':via}
out['USB_final']=usb
out['status']='Etapa 3 completa en el PCB guardado'
neck=[t for t in v.b.GetTracks() if not isinstance(t,v.k.PCB_VIA) and t.GetNetname()=='/40_mcu/USB_D-' and abs(v.k.ToMM(t.GetWidth())-.15)<1e-6]
assert len(neck)==3, 'Escape autorizado: tres segmentos'
expected={frozenset([a,z]) for a,z in zip([(173.,107.5),(173.2825,107.7825),(173.6,107.7825)],[(173.2825,107.7825),(173.6,107.7825),(174.8,107.9)])}
actual={frozenset([v.xy(t.GetStart()),v.xy(t.GetEnd())]) for t in neck}
assert actual==expected
out['USB_escape']={'width_mm':.15,'length_mm':round(sum(v.k.ToMM(t.GetLength()) for t in neck),6),'layer':'F.Cu','approved':True}
assert abs(out['USB_escape']['length_mm']-1.922754)<.00001
for t in v.b.GetTracks():
    if isinstance(t,v.k.PCB_VIA) or t.GetNetname() not in ['/40_mcu/USB_D-','/40_mcu/USB_D+']:continue
    assert abs(v.k.ToMM(t.GetWidth())-.3)<1e-6 or t in neck
out['central_ground_plated_holes']=sum(p.GetNumber()=='41' and p.GetDrillSize().x>0 for p in v.b.FindFootprintByReference('U401').Pads());assert out['central_ground_plated_holes']==12
print(json.dumps(out,indent=2))
