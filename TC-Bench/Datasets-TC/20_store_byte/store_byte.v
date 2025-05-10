// 2:1 MUX 模块，使用 AND, OR, NOT 实现
module mux_2to1 (
    input sel,       // 选择信号
    input in1,       // 输入1
    input in0,       // 输入0
    output out       // 输出
);
    wire not_sel;
    wire and1_out, and0_out;

    not g1 (not_sel, sel);               // 生成 NOT sel
    and g2 (and1_out, sel, in1);         // 生成 sel AND in1
    and g3 (and0_out, not_sel, in0);     // 生成 NOT sel AND in0
    or  g4 (out, and1_out, and0_out);    // 生成最终输出 (sel AND in1) OR (NOT sel AND in0)
endmodule

// D触发器模块
module d_flip_flop (
    input clk,
    input rst,
    input d,
    output q,
    output q_not
);
    wire Y1, Y2, Y3, Y4, Y5, Y6;
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
    assign q = Y5;
    nor g7 (q_not, q);
endmodule

// 字节存储模块
module store_byte (
    input clk,
    input rst,
    input read_enable,
    input write_enable,
    input [7:0] data_in,
    output [7:0] data_out,
    output output_enable
);

    wire [7:0] data_q_internal;
    wire output_enable_w;

    assign output_enable = output_enable_w;

    genvar i;
    generate
        for (i = 0; i < 8; i = i + 1) begin : byte_storage
            wire d_mux_out;
            // 使用基本逻辑门实现的mux替换三元运算符
            mux_2to1 mux_d (
                .sel(write_enable),
                .in1(data_in[i]),
                .in0(data_q_internal[i]),
                .out(d_mux_out)
            );

            d_flip_flop bit_ff (
                .clk(clk),
                .rst(rst),
                .d(d_mux_out),
                .q(data_q_internal[i]),
                .q_not()
            );
        end
    endgenerate

    genvar j;
    generate
        for (j = 0; j < 8; j = j + 1) begin : byte_storage_1
            wire q_mux_out;
            // 使用基本逻辑门实现的mux替换三元运算符
            mux_2to1 mux_q (
                .sel(read_enable),
                .in1(data_q_internal[j]),
                .in0(data_out[j]),
                .out(q_mux_out)
            );

            d_flip_flop bit_ff (
                .clk(clk),
                .rst(rst),
                .d(q_mux_out),
                .q(data_out[j]),
                .q_not()
            );
        end
    endgenerate

    // 直接根据 read_enable 分配 output_enable
    assign output_enable_w = read_enable;

endmodule