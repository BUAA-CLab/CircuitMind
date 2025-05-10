`timescale 1ns / 1ps

module decoder_1bit_tb(

    );

    reg in;
    wire out1, out2;

    initial begin
        $monitor("Time=%0t: in=%b, out1=%b, out2=%b", $time, in, out1, out2);
    end

    initial begin
        in = 1'b0;  #10;
        in = 1'b1;  #10;

        $finish(0);
    end

    decoder_1bit decoder_1bit_inst
    (
        .in(in),
        .out1(out1),
        .out2(out2)
    );

endmodule
