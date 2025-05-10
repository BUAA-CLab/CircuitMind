`timescale 1ns / 1ps

module counting_signals_ref_tb(

    );

    reg a;
    reg b;
    reg c;
    reg d;
    wire [2:0] count;

    initial begin
        $monitor("Time=%0t: a=%b, b=%b, c=%b, d=%b, count=%b", $time, a, b, c, d, count);
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

    counting_signals_ref counting_signals_inst
    (
        .a(a),
        .b(b),
        .c(c),
        .d(d),
        .count(count)
    );

endmodule
