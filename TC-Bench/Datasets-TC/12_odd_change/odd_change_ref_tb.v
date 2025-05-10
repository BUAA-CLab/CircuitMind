`timescale 1ns / 1ps

module odd_change_ref_tb(

    );

    reg clk;
    reg rst;

    wire dout;

    initial begin
        clk = 1;
        forever #5 clk = ~clk; 
    end

    initial begin
        $monitor("Time=%0t:  dout=%b", $time,  dout);
    end

    initial begin

        rst = 1;

        rst = 0;


        $finish(0);
    end

    odd_change_ref odd_change_inst
    (
        .clk(clk),
        .rst(rst),
        .dout(dout)
    );


endmodule
