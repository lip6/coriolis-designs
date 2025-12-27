
from pathlib          import Path
from coriolis         import Cfg 
from coriolis.helpers import overlay
from pdks.gf180mcu    import setup


setup(  useHV=True )

DOIT_CONFIG = { 'verbosity' : 2 }

from coriolis.designflow.task     import Tasks
from coriolis.designflow.cougar   import Cougar
from coriolis.designflow.lvx      import Lvx
from coriolis.designflow.tasyagle           import TasYagle, STA, XTas
from coriolis.designflow.druc     import Druc
from coriolis.designflow.pnr      import PnR
from coriolis.designflow.yosys    import Yosys
from coriolis.designflow.klayout  import Klayout, ShowDRC
from coriolis.designflow.blif2vst import Blif2Vst
from coriolis.designflow.alias    import Alias
from coriolis.designflow.clean    import Clean
from pdks.gf180mcu.designflow.drc import DRC
PnR.textMode = True

import doDesign
topName            = 'ibex'
topName            = 'aes'
topName            = 'arlet6502'
topName            = 'picorv32'
topName            = 'ao68000'
topName            = 'jpeg_encoder'
topName            = 'mac'
topName            = 'uart_rx'
topName            = 'counter'
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
               , f'{topName}_cts.vst'
               , f'{topName}_cts.spi'
               , f'{topName}.spi'
               ]
else:
    pnrFiles = [ f'{topName}_cts_r.gds'
               , f'{topName}_cts_r.spi'
               , f'{topName}_cts_r.vst'
               ]


ruleYosys   = Yosys   .mkRule( 'yosys'   , f'{topName}.v' )
ruleB2V     = Blif2Vst.mkRule( 'b2v'     , f'{topName}.vst', [ruleYosys], flags=0 )
rulePnR     = PnR     .mkRule( 'pnr'     , pnrFiles, [ruleYosys], doDesign.scriptMain )
ruleGds     = Alias   .mkRule( 'gds'     , [rulePnR] )
ruleDRC     = DRC     .mkRule( 'drc'     , [rulePnR], DRC.GF180MCU_C|DRC.ANTENNA|drcFlags )
staLayout = rulePnR.file_target( 2 )
ruleSTA     = STA     .mkRule( 'sta'    , staLayout )
ruleXTas    = XTas   .mkRule( 'xtas'   , ruleSTA.file_target(0) )
ruleCgt     = PnR     .mkRule( 'cgt'     )
ruleKlayout = Klayout .mkRule( 'klayout' )
ruleClean   = Clean   .mkRule()
