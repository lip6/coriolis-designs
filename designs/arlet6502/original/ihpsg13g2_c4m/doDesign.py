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
        cell = af.getCell( 'arlet6502', CRL.Catalog.State.Logical )
        if not cell:
            cell = CRL.Blif.load( 'arlet6502' )
        if editor:
            editor.setCell( cell ) 
            editor.setDbuMode( DbU.StringModePhysical )
        ioPadsSpec = [ (IoPin.WEST , None, 'di_0'       , 'di(0)'  , 'di(0)'  )
                     , (IoPin.WEST , None, 'di_1'       , 'di(1)'  , 'di(1)'  )
                     , (IoPin.WEST , None, 'di_2'       , 'di(2)'  , 'di(2)'  )
                     , (IoPin.WEST , None, 'di_3'       , 'di(3)'  , 'di(3)'  )
                     , (IoPin.WEST , None, 'allpower_0' , 'iovdd'  , 'vdd'    )
                     , (IoPin.WEST , None, 'allground_0', 'iovss'  , 'vss'    )
                     , (IoPin.WEST , None, 'di_4'       , 'di(4)'  , 'di(4)'  )
                     , (IoPin.WEST , None, 'di_5'       , 'di(5)'  , 'di(5)'  )
                     , (IoPin.WEST , None, 'di_6'       , 'di(6)'  , 'di(6)'  )
                     , (IoPin.WEST , None, 'di_7'       , 'di(7)'  , 'di(7)'  )

                     , (IoPin.SOUTH, None, 'do_0'       , 'do(0)'  , 'do(0)'  )
                     , (IoPin.SOUTH, None, 'do_1'       , 'do(1)'  , 'do(1)'  )
                     , (IoPin.SOUTH, None, 'do_2'       , 'do(2)'  , 'do(2)'  )
                     , (IoPin.SOUTH, None, 'do_3'       , 'do(3)'  , 'do(3)'  )
                     , (IoPin.SOUTH, None, 'allpower_1' , 'iovdd'  , 'vdd'    )
                     , (IoPin.SOUTH, None, 'allground_1', 'iovss'  , 'vss'    )
                     , (IoPin.SOUTH, None, 'do_4'       , 'do(4)'  , 'do(4)'  )
                     , (IoPin.SOUTH, None, 'do_5'       , 'do(5)'  , 'do(5)'  )
                     , (IoPin.SOUTH, None, 'do_6'       , 'do(6)'  , 'do(6)'  )
                     , (IoPin.SOUTH, None, 'do_7'       , 'do(7)'  , 'do(7)'  )
                     , (IoPin.SOUTH, None, 'a_0'        , 'a(0)'   , 'a(0)'   )
                     , (IoPin.SOUTH, None, 'a_1'        , 'a(1)'   , 'a(1)'   )

                     , (IoPin.EAST , None, 'a_2'        , 'a(2)'   , 'a(2)'   )
                     , (IoPin.EAST , None, 'a_3'        , 'a(3)'   , 'a(3)'   )
                     , (IoPin.EAST , None, 'a_4'        , 'a(4)'   , 'a(4)'   )
                     , (IoPin.EAST , None, 'a_5'        , 'a(5)'   , 'a(5)'   )
                     , (IoPin.EAST , None, 'a_6'        , 'a(6)'   , 'a(6)'   )
                     , (IoPin.EAST , None, 'allpower_2' , 'iovdd'  , 'vdd'    )
                     , (IoPin.EAST , None, 'allground_2', 'iovss'  , 'vss'    )
                     , (IoPin.EAST , None, 'a_7'        , 'a(7)'   , 'a(7)'   )
                     , (IoPin.EAST , None, 'a_8'        , 'a(8)'   , 'a(8)'   )
                     , (IoPin.EAST , None, 'a_9'        , 'a(9)'   , 'a(9)'   )
                     , (IoPin.EAST , None, 'a_10'       , 'a(10)'  , 'a(10)'  )
                     , (IoPin.EAST , None, 'a_11'       , 'a(11)'  , 'a(11)'  )
                     , (IoPin.EAST , None, 'a_12'       , 'a(12)'  , 'a(12)'  )
                     , (IoPin.EAST , None, 'a_13'       , 'a(13)'  , 'a(13)'  )

                     , (IoPin.NORTH, None, 'irq'        , 'irq'    , 'irq'    )
                     , (IoPin.NORTH, None, 'nmi'        , 'nmi'    , 'nmi'    )
                     , (IoPin.NORTH, None, 'rdy'        , 'rdy'    , 'rdy'    )
                     , (IoPin.NORTH, None, 'clk'        , 'clk'    , 'clk'    )
                     , (IoPin.NORTH, None, 'allpower_3' , 'iovdd'  , 'vdd'    )
                     , (IoPin.NORTH, None, 'allground_3', 'iovss'  , 'vss'    )
                     , (IoPin.NORTH, None, 'reset'      , 'reset'  , 'reset'  )
                     , (IoPin.NORTH, None, 'we'         , 'we'     , 'we'     )
                     , (IoPin.NORTH, None, 'a_14'       , 'a(14)'  , 'a(14)'  )
                     , (IoPin.NORTH, None, 'a_15'       , 'a(15)'  , 'a(15)'  )
                     ]
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
        conf.cfg.etesian.aspectRatio         = 1.5
       # etesian.spaceMargin is ignored if the coreSize is directly set.
       #conf.cfg.etesian.spaceMargin         = 0.10
       #conf.cfg.anabatic.searchHalo         = 2
        conf.cfg.anabatic.globalIterations   = 20
        conf.cfg.katana.maxFlatEdgeOverflow  = 30
        conf.cfg.katana.hTracksReservedLocal = 15
        conf.cfg.katana.vTracksReservedLocal = 20
        conf.cfg.katana.hTracksReservedMin   = 7
        conf.cfg.katana.vTracksReservedMin   = 12
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
        conf.coreSize            = conf.computeCoreSize( 36*conf.sliceHeight, 1.0 )
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
