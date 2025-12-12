#!/usr/bin/env python3

import sys
import traceback
from   coriolis.Hurricane  import DbU, Breakpoint, Cell
from   coriolis            import CRL
from   coriolis.helpers.io import ErrorMessage, WarningMessage, catch
from   coriolis.helpers    import loadUserSettings, setTraceLevel, trace, l, u, n
loadUserSettings()
from   coriolis            import plugins
from   coriolis.plugins.block.block         import Block
from   coriolis.plugins.block.configuration import IoPin, GaugeConf
from   coriolis.plugins.block.spares        import Spares
from   coriolis.plugins.core2chip.niolib    import CoreToChip
from   coriolis.plugins.chip.configuration  import ChipConf
from   coriolis.plugins.chip.chip           import Chip
from   coriolis.designflow.connectors_placement                 import *

af = CRL.AllianceFramework.get()

CoreName = 'picorv32'
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
    global af
    DbU.setStringMode( DbU.StringModeSymbolic )
    dico = get_signals_hurricane(CoreName)
    rvalue = True
    try:
        #setTraceLevel( 550 )
        #Breakpoint.setStopLevel( 100 )
        cell, editor = plugins.kwParseMain( **kw )
        cell = af.getCell( CoreName, CRL.Catalog.State.Logical )
        af.saveCell( cell, CRL.Catalog.State.Logical )
        if editor:
            editor.setCell( cell ) 
        ioPadsSpec = []
        m1pitch=l(5)
        m2pitch=l(10)
        ioPadsSpec = [ ]
        h,v =  (398* l( 10), 398*l(10 ))
        pitch_id=['1*m2pitch','1*m2pitch','1*m2pitch','1*m2pitch']

        L = generate_ioPinsSpec_list(pitch_id,dico,h,v,m2pitch,m2pitch)
        M =[]
        for i in range(len(L)):
            S= L[i]
            tup= (int(eval(S[0])),S[1],int(eval(S[2])),int(eval(S[3])),eval(S[4]))
            M.append(tup)
        ioPinsSpec =M 
        print(ioPinsSpec)

        conf = ChipConf( cell, ioPins=ioPinsSpec, ioPads=ioPadsSpec ) 
        #conf.cfg.etesian.aspectRatio         = 1.0
        conf.cfg.etesian.spaceMargin         = 0.10
        #conf.cfg.etesian.densityVariation    = 0.05
        #conf.cfg.anabatic.searchHalo         = 2
        conf.cfg.anabatic.globalIterations   = 10
        conf.cfg.anabatic.topRoutingLayer    = 'METAL5'
        conf.cfg.block.spareSide             = l(1000)
        conf.cfg.katana.hTracksReservedMin   = 6
        conf.cfg.katana.vTracksReservedMin   = 5
        conf.cfg.katana.hTracksReservedLocal = 10
        conf.cfg.katana.vTracksReservedLocal = 7 
        conf.cfg.katana.termSatReservedLocal = 6 
        conf.cfg.katana.termSatThreshold     = 9 
        conf.cfg.katana.trackFill            = 0
        conf.cfg.katana.runRealignStage      = True
        conf.cfg.katana.dumpMeasures         = False
        conf.useSpares = True
        conf.useHFNS   = False
        conf.useHTree( 'clk', Spares.HEAVY_LEAF_LOAD )
        conf.coreSize =  (400* l( 10), 400*l(10 ))
        conf.editor = editor
        blockBuilder = Block( conf )
        cell.setTerminalNetlist( False )
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
