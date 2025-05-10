module decoder_3bit (
    input wire [2:0] in,
    output wire [7:0] out
);

    assign out = 1 << in;

endmodule
