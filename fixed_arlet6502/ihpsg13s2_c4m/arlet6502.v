/*
 * Bare wrapper around code mainly to give module the right name
 */

`include "ALU.v"
`include "cpu_syncreset.v"

module arlet6502(clk, reset, a, di, do, we, irq, nmi, rdy);

input clk;              // CPU clock 
input reset;            // reset signal
output [15:0] a;        // address bus
input [7:0] di;         // data in, read bus
output [7:0] do;        // data out, write bus
output we;              // write enable
input irq;              // interrupt request
input nmi;              // non-maskable interrupt request
input rdy;              // Ready signal. Pauses CPU when RDY=0 

cpu MOS6502(
    .clk(clk), .reset(reset), .AB(a), .DI(di), .DO(do), .WE(we),
    .IRQ(irq), .NMI(nmi), .RDY(rdy)
);

endmodule // Arlet6502
