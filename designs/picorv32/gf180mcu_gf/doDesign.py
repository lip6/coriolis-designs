#!/usr/bin/env python3

import sys
import traceback
from   coriolis.Hurricane  import DbU, Breakpoint, PythonAttributes
from   coriolis            import CRL, Cfg
from   coriolis.helpers    import loadUserSettings, setTraceLevel, trace, overlay, l, u, n
from   coriolis.helpers.io import ErrorMessage, WarningMessage, catch
loadUserSettings()
from   coriolis            import plugins
from   coriolis.plugins.block.block         import Block
from   coriolis.plugins.block.configuration import IoPin, GaugeConf
from   coriolis.plugins.block.spares        import Spares
from   pdks.gf180mcu.core2chip.gf180mcu     import CoreToChip
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
        cfg.misc.logMode                = True
        cfg.misc.verboseLevel1          = True
        cfg.misc.verboseLevel2          = True
        cfg.misc.minTraceLevel          = 15900
        cfg.misc.maxTraceLevel          = 16000
        #cfg.block.upperEastWestPins     = None
        #print( 'cfg.block.upperEastWestPins={}'.format( cfg.block.upperEastWestPins ))

    global af, buildChip
    hpitch       = 0
    gaugeName    = Cfg.getParamString('anabatic.routingGauge').asString()
    routingGauge = af.getRoutingGauge( gaugeName )
    for layerGauge in routingGauge.getLayerGauges():
        if layerGauge.getType() in [ CRL.RoutingLayerGauge.PinOnly
                                   , CRL.RoutingLayerGauge.Unusable
                                   , CRL.RoutingLayerGauge.BottomPowerSupply ]:
            continue
        if layerGauge.getDirection() == CRL.RoutingLayerGauge.Horizontal:
            hpitch = layerGauge.getPitch()
            break
    sliceHeight = af.getCellGauge().getSliceHeight()

    rvalue = True
    try:
        #setTraceLevel( 550 )
        #Breakpoint.setStopLevel( 100 )
        cell, editor = plugins.kwParseMain( **kw )
        cell = CRL.Blif.load( 'picorv32' )
        if editor:
            editor.setCell( cell ) 
            editor.setDbuMode( DbU.StringModePhysical )
        ioPadsSpec = []
        vspace     = 6
        hspace     = 5
        ioPinsSpec = [ (IoPin.NORTH|IoPin.A_BEGIN, 'trace_data({})'  ,     vspace, vspace, range(0, 36))
                         , (IoPin.NORTH|IoPin.A_BEGIN, 'mem_la_wdata({})',  38*vspace, vspace, range(0, 32))
                         , (IoPin.NORTH|IoPin.A_BEGIN, 'mem_la_addr({})' ,  70*vspace, vspace, range(0, 32))
                         , (IoPin.SOUTH|IoPin.A_BEGIN, 'eoi({})'         ,     vspace, vspace, range(0, 32))
                         , (IoPin.SOUTH|IoPin.A_BEGIN, 'mem_addr({})'    ,  33*vspace, vspace, range(0, 32))
                         , (IoPin.SOUTH|IoPin.A_BEGIN, 'mem_wdata({})'   ,  65*vspace, vspace, range(0, 32))
                         , (IoPin.SOUTH|IoPin.A_BEGIN, 'mem_rdata({})'   ,  97*vspace, vspace, range(0,  4))
                         , (IoPin.EAST |IoPin.A_BEGIN, 'mem_rdata({})'   ,     hspace+5, hspace, range(4, 32))
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
                         , (IoPin.WEST |IoPin.A_BEGIN, 'pcpi_ready'      , 141*hspace-6, 0, 1)]

        print(ioPinsSpec)
        designConf = ChipConf( cell, ioPins=ioPinsSpec, ioPads=ioPadsSpec ) 
        designConf.cfg.etesian.bloat               = 'disabled'
       #designConf.cfg.etesian.bloat               = 'nsxlib'
        designConf.cfg.etesian.densityVariation    = 0.05
        designConf.cfg.etesian.aspectRatio         = 2.0
       # etesian.spaceMargin is ignored if the coreSize is directly set.
       #designConf.cfg.etesian.spaceMargin         = 0.10
       #designConf.cfg.anabatic.searchHalo         = 2
       #designConf.cfg.anabatic.globalIterations   = 6
        designConf.cfg.anabatic.gcellAspectRatio   = 2.0
       #designConf.cfg.katana.hTracksReservedLocal = 7
        designConf.cfg.katana.vTracksReservedLocal = 8
       #designConf.cfg.katana.hTracksReservedMin   = 5
       #designConf.cfg.katana.vTracksReservedMin   = 6
        designConf.cfg.katana.trackFill            = 0
        designConf.cfg.katana.runRealignStage      = False
        designConf.cfg.block.spareSide             = 8*sliceHeight
        designConf.coreToChipClass     = CoreToChip
        designConf.editor              = editor
        designConf.ioPinsInTracks      = True
        designConf.useSpares           = True
        designConf.useHFNS             = True
        designConf.bColumns            = 2
        designConf.bRows               = 2
        designConf.chipName            = 'chip'
        designConf.coreSize            = designConf.computeCoreSize( 122*designConf.sliceHeight, 1.0 )
        designConf.chipSize            = ( 350*sliceHeight, 350*sliceHeight )
        if buildChip:
            designConf.useHTree( 'clk_from_pad', Spares.HEAVY_LEAF_LOAD )
            designConf.useHTree( 'reset_from_pad' )
            chipBuilder = Chip( designConf )
            chipBuilder.doChipNetlist()
            chipBuilder.doChipFloorplan()
            rvalue = chipBuilder.doPnR()
            chipBuilder.save()
        else:
            designConf.useHTree( 'clk', Spares.HEAVY_LEAF_LOAD )
            designConf.useHTree( 'resetn' )
            blockBuilder = Block( designConf )
            rvalue = blockBuilder.doPnR()
            blockBuilder.save()
    except Exception as e:
        catch( e )
        rvalue = False
    sys.stdout.flush()
    sys.stderr.flush()
    #return rvalue
    return True


if __name__ == '__main__':
    rvalue = scriptMain()
    shellRValue = 0 if rvalue else 1
    sys.exit( shellRValue )
