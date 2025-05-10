module full_adder (
    input wire a,
    input wire b,      
    input wire c,       
    output wire Sum,    
    output wire Carry   
);

    assign Sum = a ^ b ^ c; 
    assign Carry = (a & b) | (b & c) | (a & c); 

endmodule
