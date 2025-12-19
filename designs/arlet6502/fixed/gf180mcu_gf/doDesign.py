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
    global af, buildChip

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

    rvalue = True
    try:
        #setTraceLevel( 550 )
        #Breakpoint.setStopLevel( 100 )
        cell, editor = plugins.kwParseMain( **kw )
        cell = CRL.Blif.load( 'arlet6502' )
        if editor:
            editor.setCell( cell ) 
            editor.setDbuMode( DbU.StringModePhysical )
        ioPadsSpec = []
        ioPinsSpec = [ (IoPin.WEST |IoPin.A_BEGIN, 'di({})'  ,    16, 16,  8)
                     , (IoPin.WEST |IoPin.A_BEGIN, 'do({})'  , 14*16, 16,  8)
                     , (IoPin.EAST |IoPin.A_BEGIN, 'a({})'   ,    16, 16, 16)
                     , (IoPin.NORTH|IoPin.A_BEGIN, 'clk'     , 10*16,  0 , 1)
                     , (IoPin.NORTH|IoPin.A_BEGIN, 'irq'     , 11*16,  0 , 1)
                     , (IoPin.NORTH|IoPin.A_BEGIN, 'nmi'     , 12*16,  0 , 1)
                     , (IoPin.NORTH|IoPin.A_BEGIN, 'rdy'     , 13*16,  0 , 1)
                     , (IoPin.NORTH|IoPin.A_BEGIN, 'we'      , 14*16,  0 , 1)
                     , (IoPin.NORTH|IoPin.A_BEGIN, 'reset'   , 15*16,  0 , 1)
                     ]
        print(ioPinsSpec)
        conf = ChipConf( cell, ioPins=ioPinsSpec, ioPads=ioPadsSpec ) 
        conf.cfg.etesian.bloat               = 'disabled'
       #conf.cfg.etesian.bloat               = 'nsxlib'
        conf.cfg.etesian.densityVariation    = 0.05
        conf.cfg.etesian.aspectRatio         = 2.0
       # etesian.spaceMargin is ignored if the coreSize is directly set.
       #conf.cfg.etesian.spaceMargin         = 0.10
       #conf.cfg.anabatic.searchHalo         = 2
       #conf.cfg.anabatic.globalIterations   = 6
        conf.cfg.anabatic.gcellAspectRatio   = 2.0
       #conf.cfg.katana.hTracksReservedLocal = 7
        conf.cfg.katana.vTracksReservedLocal = 8
       #conf.cfg.katana.hTracksReservedMin   = 5
       #conf.cfg.katana.vTracksReservedMin   = 6
        conf.cfg.katana.trackFill            = 0
        conf.cfg.katana.runRealignStage      = False
        conf.cfg.block.spareSide             = 8*conf.sliceHeight
        conf.coreToChipClass     = CoreToChip
        conf.editor              = editor
        conf.ioPinsInTracks      = True
        conf.useSpares           = True
        conf.useHFNS             = True
        conf.bColumns            = 2
        conf.bRows               = 2
        conf.chipName            = 'chip'
        conf.coreSize            = conf.computeCoreSize( 45*conf.sliceHeight, 1.0 )
        conf.chipSize            = ( 350*conf.sliceHeight, 350*conf.sliceHeight )
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
            conf.useHTree( 'reset' )
            blockBuilder = Block( conf )
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
