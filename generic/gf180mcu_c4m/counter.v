module counter (
   input clk,            // clock         
   input load,          // load the value
   input [7:0] val,     // input value loaded in the counter
   output reg [7:0] cpt // counter value
);
   wire [7:0] omux, oadd;
   
   assign omux = load ? val : cpt;
   assign oadd = omux + 1;	  

   always @(posedge clk) begin
      cpt <= oadd;
   end
endmodule
