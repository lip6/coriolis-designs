#!/usr/bin/env python3

import sys
import os
import traceback
from   coriolis            import Cfg, CRL
from   coriolis.Hurricane  import DbU, Breakpoint
from   coriolis.helpers.io import ErrorMessage, WarningMessage, catch
from   coriolis.helpers    import loadUserSettings, setTraceLevel, trace, overlay, l, u, n
loadUserSettings()
from   coriolis                             import plugins
from   coriolis.plugins.block.block         import Block
from   coriolis.plugins.block.configuration import IoPin, GaugeConf
from   coriolis.plugins.block.spares        import Spares
from   coriolis.plugins.chip.configuration  import ChipConf
from   coriolis.plugins.chip.chip           import Chip
from   pdks.sky130_c4m.core2chip.sky130     import CoreToChip


af        = CRL.AllianceFramework.get()
buildChip = False
dft  = False
CoreName = 'counter'

def scriptMain ( **kw ):
    """The mandatory function to be called by Coriolis CGT/Unicorn."""
    global af, buildChip,dft,dft_std_cells,CoreName

    rvalue    = True
    gaugeName = None
    with overlay.CfgCache(priority=Cfg.Parameter.Priority.UserFile) as cfg:
        cfg.misc.catchCore              = False
        cfg.misc.info                   = False
        cfg.misc.paranoid               = False
        cfg.misc.bug                    = False
        cfg.misc.logMode                = True
        cfg.misc.verboseLevel1          = True
        cfg.misc.verboseLevel2          = True
        cfg.misc.minTraceLevel          = 16000
        cfg.misc.maxTraceLevel          = 17000

    try:
        #setTraceLevel( 550 )
        #Breakpoint.setStopLevel( 99 )
        cell, editor = plugins.kwParseMain( **kw )
        if buildChip:
            CoreName += '_harness'
        cell = CRL.Blif.load( CoreName )
        if editor:
            editor.setCell( cell ) 
            editor.setDbuMode( DbU.StringModePhysical )
        if buildChip:
            ioPinsSpec = [ ]
            ioPadsSpec = [ ]
        else:
            ioPadsSpec = [ ]
            ioPinsSpec = [ ]
        conf = ChipConf( cell, ioPins=ioPinsSpec, ioPads=ioPadsSpec ) 
        conf.cfg.misc.catchCore              = False
        conf.cfg.misc.minTraceLevel          = 12300
        conf.cfg.misc.maxTraceLevel          = 12400
        conf.cfg.misc.info                   = False
        conf.cfg.misc.paranoid               = False
        conf.cfg.misc.bug                    = False
        conf.cfg.misc.logMode                = True
        conf.cfg.misc.verboseLevel1          = True
        conf.cfg.misc.verboseLevel2          = True
       #conf.cfg.etesian.bloat               = 'Flexlib'
        conf.cfg.etesian.densityVariation    = 0.05
        conf.cfg.etesian.aspectRatio         = 1.0
       # etesian.spaceMargin is ignored if the coreSize is directly set.
        conf.cfg.etesian.spaceMargin         = 0.05
        conf.cfg.anabatic.globalIterations   = 10
        conf.cfg.anabatic.gcellAspectRatio   = 2.0
        conf.cfg.katana.maxFlatEdgeOverflow  = 200
        conf.cfg.katana.hTracksReservedMin   = 5
        conf.cfg.katana.vTracksReservedMin   = 6
        conf.cfg.katana.hTracksReservedLocal = 8
        conf.cfg.katana.vTracksReservedLocal = 9
        conf.cfg.katana.globalRipupLimit     = 7
        conf.cfg.katana.runRealignStage      = False
        conf.cfg.katana.dumpMeasures         = True
        conf.editor              = editor
        conf.ioPinsInTracks      = True
        conf.useSpares           = True
        conf.useClockTree        = True
        conf.useHFNS             = True
        conf.bColumns            = 2
        conf.bRows               = 2
        conf.chipName            = 'chip'
        conf.coreSize            = conf.computeCoreSize( 20*conf.sliceHeight, 1.0 )
        conf.chipSize            = ( u(2020.0), u(2060.0) )
        conf.coreToChipClass     = CoreToChip
        if buildChip:
            conf.useHTree( 'io_in_from_pad(37)', Spares.HEAVY_LEAF_LOAD )
            conf.useHTree( 'io_in_from_pad(35)' )
        else:
            conf.useHTree( 'clk', Spares.HEAVY_LEAF_LOAD )
        #conf.useHTree( 'core.subckt_0_cpu.abc_11829_new_n340' )
        if buildChip:
            chipBuilder = Chip( conf )
            chipBuilder.doChipNetlist()
            chipBuilder.doChipFloorplan()
            if editor:
                editor.setCell( conf.chip )
            rvalue = chipBuilder.doPnR()
            chipBuilder.save()
        else:
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
