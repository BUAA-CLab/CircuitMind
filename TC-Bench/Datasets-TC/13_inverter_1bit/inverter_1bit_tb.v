`timescale 1ns / 1ps

module inverter_1bit_tb(

    );

    reg a;
    reg inv_signal;
    wire y;

    initial begin
        $monitor("Time=%0t: a=%b, inv_signal=%b, y=%b", $time, a, inv_signal, y);
    end

    initial begin
        a = 1'b0;   inv_signal = 1'b0;  #10;
        a = 1'b1;   inv_signal = 1'b0;  #10;
        a = 1'b0;   inv_signal = 1'b1;  #10;
        a = 1'b1;   inv_signal = 1'b1;  #10;

        $finish(0);
    end

    inverter_1bit inverter_1bit_inst
    (
        .a(a),
        .inv_signal(inv_signal),
        .y(y)
    );

endmodule
