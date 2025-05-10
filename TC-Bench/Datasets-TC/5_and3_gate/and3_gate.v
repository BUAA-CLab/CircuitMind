module and3_gate(
    input wire a,
    input wire b,
    input wire c,
    output wire y
);

    assign y = a & b & c;

endmodule
