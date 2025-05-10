module not_gate(
        input wire in,
        output wire out
    );

    assign out = ~(in & in);

endmodule
