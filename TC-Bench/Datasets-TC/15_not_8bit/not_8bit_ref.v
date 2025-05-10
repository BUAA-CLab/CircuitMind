module not_8bit_ref(
        input wire [7:0] a,
        output wire [7:0] y
    );

    assign y = ~a;

endmodule
