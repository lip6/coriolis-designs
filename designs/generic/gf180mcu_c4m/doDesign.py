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
dft  = False
CoreName = 'counter'


def scriptMain ( **kw ):
    global af, buildChip, dft,dft_std_cells,CoreName


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

    rvalue = True
    try:
        #setTraceLevel( 550 )
        #for cell in af.getAllianceLibrary(1).getLibrary().getCells():
        #    print( '"{}" {}'.format(cell.getName(),cell) )
        #Breakpoint.setStopLevel( 100 )
        cell, editor = plugins.kwParseMain( **kw )
        cell = CRL.Blif.load( CoreName )
        if editor:
            editor.setCell( cell ) 
            editor.setDbuMode( DbU.StringModePhysical )
        ioPadsSpec = [ ]
        ioPinsSpec = [ ]
       #Explicit placement of dft connectors is supported. If not defined,
       #they are automatically added (optimized)
        conf = ChipConf( cell, ioPins=ioPinsSpec, ioPads=ioPadsSpec ) 
        conf.cfg.etesian.bloat               = 'disabled'
       #conf.cfg.etesian.bloat               = 'nsxlib'
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
       #conf.cfg.chip.supplyRailWidth        = l(250.0)
       #conf.cfg.chip.supplyRailPitch        = l(450.0)
        conf.editor              = editor
        conf.ioPinsInTracks      = True
        conf.useSpares           = True
        conf.useHFNS             = False
        conf.bColumns            = 2
        conf.bRows               = 2
        conf.chipName            = 'chip'
        conf.coreToChipClass     = CoreToChip
        conf.coreSize            = conf.computeCoreSize( 40*conf.sliceHeight, 1.0 )
        conf.chipSize            = ( 140*conf.sliceHeight, 140*conf.sliceHeight )
        if buildChip:
            conf.useHTree( 'clk_from_pad', Spares.HEAVY_LEAF_LOAD )
            chipBuilder = Chip( conf )
            chipBuilder.doChipNetlist()
            chipBuilder.doChipFloorplan()
            rvalue = chipBuilder.doPnR()
            chipBuilder.save()
        else:
            conf.useHTree( 'clk', Spares.HEAVY_LEAF_LOAD )
            blockBuilder = Block( conf )
            if dft:
             if dft_std_cells is not None:
                conf.dft_std_cells = dft_std_cells
             rvalue = blockBuilder.doPnRDFT()
            else:
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
