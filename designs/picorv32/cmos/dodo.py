
import os
from   doit                        import get_var
from   coriolis                    import Cfg
from   coriolis.helpers            import overlay
from   coriolis.designflow.technos import setupCMOS


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
setupCMOS()

DOIT_CONFIG = { 'verbosity' : 2 }

from coriolis                     import CRL
from coriolis.designflow.task     import Tasks
from coriolis.designflow.pnr      import PnR
from coriolis.designflow.yosys    import Yosys
from coriolis.designflow.blif2vst import Blif2Vst
from coriolis.designflow.cougar   import Cougar
from coriolis.designflow.lvx      import Lvx 
from coriolis.designflow.druc     import Druc
from coriolis.designflow.tasyagle import TasYagle, STA, XTas
from coriolis.designflow.copy     import Copy
from coriolis.designflow.alias    import Alias
from coriolis.designflow.clean    import Clean
from coriolis.designflow.klayout  import Klayout, ShowDRC
import doDesign

reuseBlif          = get_var( 'reuse-blif', None )
PnR.textMode       = True
pnrSuffix          = '_cts_r'
topName            = 'picorv32'
doDesign.buildChip = False
#drcFlags           = DRC.SHOW_ERRORS
drcFlags           = 0

if doDesign.buildChip:
    pnrFiles = [ 'chip_r.ap'
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
               , 'picorv32.vst'
               , 'picorv32.spi'
               ]
else:
    pnrFiles = [ 'picorv32_cts_r.ap'
               , 'picorv32_cts_r.vst'
               , 'picorv32_cts_r.spi'
               ]

if reuseBlif:
    ruleYosys = Copy.mkRule( 'yosys', 'picorv32.blif', './non_generateds/picorv32.{}.blif'.format( reuseBlif ))
else:
    ruleYosys = Yosys.mkRule( 'yosys', 'picorv32.v' )
rulePnR     = PnR     .mkRule( 'pnr'     , pnrFiles, [ruleYosys], doDesign.scriptMain )
ruleCgt     = PnR     .mkRule( 'cgt'     )   
ruleKlayout = Klayout .mkRule( 'klayout' )
ruleCougar  = Cougar  .mkRule( 'cougar'
                             , 'arlet6502_cts_r_ext.al'
                             , [rulePnR]
                             , flags=Cougar.Verbose|Cougar.Flatten )
ruleLvx     = Lvx     .mkRule( 'lvx'
                             , [ rulePnR.file_target(1)
                               , ruleCougar.file_target(0) ]
                             , flags=Lvx.Flatten )
ruleDruc    = Druc    .mkRule( 'druc', [rulePnR], flags=0 )
ruleClean   = Clean   .mkRule()
