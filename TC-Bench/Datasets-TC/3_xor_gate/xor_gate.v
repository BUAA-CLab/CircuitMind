module xor_gate(
    input wire a,
    input wire b,
    output wire y
);

    assign y = (a & ~b) | (~a & b);

endmodule

