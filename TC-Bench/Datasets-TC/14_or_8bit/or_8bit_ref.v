module or_8bit_ref (
    input wire [7:0] a,
    input wire [7:0] b,
    output wire [7:0] y
);

    assign y = a | b;

endmodule