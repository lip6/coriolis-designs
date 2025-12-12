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
from   coriolis.designflow.connectors_placement                 import generate_ioPinsSpec_list

af        = CRL.AllianceFramework.get()
buildChip = False
CoreName = 'ibex'
CoreName = 'aes'
CoreName = 'arlet6502'
CoreName = 'picorv32'
CoreName = 'ao68000'
CoreName = 'jpeg_encoder'
CoreName = 'mac'
CoreName = 'uart_rx'
CoreName = 'counter'
input_side_in_um = 700
input_side_in_um_horizental = 700
aspect_ratio = input_side_in_um_horizental/input_side_in_um
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

    rvalue = True
    try:
        #setTraceLevel( 550 )
        #Breakpoint.setStopLevel( 100 )
        cell, editor = plugins.kwParseMain( **kw )
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
        ioPadsSpec = [ (IoPin.WEST , None, 'di_0'       , 'di(0)'  , 'DI(0)'  )
                     , (IoPin.WEST , None, 'di_1'       , 'di(1)'  , 'DI(1)'  )
                     , (IoPin.WEST , None, 'di_2'       , 'di(2)'  , 'DI(2)'  )
                     , (IoPin.WEST , None, 'di_3'       , 'di(3)'  , 'DI(3)'  )
                     , (IoPin.WEST , None, 'allpower_0' , 'DVDD'   , 'VDD'    )
                     , (IoPin.WEST , None, 'allground_0', 'DVSS'   , 'VSS'    )
                     , (IoPin.WEST , None, 'di_4'       , 'di(4)'  , 'DI(4)'  )
                     , (IoPin.WEST , None, 'di_5'       , 'di(5)'  , 'DI(5)'  )
                     , (IoPin.WEST , None, 'di_6'       , 'di(6)'  , 'DI(6)'  )
                     , (IoPin.WEST , None, 'di_7'       , 'di(7)'  , 'DI(7)'  )

                     , (IoPin.SOUTH, None, 'do_0'       , 'do(0)'  , 'DO(0)'  )
                     , (IoPin.SOUTH, None, 'do_1'       , 'do(1)'  , 'DO(1)'  )
                     , (IoPin.SOUTH, None, 'do_2'       , 'do(2)'  , 'DO(2)'  )
                     , (IoPin.SOUTH, None, 'do_3'       , 'do(3)'  , 'DO(3)'  )
                     , (IoPin.SOUTH, None, 'do_4'       , 'do(4)'  , 'DO(4)'  )
                     , (IoPin.SOUTH, None, 'allpower_1' , 'DVDD'   , 'VDD'    )
                     , (IoPin.SOUTH, None, 'allground_1', 'DVSS'   , 'VSS'    )
                     , (IoPin.SOUTH, None, 'do_5'       , 'do(5)'  , 'DO(5)'  )
                     , (IoPin.SOUTH, None, 'do_6'       , 'do(6)'  , 'DO(6)'  )
                     , (IoPin.SOUTH, None, 'do_7'       , 'do(7)'  , 'DO(7)'  )
                     , (IoPin.SOUTH, None, 'a_0'        , 'a(0)'   , 'A(0)'   )
                     , (IoPin.SOUTH, None, 'a_1'        , 'a(1)'   , 'A(1)'   )

                     , (IoPin.EAST , None, 'a_2'        , 'a(2)'   , 'A(2)'   )
                     , (IoPin.EAST , None, 'a_3'        , 'a(3)'   , 'A(3)'   )
                     , (IoPin.EAST , None, 'a_4'        , 'a(4)'   , 'A(4)'   )
                     , (IoPin.EAST , None, 'a_5'        , 'a(5)'   , 'A(5)'   )
                     , (IoPin.EAST , None, 'a_6'        , 'a(6)'   , 'A(6)'   )
                     , (IoPin.EAST , None, 'a_7'        , 'a(7)'   , 'A(7)'   )
                     , (IoPin.EAST , None, 'allpower_2' , 'DVDD'   , 'VDD'    )
                     , (IoPin.EAST , None, 'allground_2', 'DVSS'   , 'VSS'    )
                     , (IoPin.EAST , None, 'a_8'        , 'a(8)'   , 'A(8)'   )
                     , (IoPin.EAST , None, 'a_9'        , 'a(9)'   , 'A(9)'   )
                     , (IoPin.EAST , None, 'a_10'       , 'a(10)'  , 'A(10)'  )
                     , (IoPin.EAST , None, 'a_11'       , 'a(11)'  , 'A(11)'  )
                     , (IoPin.EAST , None, 'a_12'       , 'a(12)'  , 'A(12)'  )
                     , (IoPin.EAST , None, 'a_13'       , 'a(13)'  , 'A(13)'  )

                     , (IoPin.NORTH, None, 'irq'        , 'irq'    , 'IRQ'    )
                     , (IoPin.NORTH, None, 'nmi'        , 'nmi'    , 'NMI'    )
                     , (IoPin.NORTH, None, 'rdy'        , 'rdy'    , 'RDY'    )
                     , (IoPin.NORTH, None, 'allground_3', 'DVSS'   , 'VSS'    )
                     , (IoPin.NORTH, None, 'allpower_3' , 'DVDD'   , 'VDD'    )
                     , (IoPin.NORTH, None, 'clk'        , 'clk'    , 'clk'    )
                     , (IoPin.NORTH, None, 'reset'      , 'reset'  , 'reset'  )
                     , (IoPin.NORTH, None, 'we'         , 'we'     , 'WE'     )
                     , (IoPin.NORTH, None, 'a_14'       , 'a(14)'  , 'A(14)'  )
                     , (IoPin.NORTH, None, 'a_15'       , 'a(15)'  , 'A(15)'  )
                     ]



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
        designConf.coreSize            = designConf.computeCoreSize( number_of_sliceHeight*designConf.sliceHeight, aspect_ratio )
        print('        coresize      ', designConf.coreSize)
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
            #designConf.useHTree( 'reset' )
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
