module adder_8bit_ref (
    input  [7:0] a,          // 8-bit input A
    input  [7:0] b,          // 8-bit input B
    input        carry_in,   // Input carry
    
    output [7:0] sum,        // 8-bit sum output
    output       carry_out   // Carry-out signal
);

    // Intermediate signals for carry propagation
    wire [8:0] full_sum;

    // Perform addition with carry-in
    assign full_sum = a + b + carry_in;

    // Assign the sum and carry-out
    assign sum = full_sum[7:0];      // Lower 8 bits as the sum
    assign carry_out = full_sum[8]; // 9th bit as carry-out

endmodule
