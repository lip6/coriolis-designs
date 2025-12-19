
import sys
from   doit      import get_var
from   pdks.nsx2 import setup
setup()

DOIT_CONFIG = { 'verbosity' : 2 }

from coriolis                      import CRL
from coriolis.designflow.task      import ShellEnv, Tasks
from coriolis.designflow.vasy      import Vasy
from coriolis.designflow.iverilog  import Iverilog
from coriolis.designflow.gtkwave   import GtkWave
from coriolis.designflow.yosys     import Yosys
from coriolis.designflow.blif2vst  import Blif2Vst
from coriolis.designflow.klayout   import Klayout
from coriolis.designflow.pnr       import PnR
from coriolis.designflow.s2r       import S2R
from coriolis.designflow.lvx       import Lvx
from coriolis.designflow.graal     import Graal
from coriolis.designflow.cougar    import Cougar
from coriolis.designflow.druc      import Druc
from coriolis.designflow.tasyagle  import TasYagle, STA, XTas
from coriolis.designflow.copy      import Copy
from coriolis.designflow.clean     import Clean
from coriolis.designflow.klayout   import DRC
import doDesign

reuseBlif    = get_var( 'reuse-blif', None )
PnR.textMode = True
topName      = 'arlet6502'

if reuseBlif:
    ruleYosys = Copy.mkRule( 'yosys', f'{topName}.blif', f'./non_generateds/{topName}.{reuseBlif}.blif' )
else:
    ruleYosys = Yosys.mkRule( 'yosys', f'{topName}.v' )

rulePnR = PnR.mkRule( 'gds', [ f'{topName}_cts_r.ap'
                             , f'{topName}_cts_r.vst'
                             , f'{topName}_cts_r.spi' ]
                           , [ruleYosys]
                           , doDesign.scriptMain
                           , topName=topName )
ruleVasy = Vasy.mkRule( 'vasy', topName+'_cts_r.v'
                              , rulePnR.file_target(1)
                              , Vasy.Overwrite|Vasy.RemovePowerSupplies )
ruleIverilog = Iverilog.mkRule( 'iverilog', [ ruleVasy, 'tb_counter.v' ] )
ruleDruc     = Druc    .mkRule( 'druc'    , [rulePnR], flags=0 )
ruleCgt      = PnR     .mkRule( 'cgt' )
ruleGraal    = Graal   .mkRule( 'graal' )
ruleClean    = Clean   .mkRule( [ 'lefRWarning.log', 'cgt.log' ] )

from pdks.nsx2 import setup_techno
#setup_techno( 'sg13g2' )
#setup_techno( 'gf180mcu' )
setup_techno( 'sky130' )

S2R.flags  = S2R.NoReplaceBlackboxes 
ruleS2R    = S2R   .mkRule( 's2r'   , [f'{topName}_cts_r.gds']   , [rulePnR], S2R.flags )
ruleCougar = Cougar.mkRule( 'cougar',  f'{topName}_cts_r_ext.vst', [rulePnR], flags=Cougar.Verbose )
ruleLvx    = Lvx   .mkRule( 'lvx', [ rulePnR.file_target(1)
                                   , ruleCougar.file_target(0) ]
                                 , flags=Lvx.Flatten )
ruleCougarSpi = Cougar.mkRule( 'cougarSpi', f'{topName}_ext.spi'
                                          , [rulePnR]
                                          , Cougar.Transistor|Cougar.Verbose )

TasYagle.ClockName = 'clk'
TasYagle.VddSupply = 1.8  # (5v for GF180Mcu)
staLayout          = ruleCougarSpi.file_target( 0 )
ruleSTA            = STA.mkRule( 'sta', staLayout )

