`timescale 1ns / 1ps

module elegant_storage_ref_tb(

);

    reg clk;
    reg write_enable;        // Write enable signal for testing
    reg [7:0] data_in;      // Data input for testing
    wire [7:0] data_out;    // Data output from the module

    // Instantiate the ReadWriteMemory module
    elegant_storage_ref elegant_storage_inst (
        .clk(clk),
        .write_enable(write_enable),
        .data_in(data_in),
        .data_out(data_out)
    );

    initial begin
        // Monitor the signals
        $monitor("Time = %0d: write_enable = %b, data_in = %b, data_out = %b", $time, write_enable, data_in, data_out);
    end

    initial begin
        clk = 1;
        forever #5 clk = ~clk; // 10 time units clock period
    end

    initial begin

        // Initialize signals
        write_enable = 0;
        data_in = 8'b00000000;

        // Test case 1: Write 0x55 to memory
        write_enable = 1;
        data_in = 8'h55;
        write_enable = 0;

        // Verify data output reflects written value

        // Test case 2: Write 0xAA to memory
        write_enable = 1;
        data_in = 8'hAA;
        write_enable = 0;

        // Verify data output reflects written value

        // Test case 3: Write 0xFF to memory
        write_enable = 1;
        data_in = 8'hFF;
        write_enable = 0;

        // Verify data output reflects written value

        // End simulation
        $finish(0);
    end

endmodule

