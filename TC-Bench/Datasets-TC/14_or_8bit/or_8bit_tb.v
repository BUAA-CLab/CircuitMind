`timescale 1ns / 1ps

module or_8bit_tb(

    );

    reg [7:0] a;
    reg [7:0] b;
    wire [7:0] y;

    initial begin
        $monitor("Time=%0t: a=%b, b=%b, y=%b", $time, a, b, y);
    end

    initial begin
        a = 8'b00011100;
        b = 8'b00010001;
        a = 8'b10110010;
        b = 8'b11110100;

        $finish(0);
    end

    or_8bit or_8bit_inst
    (
        .a(a),
        .b(b),
        .y(y)
    );

endmodule
