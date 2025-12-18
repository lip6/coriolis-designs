#!/usr/bin/env python3

import sys
import traceback
from   coriolis.Hurricane  import DbU, Breakpoint, PythonAttributes
from   coriolis            import CRL, Cfg
from   coriolis.helpers    import loadUserSettings, setTraceLevel, trace, overlay, l, u, n
from   coriolis.helpers.io import ErrorMessage, WarningMessage, catch
from   coriolis            import plugins
from   coriolis.plugins.block.block         import Block
from   coriolis.plugins.block.configuration import IoPin, GaugeConf
from   coriolis.plugins.block.spares        import Spares
from   pdks.gf180mcu_c4m.core2chip.gf180mcu import CoreToChip
from   coriolis.plugins.chip.configuration  import ChipConf
from   coriolis.plugins.chip.chip           import Chip


af        = CRL.AllianceFramework.get()
buildChip = False


def scriptMain ( **kw ):
    """The mandatory function to be called by Coriolis CGT/Unicorn."""
    with overlay.CfgCache(priority=Cfg.Parameter.Priority.UserFile) as cfg:
        cfg.misc.catchCore              = False
        cfg.misc.info                   = False
        cfg.misc.paranoid               = False
        cfg.misc.bug                    = False
        cfg.misc.logMode                = False
        cfg.misc.verboseLevel1          = True
        cfg.misc.verboseLevel2          = False
        cfg.misc.minTraceLevel          = 16000
        cfg.misc.maxTraceLevel          = 17000

    global af, buildChip

    rvalue = True
    try:
        #setTraceLevel( 550 )
        #for cell in af.getAllianceLibrary(1).getLibrary().getCells():
        #    print( '"{}" {}'.format(cell.getName(),cell) )
        #Breakpoint.setStopLevel( 100 )
        cell, editor = plugins.kwParseMain( **kw )
        cell = CRL.Blif.load( 'picorv32' )
        if editor:
            editor.setCell( cell ) 
            editor.setDbuMode( DbU.StringModePhysical )
        ioPadsSpec = [ (IoPin.WEST , None, 'di_0'       , 'DI(0)'  , 'DI(0)'  )
                     , (IoPin.WEST , None, 'di_1'       , 'DI(1)'  , 'DI(1)'  )
                     , (IoPin.WEST , None, 'di_2'       , 'DI(2)'  , 'DI(2)'  )
                     , (IoPin.WEST , None, 'di_3'       , 'DI(3)'  , 'DI(3)'  )
                     , (IoPin.WEST , None, 'allpower_0' , 'DVDD'   , 'vdd'    )
                     , (IoPin.WEST , None, 'allground_0', 'DVSS'   , 'vss'    )
                     , (IoPin.WEST , None, 'di_4'       , 'DI(4)'  , 'DI(4)'  )
                     , (IoPin.WEST , None, 'di_5'       , 'DI(5)'  , 'DI(5)'  )
                     , (IoPin.WEST , None, 'di_6'       , 'DI(6)'  , 'DI(6)'  )
                     , (IoPin.WEST , None, 'di_7'       , 'DI(7)'  , 'DI(7)'  )

                     , (IoPin.SOUTH, None, 'do_0'       , 'DO(0)'  , 'DO(0)'  )
                     , (IoPin.SOUTH, None, 'do_1'       , 'DO(1)'  , 'DO(1)'  )
                     , (IoPin.SOUTH, None, 'do_2'       , 'DO(2)'  , 'DO(2)'  )
                     , (IoPin.SOUTH, None, 'do_3'       , 'DO(3)'  , 'DO(3)'  )
                     , (IoPin.SOUTH, None, 'allpower_1' , 'DVDD'   , 'vdd'    )
                     , (IoPin.SOUTH, None, 'allground_1', 'DVSS'   , 'vss'    )
                     , (IoPin.SOUTH, None, 'do_4'       , 'DO(4)'  , 'DO(4)'  )
                     , (IoPin.SOUTH, None, 'do_5'       , 'DO(5)'  , 'DO(5)'  )
                     , (IoPin.SOUTH, None, 'do_6'       , 'DO(6)'  , 'DO(6)'  )
                     , (IoPin.SOUTH, None, 'do_7'       , 'DO(7)'  , 'DO(7)'  )
                     , (IoPin.SOUTH, None, 'a_0'        , 'A(0)'   , 'A(0)'   )
                     , (IoPin.SOUTH, None, 'a_1'        , 'A(1)'   , 'A(1)'   )

                     , (IoPin.EAST , None, 'a_2'        , 'A(2)'   , 'A(2)'   )
                     , (IoPin.EAST , None, 'a_3'        , 'A(3)'   , 'A(3)'   )
                     , (IoPin.EAST , None, 'a_4'        , 'A(4)'   , 'A(4)'   )
                     , (IoPin.EAST , None, 'a_5'        , 'A(5)'   , 'A(5)'   )
                     , (IoPin.EAST , None, 'a_6'        , 'A(6)'   , 'A(6)'   )
                     , (IoPin.EAST , None, 'allpower_2' , 'DVDD'   , 'vdd'    )
                     , (IoPin.EAST , None, 'allground_2', 'DVSS'   , 'vss'    )
                     , (IoPin.EAST , None, 'a_7'        , 'A(7)'   , 'A(7)'   )
                     , (IoPin.EAST , None, 'a_8'        , 'A(8)'   , 'A(8)'   )
                     , (IoPin.EAST , None, 'a_9'        , 'A(9)'   , 'A(9)'   )
                     , (IoPin.EAST , None, 'a_10'       , 'A(10)'  , 'A(10)'  )
                     , (IoPin.EAST , None, 'a_11'       , 'A(11)'  , 'A(11)'  )
                     , (IoPin.EAST , None, 'a_12'       , 'A(12)'  , 'A(12)'  )
                     , (IoPin.EAST , None, 'a_13'       , 'A(13)'  , 'A(13)'  )

                     , (IoPin.NORTH, None, 'irq'        , 'IRQ'    , 'IRQ'    )
                     , (IoPin.NORTH, None, 'nmi'        , 'NMI'    , 'NMI'    )
                     , (IoPin.NORTH, None, 'rdy'        , 'RDY'    , 'RDY'    )
                     , (IoPin.NORTH, None, 'clk'        , 'clk'    , 'clk'    )
                     , (IoPin.NORTH, None, 'allpower_3' , 'DVDD'   , 'vdd'    )
                     , (IoPin.NORTH, None, 'allground_3', 'DVSS'   , 'vss'    )
                     , (IoPin.NORTH, None, 'reset'      , 'reset'  , 'reset'  )
                     , (IoPin.NORTH, None, 'we'         , 'WE'     , 'WE'     )
                     , (IoPin.NORTH, None, 'a_14'       , 'a(14)'  , 'A(14)'  )
                     , (IoPin.NORTH, None, 'a_15'       , 'a(15)'  , 'A(15)'  )
                     ]
        vspace     = 6
        hspace     = 4
        ioPinsSpec = [ (IoPin.NORTH|IoPin.A_BEGIN, 'trace_data({})'  ,     vspace, vspace, range(0, 36))
                     , (IoPin.NORTH|IoPin.A_BEGIN, 'mem_la_wdata({})',  38*vspace, vspace, range(0, 32))
                     , (IoPin.NORTH|IoPin.A_BEGIN, 'mem_la_addr({})' ,  70*vspace, vspace, range(0, 32))
                     , (IoPin.SOUTH|IoPin.A_BEGIN, 'eoi({})'         ,     vspace, vspace, range(0, 32))
                     , (IoPin.SOUTH|IoPin.A_BEGIN, 'mem_addr({})'    ,  33*vspace, vspace, range(0, 32))
                     , (IoPin.SOUTH|IoPin.A_BEGIN, 'mem_wdata({})'   ,  65*vspace, vspace, range(0, 32))
                     , (IoPin.SOUTH|IoPin.A_BEGIN, 'mem_rdata({})'   ,  97*vspace, vspace, range(0,  4))
                     , (IoPin.EAST |IoPin.A_BEGIN, 'mem_rdata({})'   ,     hspace, hspace, range(4, 32))
                     , (IoPin.EAST |IoPin.A_BEGIN, 'irq({})'         ,  33*hspace, hspace, range(0, 32))
                     , (IoPin.EAST |IoPin.A_BEGIN, 'pcpi_insn({})'   ,  65*hspace, hspace, range(0, 32))
                     , (IoPin.EAST |IoPin.A_BEGIN, 'pcpi_rs1({})'    ,  97*hspace, hspace, range(0,  8))
                     , (IoPin.WEST |IoPin.A_BEGIN, 'pcpi_rs1({})'    ,     hspace, hspace, range(8, 32))
                     , (IoPin.WEST |IoPin.A_BEGIN, 'pcpi_rd({})'     ,  33*hspace, hspace, range(0, 32))
                     , (IoPin.WEST |IoPin.A_BEGIN, 'pcpi_rs2({})'    ,  97*hspace, hspace, range(8, 32))
                     , (IoPin.WEST |IoPin.A_BEGIN, 'mem_wstrb({})'   , 121*hspace, hspace, range(0,  4))
                     , (IoPin.WEST |IoPin.A_BEGIN, 'mem_la_wstrb({})', 125*hspace, hspace, range(0,  4))
                     , (IoPin.WEST |IoPin.A_BEGIN, 'mem_la_write'    , 129*hspace, 0, 1)
                     , (IoPin.WEST |IoPin.A_BEGIN, 'trap'            , 130*hspace, 0, 1)
                     , (IoPin.WEST |IoPin.A_BEGIN, 'resetn'          , 131*hspace, 0, 1)
                     , (IoPin.WEST |IoPin.A_BEGIN, 'mem_instr'       , 132*hspace, 0, 1)
                     , (IoPin.WEST |IoPin.A_BEGIN, 'mem_valid'       , 133*hspace, 0, 1)
                     , (IoPin.WEST |IoPin.A_BEGIN, 'mem_la_read'     , 134*hspace, 0, 1)
                     , (IoPin.WEST |IoPin.A_BEGIN, 'pcpi_wr'         , 135*hspace, 0, 1)
                     , (IoPin.WEST |IoPin.A_BEGIN, 'pcpi_wait'       , 136*hspace, 0, 1)
                     , (IoPin.WEST |IoPin.A_BEGIN, 'trace_valid'     , 137*hspace, 0, 1)
                     , (IoPin.WEST |IoPin.A_BEGIN, 'mem_ready'       , 138*hspace, 0, 1)
                     , (IoPin.WEST |IoPin.A_BEGIN, 'clk'             , 139*hspace, 0, 1)
                     , (IoPin.WEST |IoPin.A_BEGIN, 'pcpi_valid'      , 140*hspace, 0, 1)
                     , (IoPin.WEST |IoPin.A_BEGIN, 'pcpi_ready'      , 141*hspace, 0, 1)]
       #ioPinsSpec = []
        conf = ChipConf( cell, ioPins=ioPinsSpec, ioPads=ioPadsSpec ) 
        conf.cfg.etesian.bloat               = 'disabled'
        conf.cfg.etesian.densityVariation    = 0.05
        conf.cfg.etesian.aspectRatio         = 1.0
       # etesian.spaceMargin is ignored if the coreSize is directly set.
       #conf.cfg.etesian.spaceMargin         = 0.10
       #conf.cfg.anabatic.searchHalo         = 2
        conf.cfg.anabatic.globalIterations   = 6
        conf.cfg.katana.hTracksReservedLocal = 6
        conf.cfg.katana.vTracksReservedLocal = 3
        conf.cfg.katana.hTracksReservedMin   = 4
        conf.cfg.katana.vTracksReservedMin   = 5
        conf.cfg.katana.trackFill            = 0
        conf.cfg.katana.runRealignStage      = True
        conf.cfg.block.spareSide             = 16*conf.sliceHeight
        conf.editor              = editor
        conf.ioPinsInTracks      = True
        conf.useSpares           = True
        conf.useHFNS             = True
        conf.bColumns            = 2
        conf.bRows               = 2
        conf.chipName            = 'chip'
        conf.coreToChipClass     = CoreToChip
        conf.coreSize            = conf.computeCoreSize( 86*conf.sliceHeight, 1.0 )
        conf.chipSize            = ( 140*conf.sliceHeight, 140*conf.sliceHeight )
        if buildChip:
            conf.useHTree( 'clk_from_pad', Spares.HEAVY_LEAF_LOAD )
            conf.useHTree( 'reset_from_pad' )
            chipBuilder = Chip( conf )
            chipBuilder.doChipNetlist()
            chipBuilder.doChipFloorplan()
            rvalue = chipBuilder.doPnR()
            chipBuilder.save()
        else:
            conf.useHTree( 'clk', Spares.HEAVY_LEAF_LOAD )
            conf.useHTree( 'resetn' )
            blockBuilder = Block( conf )
            rvalue = blockBuilder.doPnR()
            blockBuilder.save()
    except Exception as e:
        catch( e )
        rvalue = False
    sys.stdout.flush()
    sys.stderr.flush()
    return rvalue


if __name__ == '__main__':
    rvalue = scriptMain()
    shellRValue = 0 if rvalue else 1
    sys.exit( shellRValue )
