
from pathlib          import Path
from doit             import get_var
from coriolis         import Cfg 
from coriolis.helpers import overlay
from pdks.gf180mcu    import setup


setup( useHV=True )

DOIT_CONFIG = { 'verbosity' : 2 }

from coriolis.designflow.task     import Tasks
from coriolis.designflow.cougar   import Cougar
from coriolis.designflow.lvx      import Lvx
from coriolis.designflow.x2y      import x2y
from coriolis.designflow.tasyagle import TasYagle, STA, XTas
from coriolis.designflow.druc     import Druc
from coriolis.designflow.pnr      import PnR
from coriolis.designflow.yosys    import Yosys
from coriolis.designflow.klayout  import Klayout, ShowDRC
from coriolis.designflow.blif2vst import Blif2Vst
from coriolis.designflow.copy     import Copy
from coriolis.designflow.alias    import Alias
from coriolis.designflow.clean    import Clean
from pdks.gf180mcu.designflow.drc import DRC
import doDesign

reuseBlif          = get_var( 'reuse-blif', None )
PnR.textMode       = True
doDesign.buildChip = False
#drcFlags           = DRC.SHOW_ERRORS
drcFlags           = 0


if doDesign.buildChip:
    pnrFiles = [ 'chip_r.gds'
               , 'chip_r.vst'
               , 'chip_r.spi'
               , 'chip.vst'
               , 'chip.spi'
               , 'corona_cts_r.vst'
               , 'corona_cts_r.spi'
               , 'corona_r.vst'
               , 'corona_r.spi'
               , 'corona.vst'
               , 'corona.spi'
               , 'arlet6502_cts.vst'
               , 'arlet6502_cts.spi'
               , 'arlet6502.spi'
               ]
else:
    pnrFiles = [ 'arlet6502_cts_r.gds'
               , 'arlet6502_cts_r.spi'
               , 'arlet6502_cts_r.vst'
               ]

if reuseBlif:
    ruleYosys = Copy.mkRule( 'yosys', 'arlet6502.blif', './non_generateds/arlet6502.{}.blif'.format( reuseBlif ))
else:
    ruleYosys = Yosys   .mkRule( 'yosys', 'arlet6502.v' )
ruleB2V     = Blif2Vst.mkRule( 'b2v'     , 'arlet6502.vst', [ruleYosys], flags=0 )
rulePnR     = PnR     .mkRule( 'pnr'     , pnrFiles, [ruleYosys], doDesign.scriptMain )
staLayout = rulePnR.file_target( 2 )
#ruleSTA     = STA     .mkRule( 'sta'     , staLayout )
#ruleXTas    = XTas    .mkRule( 'xtas'    , ruleSTA.file_target(0) )
ruleGds     = Alias   .mkRule( 'gds'     , [rulePnR] )
ruleDRC     = DRC     .mkRule( 'drc'     , [rulePnR], DRC.GF180MCU_C|DRC.ANTENNA|drcFlags )
ruleCgt     = PnR     .mkRule( 'cgt'     )
ruleKlayout = Klayout .mkRule( 'klayout' )
ruleClean   = Clean   .mkRule()
