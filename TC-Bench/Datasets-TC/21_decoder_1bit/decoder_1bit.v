module decoder_1bit(
    input wire in,
    output wire out1,
    output wire out2
);

    assign out1 = ~in;
    assign out2 = in;

endmodule
