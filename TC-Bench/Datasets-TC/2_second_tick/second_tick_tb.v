`timescale 1ns / 1ps

module second_tick_tb(

    );

    reg a;
    reg b;
    wire out;

    initial begin
        $monitor("Time=%0t: a=%b, b=%b, out=%b", $time, a, b, out);
    end

    initial begin
        a = 1'b0; b = 1'b0; #10;
        a = 1'b1; b = 1'b0; #10;
        a = 1'b0; b = 1'b1; #10;
        a = 1'b1; b = 1'b1; #10;

        $finish(0);
    end

    second_tick second_tick_inst
    (
        .a(a),
        .b(b),
        .out(out)
    );

endmodule
