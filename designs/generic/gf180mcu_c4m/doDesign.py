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
from   coriolis.designflow.connectors_placement                 import *


af        = CRL.AllianceFramework.get()
buildChip = False

CoreName = 'counter'
def get_signals_hurricane(entity):
# from coriolis.designflow.technos import setupSky130_c4m
# from coriolis import CRL
# setupSky130_c4m( '../../..', '../../../pdkmaster/C4M.Sky130' )
# af = CRL.AllianceFramework.get()
 cell_blif  = CRL.Blif.load(f'{entity}.blif')
 #get supply pins not used in placement
 supply_pins = [j.getName() for j in cell_blif.getSupplyNets()]
 vectors = {}
 for i in cell_blif.getExternalNets():
     #vector_name
     a=i.getName()
     vector = a.split('(')[0]
     if vector in vectors:
      #vector size
      vectors[vector][1] += 1
      #first bit of vector, it is 0 in most cases
      vectors[vector][2]=min(vectors[vector][2],int(a.split(')')[0].split('(')[1]))
     else:
         supply = False
         for s in supply_pins:
             if vector == s:
                 supply = True
         if supply == False:
             if '(' in a:
              bit = int(a.split(')')[0].split('(')[1])
             else: 
              bit = 0   
             vectors[vector] = [vector,1,bit]
 signals_sorted={}
 #In order to have a dictionnary with a number as key
 #usefull for sorting signals in other functions
 for i, key in enumerate(vectors):
  signals_sorted[i] = vectors[key]
 return signals_sorted
combinational =0



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
    hpitch       = 0
    gaugeName    = Cfg.getParamString('anabatic.routingGauge').asString()
    dico = get_signals_hurricane(CoreName)
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
        #for cell in af.getAllianceLibrary(1).getLibrary().getCells():
        #    print( '"{}" {}'.format(cell.getName(),cell) )
        #Breakpoint.setStopLevel( 100 )
        cell, editor = plugins.kwParseMain( **kw )
        cell = af.getCell(CoreName, CRL.Catalog.State.Logical )
        if not cell:
            cell = CRL.Blif.load( CoreName )
        if editor:
            editor.setCell( cell ) 
            editor.setDbuMode( DbU.StringModePhysical )
        ioPadsSpec = []
        h,v =  44*sliceHeight,  44*sliceHeight
        pitch_id=['hpitch','hpitch', 'hpitch', 'hpitch']

        L = generate_ioPinsSpec_list(pitch_id,dico,h,v,hpitch,hpitch)
        M =[]
        for i in range(len(L)):
            S= L[i]
            tup= (int(eval(S[0])),S[1],int(eval(S[2])),int(eval(S[3])),eval(S[4]))
            M.append(tup)
        ioPinsSpec =M 
        print(ioPinsSpec)

        designConf = ChipConf( cell, ioPins=ioPinsSpec, ioPads=ioPadsSpec ) 
        designConf.cfg.etesian.bloat               = 'disabled'
       #designConf.cfg.etesian.bloat               = 'nsxlib'
        designConf.cfg.etesian.densityVariation    = 0.05
        designConf.cfg.etesian.aspectRatio         = 1.0
       # etesian.spaceMargin is ignored if the coreSize is directly set.
       #designConf.cfg.etesian.spaceMargin         = 0.10
       #designConf.cfg.anabatic.searchHalo         = 2
        designConf.cfg.anabatic.globalIterations   = 6
        designConf.cfg.katana.hTracksReservedLocal = 6
        designConf.cfg.katana.vTracksReservedLocal = 3
        designConf.cfg.katana.hTracksReservedMin   = 4
        designConf.cfg.katana.vTracksReservedMin   = 5
        designConf.cfg.katana.trackFill            = 0
        designConf.cfg.katana.runRealignStage      = True
        designConf.cfg.block.spareSide             = 16*sliceHeight
        designConf.cfg.chip.padCoreSide            = 'North'
       #designConf.cfg.chip.use45corners           = False
       #designConf.cfg.chip.useAbstractPads        = True
        designConf.cfg.chip.supplyRailWidth        = l(250.0)
        designConf.cfg.chip.supplyRailPitch        = l(450.0)
        designConf.editor              = editor
        designConf.useSpares           = True
        designConf.useHFNS             = False
        designConf.bColumns            = 2
        designConf.bRows               = 2
        designConf.chipName            = 'chip'
        designConf.chipConf.ioPadGauge = 'LEF.GF_IO_Site'
        designConf.coreToChipClass     = CoreToChip
        designConf.coreSize            = (  45*sliceHeight,  45*sliceHeight )
        designConf.chipSize            = ( 140*sliceHeight, 140*sliceHeight )
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
            designConf.useHTree( 'reset' )
            blockBuilder = Block( designConf )
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
