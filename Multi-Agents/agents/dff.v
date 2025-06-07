module d_flip_flop (
    input clk,
    input rst,
    input d,
    output q,
    output q_not
);
    wire Y1,Y2,Y3,Y4,Y5,Y6;
    wire Y3_1;
    wire d1;
    wire rst_;

    nor g8 (rst_, rst);
    and g9 (d1, rst_, d);

    nand g1 (Y1, Y2, Y4);
    nand g2 (Y2, clk, Y1);
    and g3_1 (Y3_1, clk, Y2);
    nand g3 (Y3, Y3_1, Y4);
    nand g4 (Y4, Y3, d1);
    nand g5 (Y5, Y2, Y6);
    nand g6 (Y6, Y3, Y5);
    assign      q = Y5;
    nor g7 (q_not, q);

endmodule