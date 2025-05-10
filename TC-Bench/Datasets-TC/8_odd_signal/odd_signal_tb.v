`timescale 1ns / 1ps

module odd_signal_tb(

    );

    reg a;
    reg b;
    reg c;
    reg d;

    wire y;

    initial begin
        $monitor("Time=%0t: a=%b, b=%b, c=%b, d=%b, y=%b", $time, a, b, c, d, y);
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

    odd_signal odd_signal_inst
    (
        .a(a),
        .b(b),
        .c(c),
        .d(d),
        .y(y)
    );

endmodule
