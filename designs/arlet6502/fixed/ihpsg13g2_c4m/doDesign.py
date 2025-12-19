#!/usr/bin/env python3

import sys
import traceback
from   coriolis.Hurricane  import DbU, Breakpoint, PythonAttributes, Instance, Transformation
from   coriolis            import CRL, Cfg
from   coriolis.helpers    import loadUserSettings, setTraceLevel, trace, overlay, l, u, n
from   coriolis.helpers.io import ErrorMessage, WarningMessage, catch
from   coriolis            import plugins
from   coriolis.plugins.block.block          import Block
from   coriolis.plugins.block.configuration  import IoPin, GaugeConf
from   coriolis.plugins.block.spares         import Spares
from   pdks.ihpsg13g2_c4m.core2chip.sg13g2io import CoreToChip
from   coriolis.plugins.chip.configuration   import ChipConf
from   coriolis.plugins.chip.chip            import Chip


af        = CRL.AllianceFramework.get()
buildChip = False


def scriptMain ( **kw ):
    """The mandatory function to be called by Coriolis CGT/Unicorn."""
    global af, buildChip
    gaugeName = None
    with overlay.CfgCache(priority=Cfg.Parameter.Priority.UserFile) as cfg:
        cfg.misc.catchCore     = False
        cfg.misc.info          = False
        cfg.misc.paranoid      = False
        cfg.misc.bug           = False
        cfg.misc.logMode       = True
        cfg.misc.verboseLevel1 = True
        cfg.misc.verboseLevel2 = True
        cfg.misc.minTraceLevel = 16000
        cfg.misc.maxTraceLevel = 17000

    rvalue = True
    try:
        #setTraceLevel( 550 )
        #for cell in af.getAllianceLibrary(1).getLibrary().getCells():
        #    print( '"{}" {}'.format(cell.getName(),cell) )
        #Breakpoint.setStopLevel( 100 )
        cell, editor = plugins.kwParseMain( **kw )
        cell = CRL.Blif.load( 'arlet6502' )
        if editor:
            editor.setCell( cell ) 
            editor.setDbuMode( DbU.StringModePhysical )
        ioPadsSpec = []
        pinSpacing = 10
        ioPinsSpec = [ (IoPin.WEST |IoPin.A_BEGIN, 'di({})'  ,    pinSpacing, pinSpacing,  8)
                     , (IoPin.WEST |IoPin.A_BEGIN, 'do({})'  , 14*pinSpacing, pinSpacing,  8)
                     , (IoPin.EAST |IoPin.A_BEGIN, 'a({})'   ,    pinSpacing, pinSpacing, 16)
                     , (IoPin.NORTH|IoPin.A_BEGIN, 'clk'     , 10*pinSpacing,          0 , 1)
                     , (IoPin.NORTH|IoPin.A_BEGIN, 'irq'     , 11*pinSpacing,          0 , 1)
                     , (IoPin.NORTH|IoPin.A_BEGIN, 'nmi'     , 12*pinSpacing,          0 , 1)
                     , (IoPin.NORTH|IoPin.A_BEGIN, 'rdy'     , 13*pinSpacing,          0 , 1)
                     , (IoPin.NORTH|IoPin.A_BEGIN, 'we'      , 14*pinSpacing,          0 , 1)
                     , (IoPin.NORTH|IoPin.A_BEGIN, 'reset'   , 15*pinSpacing,          0 , 1)
                     ]
        conf = ChipConf( cell, ioPins=ioPinsSpec, ioPads=ioPadsSpec ) 
        conf.cfg.tramontana.mergeSupplies    = True
        conf.cfg.etesian.bloat               = 'disabled'
       #conf.cfg.etesian.bloat               = 'nsxlib'
        conf.cfg.etesian.densityVariation    = 0.05
        conf.cfg.etesian.aspectRatio         = 1.0
       # etesian.spaceMargin is ignored if the coreSize is directly set.
       #conf.cfg.etesian.spaceMargin         = 0.10
       #conf.cfg.anabatic.searchHalo         = 2
        conf.cfg.anabatic.globalIterations   = 6
        conf.cfg.katana.hTracksReservedLocal = 15
        conf.cfg.katana.vTracksReservedLocal = 15
        conf.cfg.katana.hTracksReservedMin   = 6
        conf.cfg.katana.vTracksReservedMin   = 6
        conf.cfg.katana.trackFill            = 0
        conf.cfg.katana.runRealignStage      = False
        conf.editor              = editor
        conf.ioPinsInTracks      = True
        conf.useSpares           = True
        conf.useHFNS             = True
        conf.bColumns            = 2
        conf.bRows               = 2
        conf.chipName            = 'chip'
        conf.coreToChipClass     = CoreToChip
        conf.coreSize            = conf.computeCoreSize( 35*conf.sliceHeight, 1.0 )
        conf.chipSize            = ( u(16*85 + 2*260.0 + 40.0), u(18*85 + 2*260.0) )
        if buildChip:
            conf.useHTree( 'clk_from_pad', Spares.HEAVY_LEAF_LOAD )
            conf.useHTree( 'reset_from_pad' )
            chipBuilder = Chip( conf )
            chipBuilder.doChipNetlist()
            chipBuilder.doChipFloorplan()
            rvalue = chipBuilder.doPnR()
            CRL.Gds.load( chipBuilder.conf.chip.getLibrary()
                        , 'chip_r_seal.gds'
                        , CRL.Gds.Layer_0_IsBoundary )
            with overlay.UpdateSession():
                chipCell = chipBuilder.conf.chip
                sealCell = chipBuilder.conf.chip.getLibrary().getCell( 'sealring_top' )
                chipAb = chipCell.getAbutmentBox()
                sealAb = sealCell.getAbutmentBox()
                sealX  = (chipAb.getWidth () - sealAb.getWidth ()) // 2
                sealY  = (chipAb.getHeight() - sealAb.getHeight()) // 2
                Instance.create( chipCell
                               , 'sealring'
                               , sealCell
                               , Transformation( sealX, sealY, Transformation.Orientation.ID )
                               , Instance.PlacementStatus.FIXED
                               )
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
    return rvalue


if __name__ == '__main__':
    rvalue = scriptMain()
    shellRValue = 0 if rvalue else 1
    sys.exit( shellRValue )
