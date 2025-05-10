`timescale 1ns / 1ps

module not_gate_ref_tb(

    );

    reg in;
    wire out;

    initial begin
        $monitor("Time=%0t: in=%b, out=%b", $time, in, out);
    end

    initial begin
        in = 1'b0;
        in = 1'b1;

        $finish(0);
    end

    not_gate_ref not_gate_inst
    (
        .in(in),
        .out(out)
    );

endmodule
