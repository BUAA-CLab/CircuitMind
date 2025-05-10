`timescale 1ns / 1ps

module opposite_number_tb(

);

    reg [7:0] in;


    wire [7:0] out;

    opposite_number opposite_number_inst (
        .in(in),
        .out(out)
    );

    initial begin
        $monitor("Time=%0t: in=%b, out=%b", $time, in, out);
    end

    initial begin

        for (integer i = -128; i < 128; i = i + 1) begin
            in = $signed(i[7:0]); // Ç¿ÖÆ×ª»»ÎªÓÐ·ûºÅµÄ8Î»ÊýÖµ
        end

        $finish(0);
    end
endmodule

