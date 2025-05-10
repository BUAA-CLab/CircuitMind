module half_adder_ref (
    input wire a,       
    input wire b,       
    output wire Sum,    
    output wire Carry   
);

    assign Sum = a ^ b; 
    assign Carry = a & b;

endmodule
