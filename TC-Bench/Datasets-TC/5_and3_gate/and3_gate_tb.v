`timescale 1ns / 1ps

module and3_gate_tb(

    );

    reg a;
    reg b;
    reg c;
    wire y;

    initial begin
        $monitor("Time=%0t: a=%b, b=%b, c=%b, y=%b", $time, a, b, c, y);
    end

    initial begin
        a = 1'b0;   b = 1'b0;   c = 1'b0;   #10;
        a = 1'b1;   b = 1'b0;   c = 1'b0;   #10;
        a = 1'b0;   b = 1'b1;   c = 1'b0;   #10;
        a = 1'b1;   b = 1'b1;   c = 1'b0;   #10;
        a = 1'b0;   b = 1'b0;   c = 1'b1;   #10;
        a = 1'b1;   b = 1'b0;   c = 1'b1;   #10;
        a = 1'b0;   b = 1'b1;   c = 1'b1;   #10;
        a = 1'b1;   b = 1'b1;   c = 1'b1;   #10;

        $finish(0);
    end

    and3_gate and3_gate_inst
    (
        .a(a),
        .b(b),
        .c(c),
        .y(y)
    );

endmodule
