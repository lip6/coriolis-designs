#!/usr/bin/env python3

import sys
import os
import traceback
from   coriolis            import Cfg, CRL
from   coriolis.Hurricane  import DbU, Breakpoint
from   coriolis.helpers.io import ErrorMessage, WarningMessage, catch
from   coriolis.helpers    import loadUserSettings, setTraceLevel, trace, overlay, l, u, n
loadUserSettings()
from   coriolis            import plugins
from   coriolis.plugins.block.block         import Block
from   coriolis.plugins.block.configuration import IoPin, GaugeConf
from   coriolis.plugins.block.spares        import Spares
from   coriolis.plugins.chip.configuration  import ChipConf
from   coriolis.plugins.chip.chip           import Chip
from   pdks.sky130_c4m.core2chip.sky130         import CoreToChip
from   connectors_placement                 import generate_ioPinsSpec_list
CoreName = 'counter'
input_side_in_um = 700
input_side_in_um_horizental = 700
aspect_ratio = input_side_in_um_horizental/input_side_in_um


af        = CRL.AllianceFramework.get()
buildChip = False

def scriptMain ( **kw ):
    """The mandatory function to be called by Coriolis CGT/Unicorn."""
    global af, buildChip, CoreName
    vpitch       = 0
    hpitch       = 0
    vdone       = 0
    hdone       = 0
    gaugeName    = Cfg.getParamString('anabatic.routingGauge').asString()
    routingGauge = af.getRoutingGauge( gaugeName )
    for layerGauge in routingGauge.getLayerGauges():
        if (hdone and vdone):
            break
        elif layerGauge.getType() in [ CRL.RoutingLayerGauge.PinOnly
                                   , CRL.RoutingLayerGauge.Unusable
                                   , CRL.RoutingLayerGauge.BottomPowerSupply ]:
            continue
        if layerGauge.getDirection() == CRL.RoutingLayerGauge.Horizontal:
            vpitch = layerGauge.getPitch()
            print("            vpitch        ",vpitch)
            vdone =1
            sliceHeight = af.getCellGauge().getSliceHeight()
        elif layerGauge.getDirection() == CRL.RoutingLayerGauge.Vertical:
            hpitch = layerGauge.getPitch()
            print("            hpitch        ",hpitch)
            hdone =1
            sliceHeight = af.getCellGauge().getSliceHeight()

    sliceHeight = af.getCellGauge().getSliceHeight()
    side_converted= (input_side_in_um*1.0e-6)/(DbU.getPhysicalsPerGrid()*DbU.getResolution())
    #check if the gcell width is multiple of the pitch, else we adapt it
    gcellAR    = Cfg.getParamDouble('anabatic.gcellAspectRatio',1.0).asDouble()
    gcellWidth = int( sliceHeight * gcellAR )
    sliceStep = af.getCellGauge().getSliceStep()
    if gcellWidth % sliceStep:
        gcellWidth += sliceStep - gcellWidth % sliceStep
    #width_converted must be a multiple of gcellWidth
    #height_converted must be a multiple of sliceHeight
    width_converted = int(side_converted - side_converted % gcellWidth )
    height_converted= int( side_converted - side_converted % sliceHeight)
    number_of_sliceHeight= height_converted/sliceHeight
    print(number_of_sliceHeight)

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
        #if 'CHECK_TOOLKIT' in os.environ:
        #    checkToolkitDir   = os.environ[ 'CHECK_TOOLKIT' ]
        #    harnessProjectDir = checkToolkitDir + '/cells/sky130'
        #else:
        #    print( '[ERROR] The "CHECK_TOOLKIT" environment variable has not been set.'  )
        #    print( '        Please check "./mk/users.d/user-CONFIG.mk".'  )
        #    sys.exit( 1 )
        cell, editor = plugins.kwParseMain( **kw )
        cellName = CoreName
        if buildChip:
            cellName += '_harness'
        cell = CRL.Blif.load( CoreName )
        #temporarly here




        #get supply pins not used in placement
        supply_pins = [j.getName() for j in cell.getSupplyNets()]
        vectors = {}
        for i in cell.getExternalNets():
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
        dico= signals_sorted
        pitch_id=['1','1','1','1']
        L=generate_ioPinsSpec_list(pitch_id,dico,((number_of_sliceHeight*sliceHeight)/vpitch)-1,(((number_of_sliceHeight*sliceHeight)/vpitch)-1)/aspect_ratio,1,1)
        M =[]
        for i in range(len(L)):
            S= L[i]
            tup= (int(eval(S[0])),S[1],int(eval(S[2])),int(eval(S[3])),eval(S[4]))
            M.append(tup)
        print(M)    
        ioPinsSpec 	= M
## temporarly here








        if editor:
            editor.setCell( cell ) 
            editor.setDbuMode( DbU.StringModePhysical )
        if buildChip:
            ioPinsSpec = []
            ioPadsSpec = []
        else:
            ioPadsSpec = [ ]
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
       #conf.cfg.katana.hTracksReservedMin   = 3
       #conf.cfg.katana.vTracksReservedMin   = 1
       #conf.cfg.katana.hTracksReservedLocal = 6
       #conf.cfg.katana.vTracksReservedLocal = 3
        conf.cfg.katana.globalRipupLimit     = 7
        conf.cfg.katana.runRealignStage      = False
        conf.cfg.katana.dumpMeasures         = True
        if buildChip:
            #default path is the installation pdk one: pdks/sky130_c4m/4M.Sky130/libs.tech/
            conf.cfg.harness.path            = harnessProjectDir + '/user_project_wrapper.def'
        conf.editor              = editor
        conf.ioPinsInTracks      = True
        conf.useSpares           = True
        conf.useClockTree        = True
        conf.useHFNS             = True
        conf.bColumns            = 2
        conf.bRows               = 2
        conf.chipName            = 'chip'
        conf.coreSize            = conf.computeCoreSize( 160*conf.sliceHeight, 1.0 )
        conf.chipSize            = ( u(2020.0), u(2060.0) )
        conf.coreToChipClass     = CoreToChip
        if buildChip:
            conf.useHTree( 'io_in_from_pad(37)', Spares.HEAVY_LEAF_LOAD )
            conf.useHTree( 'io_in_from_pad(35)' )
        else:
            conf.useHTree( 'clk', Spares.HEAVY_LEAF_LOAD )
            #conf.useHTree( 'reset' )
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
