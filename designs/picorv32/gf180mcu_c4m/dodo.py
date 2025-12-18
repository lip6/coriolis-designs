
import os
from   doit              import get_var
from   coriolis          import Cfg
from   coriolis.helpers  import overlay
from   pdks.gf180mcu_c4m import setup

def userSettings ():
    with overlay.CfgCache(priority=Cfg.Parameter.Priority.UserFile) as cfg:
        cfg.misc.catchCore     = False
        cfg.misc.info          = False
        cfg.misc.paranoid      = False
        cfg.misc.bug           = False
        cfg.misc.logMode       = False
        cfg.misc.verboseLevel1 = True
        cfg.misc.verboseLevel2 = True

userSettings()
setup( )

DOIT_CONFIG = { 'verbosity' : 2 }

from coriolis                     import CRL
from coriolis.designflow.task     import Tasks
from coriolis.designflow.pnr      import PnR
from coriolis.designflow.yosys    import Yosys
from coriolis.designflow.blif2vst import Blif2Vst
from coriolis.designflow.tasyagle import TasYagle, STA, XTas
from coriolis.designflow.copy     import Copy
from coriolis.designflow.alias    import Alias
from coriolis.designflow.clean    import Clean
from coriolis.designflow.klayout  import Klayout, ShowDRC
from pdks.gf180mcu.designflow.drc import DRC
import doDesign

reuseBlif          = get_var( 'reuse-blif', None )
PnR.textMode       = True
pnrSuffix          = '_cts_r'
topName            = 'picorv32'
doDesign.buildChip = False

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
               , 'picorv32_cts.vst'
               , 'picorv32_cts.spi'
               , 'picorv32.spi'
               ]
else:
    pnrFiles = [ 'picorv32_cts_r.gds'
               , 'picorv32_cts_r.spi'
               , 'picorv32_cts_r.vst'
               ]

if reuseBlif:
    ruleYosys = Copy.mkRule( 'yosys', 'picorv32.blif', './non_generateds/picorv32.{}.blif'.format( reuseBlif ))
else:
    ruleYosys = Yosys.mkRule( 'yosys', 'picorv32.v' )
rulePnR     = PnR     .mkRule( 'pnr'     , pnrFiles, [ruleYosys], doDesign.scriptMain )
staLayout = rulePnR.file_target( 2 )
ruleSTA     = STA     .mkRule( 'sta'     , staLayout )
ruleXTas    = XTas    .mkRule( 'xtas'    , ruleSTA.file_target(0) )
ruleGds     = Alias   .mkRule( 'gds'     , [rulePnR] )
ruleDRC     = DRC     .mkRule( 'drc'     , [rulePnR], DRC.GF180MCU_C|DRC.SHOW_ERRORS|DRC.ANTENNA )
ruleCgt     = PnR     .mkRule( 'cgt'     )   
ruleKlayout = Klayout .mkRule( 'klayout' )
ruleClean   = Clean   .mkRule()
