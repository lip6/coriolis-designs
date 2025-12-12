import sys
import pathlib
DOIT_CONFIG = { 'verbosity' : 2 }
from coriolis                               import CRL
from coriolis.designflow.task               import ShellEnv, Tasks
from coriolis.designflow.vasy               import Vasy
from coriolis.designflow.iverilog           import Iverilog
from coriolis.designflow.gtkwave            import GtkWave
from coriolis.designflow.yosys              import Yosys
from coriolis.designflow.blif2vst           import Blif2Vst
from coriolis.designflow.klayout            import Klayout
from coriolis.designflow.pnr                import PnR
from coriolis.designflow.s2r                import S2R
from coriolis.designflow.lvx                import Lvx
from coriolis.designflow.cougar             import Cougar
from coriolis.designflow.druc               import Druc
from coriolis.designflow.tasyagle           import TasYagle, STA, XTas
from coriolis.designflow.clean              import Clean
from coriolis.designflow.klayout            import DRC
PnR.textMode = True
from pdks.nsx2    import setup
setup ()

import doDesign

topName = 'counter'

#DRC.setDrcRules( kdrcRules )

ruleClean   = Clean  .mkRule( [ 'lefRWarning.log', 'cgt.log' ] )

ruleCgt     = PnR.mkRule( 'cgt' )

ruleYosys = Yosys   .mkRule( 'yosys', topName+'.v' )

ruleB2V   = Blif2Vst.mkRule( 'b2v'  , [ 'counter.vst' ]
                                    , [ruleYosys]
                                    , flags=0 )
rulePnR = PnR.mkRule( 'pnr', [topName+'_cts_r.ap'
                            , topName+'_cts_r.vst'
                            , topName+'_cts_r.spi' ]
                            , [ruleYosys]
                            , doDesign.scriptMain
                            , topName=topName )

ruleVasy  = Vasy.mkRule( 'vasy', topName+'_cts_r.v'
                               , rulePnR.file_target(1)
                               , Vasy.Overwrite|Vasy.RemovePowerSupplies )

ruleIverilog = Iverilog.mkRule( 'iverilog', [ ruleVasy, 'tb_counter.v' ] )





ruleDruc   = Druc.mkRule( 'druc'  , [rulePnR], flags=0 )


from pdks.nsx2    import setup_techno
setup_techno ('sky130')

S2R.flags =  S2R.NoReplaceBlackboxes 
ruleS2R= S2R.mkRule('s2r', [topName+'_cts_r.gds'],[rulePnR],S2R.flags)

ruleCougar = Cougar.mkRule( 'cougar', topName+'_cts_r_ext.vst', [rulePnR], flags=Cougar.Verbose )

ruleLvx    = Lvx.mkRule( 'lvx', [ rulePnR.file_target(1)
                                , ruleCougar.file_target(0) ]
                                , flags=Lvx.Flatten )

ruleCougarSpi = Cougar.mkRule( 'cougarSpi', topName+'_ext.spi'
							              , [rulePnR]
							              , Cougar.Transistor | Cougar.Verbose )

TasYagle.ClockName = 'clk'
TasYagle.VddSupply     = 1.8  # (5v for GF180Mcu)
staLayout = ruleCougarSpi.file_target( 0 )
ruleSTA     = STA    .mkRule( 'sta'    , staLayout )

