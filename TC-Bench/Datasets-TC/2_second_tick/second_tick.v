module second_tick(
        input wire a,
        input wire b,
        output wire out
    );

    assign out = a & ~b;

endmodule
