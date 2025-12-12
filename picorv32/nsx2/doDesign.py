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
from   pdks.nsx2.core2chip.niolib           import CoreToChip
from   coriolis.plugins.chip.configuration  import ChipConf
from   coriolis.plugins.chip.chip           import Chip


af = CRL.AllianceFramework.get()

CoreName = 'picorv32'

def scriptMain ( **kw ):
    """The mandatory function to be called by Coriolis CGT/Unicorn."""
    global af, CoreName
    DbU.setStringMode( DbU.StringModeSymbolic )
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
        m1pitch = l(10.0)
        m2pitch = l(20.0)
        ioPinsSpec = [ (IoPin.NORTH|IoPin.A_BEGIN, 'trace_data({})'  ,     2*m2pitch, 2*m2pitch, range(0, 36))
                         , (IoPin.NORTH|IoPin.A_BEGIN, 'mem_la_wdata({})',  148*m2pitch,2*m2pitch, range(0, 32))
                         , (IoPin.NORTH|IoPin.A_BEGIN, 'mem_la_addr({})' ,  278*m2pitch,2*m2pitch, range(0, 32))
                         , (IoPin.SOUTH|IoPin.A_BEGIN, 'eoi({})'         ,   2*  m2pitch,2*m2pitch, range(0, 32))
                         , (IoPin.SOUTH|IoPin.A_BEGIN, 'mem_addr({})'    ,  100*m2pitch,2*m2pitch, range(0, 32))
                         , (IoPin.SOUTH|IoPin.A_BEGIN, 'mem_wdata({})'   ,  200*m2pitch,2*m2pitch, range(0, 32))
                         , (IoPin.SOUTH|IoPin.A_BEGIN, 'mem_rdata({})'   ,  300*m2pitch,4*m2pitch, range(0,  4))
                         , (IoPin.EAST |IoPin.A_BEGIN, 'mem_rdata({})'   ,     2*m1pitch, 2*m1pitch, range(4, 32))
                         , (IoPin.EAST |IoPin.A_BEGIN, 'irq({})'         ,  100*m1pitch, 2*m1pitch, range(0, 32))
                         , (IoPin.EAST |IoPin.A_BEGIN, 'pcpi_insn({})'   ,  200*m1pitch, 2*m1pitch, range(0, 32))
                         , (IoPin.EAST |IoPin.A_BEGIN, 'pcpi_rs1({})'    ,  300*m1pitch, 2*m1pitch, range(0,  8))
                         , (IoPin.WEST |IoPin.A_BEGIN, 'pcpi_rs1({})'    ,    2* m1pitch, 2*m1pitch, range(8, 32))
                         , (IoPin.WEST |IoPin.A_BEGIN, 'pcpi_rd({})'     ,  68*m1pitch, 2*m1pitch, range(0, 32))
                         , (IoPin.WEST |IoPin.A_BEGIN, 'pcpi_rs2({})'    ,  148*m1pitch, 2*m1pitch, range(8, 32))
                         , (IoPin.WEST |IoPin.A_BEGIN, 'mem_wstrb({})'   , 240*m1pitch, 2*m1pitch, range(0,  4))
                         , (IoPin.WEST |IoPin.A_BEGIN, 'mem_la_wstrb({})', 260*m1pitch, 2*m1pitch, range(0,  4))
                         , (IoPin.WEST |IoPin.A_BEGIN, 'mem_la_write'    , 284*m1pitch, 0, range(0, 1))
                         , (IoPin.WEST |IoPin.A_BEGIN, 'trap'            , 288*m1pitch, 0, range(0, 1))
                         , (IoPin.WEST |IoPin.A_BEGIN, 'resetn'          , 292*m1pitch, 0, range(0, 1))
                         , (IoPin.WEST |IoPin.A_BEGIN, 'mem_instr'       , 296*m1pitch, 0, range(0, 1))
                         , (IoPin.WEST |IoPin.A_BEGIN, 'mem_valid'       , 300*m1pitch, 0, range(0, 1))
                         , (IoPin.WEST |IoPin.A_BEGIN, 'mem_la_read'     , 304*m1pitch, 0, range(0, 1))
                         , (IoPin.WEST |IoPin.A_BEGIN, 'pcpi_wr'         , 308*m1pitch, 0, range(0, 1))
                         , (IoPin.WEST |IoPin.A_BEGIN, 'pcpi_wait'       , 312*m1pitch, 0, range(0, 1))
                         , (IoPin.WEST |IoPin.A_BEGIN, 'trace_valid'     , 316*m1pitch, 0, range(0, 1))
                         , (IoPin.WEST |IoPin.A_BEGIN, 'mem_ready'       , 320*m1pitch, 0, range(0, 1))
                         , (IoPin.WEST |IoPin.A_BEGIN, 'clk'             , 324*m1pitch, 0, range(0, 1))
                         , (IoPin.WEST |IoPin.A_BEGIN, 'pcpi_valid'      , 328*m1pitch, 0, range(0, 1))
                         , (IoPin.WEST |IoPin.A_BEGIN, 'pcpi_ready'      , 332*m1pitch, 0, range(0, 1))]




        print(ioPinsSpec)
        conf = ChipConf( cell, ioPins=ioPinsSpec, ioPads=ioPadsSpec ) 
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
        conf.coreSize =  ( l( 9800.0), l( 9800.0) )
        conf.editor    = editor
        blockBuilder   = Block( conf )
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
