"""Medidas del avance de etapa 3. USB y desacoples MCU siguen pendientes.
Reutiliza el grafo del verificador CAN y comprueba que etapa 2 sigue pasando.
"""
from pathlib import Path
import sys,io,contextlib,importlib.util,json
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('verify_can',Path(__file__).with_name('verify_etapa2.py'))
v=importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()):spec.loader.exec_module(v)
out={'status':'Etapa 3 parcial; USB, C401/C402 y R401 pendientes de decisiones del usuario'}
for name,a,n,z,m in [('EN_C403','U401',3,'C403',1),('RESET_SW401','U401',3,'SW401',2),
                   ('RESET_R802','U401',3,'R802',2),('BOOT_SW402','U401',27,'SW402',2),
                   ('BOOT_R402','U401',27,'R402',2),('UART_TX','U401',37,'J402',1),
                   ('UART_RX','U401',36,'J402',2),('VIO_fuente','C304',1,'C605',1),
                   ('VIO_U601','C304',1,'U601',4)]:
    out[name]=v.route(v.pad(a,n),v.pad(z,m));assert out[name],name
assert out['EN_C403']['centerline_mm']<=5
assert out['EN_C403']['via_vertical_mm']==0
print(json.dumps(out,indent=2))
