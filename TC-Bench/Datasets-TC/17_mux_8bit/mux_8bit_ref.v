module mux_8bit_ref (
    input wire [7:0] A, 
    input wire [7:0] B,   
    input wire select,  
      
    output wire [7:0] Y    
);
    
    assign Y = (select == 1'b0) ? A : B;

endmodule
