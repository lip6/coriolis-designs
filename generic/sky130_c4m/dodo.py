from pdks.sky130_c4m    import setup
setup(  )

DOIT_CONFIG = { 'verbosity' : 2 }

from coriolis.designflow.task     import Tasks
from coriolis.designflow.pnr      import PnR
from coriolis.designflow.lvx      import Lvx
from coriolis.designflow.x2y      import x2y
from coriolis.designflow.tasyagle import TasYagle, STA, XTas
from coriolis.designflow.yosys    import Yosys
from coriolis.designflow.blif2vst import Blif2Vst
from coriolis.designflow.alias    import Alias
from coriolis.designflow.clean    import Clean
PnR.textMode  = True


topName ="counter"

from doDesign  import scriptMain

ruleYosys = Yosys   .mkRule( 'yosys', f'{topName}.v' )
ruleB2V   = Blif2Vst.mkRule( 'b2v'  , [ f'{topName}.vst' ]
                                    , [ruleYosys]
                                    , flags=0 )
rulePnR   = PnR     .mkRule( 'pnr'  , [ f'{topName}_cts_r.gds'
                                      , f'{topName}_cts_r.spi'
                                      , f'{topName}_cts_r.vst' ]
                                    , [ruleYosys]
                                    , scriptMain )
ruleCgt   = PnR     .mkRule( 'cgt' )
staLayout = rulePnR.file_target( 2 )
ruleSTA     = STA    .mkRule( 'sta'    , staLayout )
ruleXTas    = XTas   .mkRule( 'xtas'   , ruleSTA.file_target(0) )
ruleGds   = Alias   .mkRule( 'gds', [rulePnR] )
ruleClean = Clean   .mkRule()
