`timescale 1ns / 1ps

module not_8bit_ref_tb(

    );

    reg [7:0] a;
    wire [7:0] y;

    initial begin
        $monitor("Time=%0t: a=%b, y=%b", $time, a, y);
    end

    initial begin
        a = 8'b11111111;
        a = 8'b00000000;
        
        $finish(0);
    end

    not_8bit_ref not_8bit_inst
    (
        .a(a),
        .y(y)
    );

endmodule
