module double_trouble (
    input wire a,    
    input wire b,     
    input wire c,     
    input wire d,     
    output wire out   
);

    wire [2:0] sum;
    assign sum = a + b + c + d;

    assign out = (sum >= 2) ? 1'b1 : 1'b0;
    
endmodule