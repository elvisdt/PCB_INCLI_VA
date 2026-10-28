"""Agrega la franja de barrera del ADM3055E como rule area (F.Cu y B.Cu)."""
import pcbnew, sys
from lay import OX, OY, FMM
b = pcbnew.LoadBoard(sys.argv[1])
for z in list(b.Zones()):
    if z.GetIsRuleArea() and z.GetZoneName() == 'BARRERA_CAN':
        b.Remove(z)
PTS = [(-0.5, 60.37), (31.4, 60.37), (31.4, 90.0), (-0.5, 90.0), (-0.5, 87.5), (24.6, 87.5), (24.6, 62.87), (-0.5, 62.87)]
z = pcbnew.ZONE(b)
z.SetIsRuleArea(True)
z.SetZoneName('BARRERA_CAN')
ls = pcbnew.LSET(); ls.AddLayer(pcbnew.F_Cu); ls.AddLayer(pcbnew.B_Cu)
z.SetLayerSet(ls)
z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(True); z.SetDoNotAllowPads(True)
z.SetDoNotAllowZoneFills(True); z.SetDoNotAllowFootprints(False)
o = z.Outline(); o.NewOutline()
for x, y in PTS:
    o.Append(FMM(x + OX), FMM(y + OY))
b.Add(z)
b.Save(sys.argv[2])
print('ok')
