`timescale 1ns / 1ps

module half_adder_tb(

    );

    reg a;
    reg b;

    wire Sum;
    wire Carry;

    initial begin
        $monitor("Time=%0t: a=%b, b=%b, Sum=%b, Carry=%b", $time, a, b, Sum, Carry);
    end

    initial begin
        a = 1'b0;   b = 1'b0;   #10;
        a = 1'b1;   b = 1'b0;   #10;
        a = 1'b0;   b = 1'b1;   #10;
        a = 1'b1;   b = 1'b1;   #10;

        $finish(0);
    end

    half_adder half_adder_inst
    (
        .a(a),
        .b(b),
        .Sum(Sum),
        .Carry(Carry)
    );

endmodule
