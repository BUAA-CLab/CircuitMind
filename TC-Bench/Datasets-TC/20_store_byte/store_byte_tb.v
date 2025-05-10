`timescale 1ns / 1ps

module store_byte_tb();

    reg clk;
    reg rst;
    reg read_enable;
    reg write_enable;
    reg [7:0] data_in;
    wire [7:0] data_out;
    wire output_enable;

    // Instantiate the store_byte module
    store_byte store_byte_inst (
        .clk(clk),
        .rst(rst),
        .read_enable(read_enable),
        .write_enable(write_enable),
        .data_in(data_in),
        .data_out(data_out),
        .output_enable(output_enable)
    );

    // Clock generation
    initial begin
        clk = 0;
        forever #5 clk = ~clk; // 10 time units clock period
    end

    initial begin
        // Initialize signals
        rst = 1; // Assert reset initially
        read_enable = 0;
        write_enable = 0;
        data_in = 8'b00000000;
        rst = 0; // Release reset

        // Test case 1: Write data to memory
        write_enable = 1;
        data_in = 8'b10101010;
        write_enable = 1;
        write_enable = 0;

        // Test case 2: Read data from memory
        read_enable = 1;
        read_enable = 0;

        // Test case 3: Ensure no output without read enable
        read_enable = 0;

        // Test case 4: Write new data and read it
        write_enable = 1;
        data_in = 8'b01010101;
        write_enable = 1;
        write_enable = 0;
        read_enable = 1;
        read_enable = 0;

        // End simulation
        $finish(0);
    end

    initial begin
        // Monitor signals
        $monitor("Time = %0d: clk = %b, rst = %b, read_enable = %b, write_enable = %b, data_in = %b, data_out = %b, output_enable = %b", $time, clk, rst, read_enable, write_enable, data_in, data_out, output_enable);
    end

endmodule