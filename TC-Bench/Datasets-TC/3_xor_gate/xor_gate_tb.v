`timescale 1ns / 1ps

module xor_gate_tb(

    );

    reg a;
    reg b;
    wire y;

    initial begin
        $monitor("Time=%0t: a=%b, b=%b, y=%b", $time, a, b, y);
    end

    initial begin
        a = 1'b0;b = 1'b0;#10;
        a = 1'b1;b = 1'b0;#10;
        a = 1'b0;b = 1'b1;#10;
        a = 1'b1;b = 1'b1;#10;

        $finish(0);
    end

    xor_gate xor_gate_inst
    (
        .a(a),
        .b(b),
        .y(y)
    );

endmodule
