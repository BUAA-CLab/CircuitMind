`timescale 1ns / 1ps

module box_tb(

);
    // Testbench signals
    reg clk;
    reg rst;
    reg read_enable;
    reg write_enable;
    reg [7:0] write_data;
    reg [1:0] address;

    wire [7:0] read_data;
    wire read_active;

    // Instantiate the module under test
    box box_inst (
        .clk(clk),
        .rst(rst),
        .read_enable(read_enable),
        .write_enable(write_enable),
        .write_data(write_data),
        .address(address),
        .read_data(read_data),
        .read_active(read_active)
    );

    // Clock generation
    initial begin
        clk = 1;
        forever #5 clk = ~clk; // 10 time units clock period
    end

    initial begin
        $monitor("Time=%0t: read_enable=%b, write_enable=%b, write_data=%b, address=%b, read_data=%b, read_active=%d", $time, read_enable, write_enable, write_data, address, read_data, read_active);
    end

    // Test procedure
    initial begin
        // Initialize signals
        rst = 1;
        read_enable = 0;
        write_enable = 0;
        write_data = 8'b00000000;
        address = 2'b00;

        // Apply reset
        rst = 0;

        // Test case 1: Write to register 0
        write_enable = 1;
        write_data = 8'b10101010;
        address = 2'b00;
        write_enable = 0;

        // Test case 2: Write to register 1
        write_enable = 1;
        write_data = 8'b01010101;
        address = 2'b01;
        write_enable = 0;

        // Test case 3: Read from register 0
        read_enable = 1;
        address = 2'b00;
        read_enable = 0;

        // Test case 4: Read from register 1
        read_enable = 1;
        address = 2'b01;
        read_enable = 0;


        // Finish simulation
        $finish(0);
    end
endmodule

