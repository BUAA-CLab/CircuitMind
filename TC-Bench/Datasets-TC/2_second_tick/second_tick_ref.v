module second_tick_ref(
        input wire a,
        input wire b,
        output wire out
    );

    assign out = a & ~b;

endmodule
