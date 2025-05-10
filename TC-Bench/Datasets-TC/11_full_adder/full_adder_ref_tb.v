`timescale 1ns / 1ps

module full_adder_ref_tb(

    );

    reg a;
    reg b;
    reg c;

    wire Sum;
    wire Carry;

    initial begin
        $monitor("Time=%0t: a=%b, b=%b, c=%b, Sum=%b, Carry=%b", $time, a, b, c, Sum, Carry);
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

    full_adder_ref full_adder_inst
    (
        .a(a),
        .b(b),
        .c(c),
        .Sum(Sum),
        .Carry(Carry)
    );

endmodule
