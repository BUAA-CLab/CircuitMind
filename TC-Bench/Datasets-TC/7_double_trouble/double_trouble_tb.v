`timescale 1ns / 1ps

module drouble_trouble_tb(

    );

    reg a;
    reg b;
    reg c;
    reg d;

    wire out;

    initial begin
        $monitor("Time=%0t: a=%b, b=%b, c=%b, d=%b, out=%b", $time, a, b, c, d, out);
    end

    initial begin
        a = 1'b0;   b = 1'b0;   c = 1'b0;   d = 1'b0;   #10;
        a = 1'b1;   b = 1'b0;   c = 1'b0;   d = 1'b0;   #10;
        a = 1'b0;   b = 1'b1;   c = 1'b0;   d = 1'b0;   #10;
        a = 1'b1;   b = 1'b1;   c = 1'b0;   d = 1'b0;   #10;
        a = 1'b0;   b = 1'b0;   c = 1'b1;   d = 1'b0;   #10;
        a = 1'b1;   b = 1'b0;   c = 1'b1;   d = 1'b0;   #10;
        a = 1'b0;   b = 1'b1;   c = 1'b1;   d = 1'b0;   #10;
        a = 1'b1;   b = 1'b1;   c = 1'b1;   d = 1'b0;   #10;
        a = 1'b0;   b = 1'b0;   c = 1'b0;   d = 1'b1;   #10;
        a = 1'b1;   b = 1'b0;   c = 1'b0;   d = 1'b1;   #10;
        a = 1'b0;   b = 1'b1;   c = 1'b0;   d = 1'b1;   #10;
        a = 1'b1;   b = 1'b1;   c = 1'b0;   d = 1'b1;   #10;
        a = 1'b0;   b = 1'b0;   c = 1'b1;   d = 1'b1;   #10;
        a = 1'b1;   b = 1'b0;   c = 1'b1;   d = 1'b1;   #10;
        a = 1'b0;   b = 1'b1;   c = 1'b1;   d = 1'b1;   #10;
        a = 1'b1;   b = 1'b1;   c = 1'b1;   d = 1'b1;   #10;

        $finish(0);
    end

    double_trouble double_trouble_inst
    (
        .a(a),
        .b(b),
        .c(c),
        .d(d),
        .out(out)
    );

endmodule
