`timescale 1ns / 1ps

module mux_8bit_ref_tb(

    );

    reg [7:0] A;
    reg [7:0] B;
    reg select;

    wire [7:0] Y;

    initial begin
        $monitor("Time=%0t: A=%b, B=%b, select=%b, Y=%b", $time, A, B, select, Y);
    end

    initial begin
        A = 8'd216;
        B = 8'd20; 
        select = 1;

        A = 8'd63;
        B = 8'd202; 
        select = 0;

        A = 8'd231;
        B = 8'd185; 
        select = 1;

        A = 8'd229;
        B = 8'd84; 
        select = 0;

        $finish(0);
    end

    mux_8bit_ref mux_8bit_inst (
        .A(A),
        .B(B),
        .select(select),
        .Y(Y)
    );

endmodule
