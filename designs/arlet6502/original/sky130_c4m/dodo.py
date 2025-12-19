
from doit            import get_var
from pdks.sky130_c4m import setup
setup()

DOIT_CONFIG = { 'verbosity' : 2 }

from coriolis.designflow.task     import Tasks
from coriolis.designflow.pnr      import PnR
from coriolis.designflow.lvx      import Lvx
from coriolis.designflow.x2y      import x2y
from coriolis.designflow.tasyagle import TasYagle, STA, XTas
from coriolis.designflow.yosys    import Yosys
from coriolis.designflow.blif2vst import Blif2Vst
from coriolis.designflow.copy     import Copy
from coriolis.designflow.alias    import Alias
from coriolis.designflow.clean    import Clean
import doDesign

reuseBlif          = get_var( 'reuse-blif', None )
PnR.textMode       = True
doDesign.buildChip = False

if reuseBlif:
    ruleYosys = Copy.mkRule( 'yosys', 'arlet6502.blif', './non_generateds/arlet6502.{}.blif'.format( reuseBlif ))
else:
    ruleYosys = Yosys.mkRule( 'yosys', 'arlet6502.v' )
rulePnR   = PnR  .mkRule( 'pnr'  , [ 'arlet6502_cts_r.gds'
                                   , 'arlet6502_cts_r.spi'
                                   , 'arlet6502_cts_r.vst' ]
                                 , [ruleYosys]
                                 , doDesign.scriptMain )
staLayout = rulePnR.file_target( 2 )
ruleSTA   = STA  .mkRule( 'sta' , staLayout )
ruleXTas  = XTas .mkRule( 'xtas', ruleSTA.file_target(0) )
ruleGds   = Alias.mkRule( 'gds' , [rulePnR] )
ruleCgt   = PnR  .mkRule( 'cgt' )
ruleClean = Clean.mkRule()
