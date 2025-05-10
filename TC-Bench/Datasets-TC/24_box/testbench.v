`timescale 1ns / 1ps

module box_tb;

    // Testbench signals
    reg clk;
    reg rst;
    reg read_enable;
    reg write_enable;
    reg [7:0] write_data;
    reg [1:0] address;

    wire [7:0] read_data_generated;
    wire [7:0] read_data_ref;
    wire read_active_generated;
    wire read_active_ref;

    integer pass_count = 0;
    integer fail_count = 0;

    // Instantiate the DUT (Device Under Test)
    box box_inst (
        .clk(clk),
        .rst(rst),
        .read_enable(read_enable),
        .write_enable(write_enable),
        .write_data(write_data),
        .address(address),
        .read_data(read_data_generated),
        .read_active(read_active_generated)
    );

    // Instantiate the reference module
    box_ref box_ref_inst (
        .clk(clk),
        .rst(rst),
        .read_enable(read_enable),
        .write_enable(write_enable),
        .write_data(write_data),
        .address(address),
        .read_data(read_data_ref),
        .read_active(read_active_ref)
    );

    // Clock generation
    initial begin
        clk = 1;
        forever #5 clk = ~clk; // 10 time units clock period
    end

    initial begin
        $monitor("Time=%0t: read_enable=%b, write_enable=%b, write_data=%b, address=%b, read_data_generated=%b, read_data_ref=%b, read_active_generated=%b, read_active_ref=%b", 
                 $time, read_enable, write_enable, write_data, address, read_data_generated, read_data_ref, read_active_generated, read_active_ref);
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

        // Final result
        if (fail_count == 0) begin
            $display("All tests passed: Passed");
        end else begin
            $display("%d tests failed: Failed", fail_count);
        end

        // Finish simulation
        $finish(0);
    end

    task check_result;
        begin
            if (read_data_generated === read_data_ref && read_active_generated === read_active_ref) begin
                pass_count = pass_count + 1;
                $display("Test %d: Passed", pass_count + fail_count);
            end else begin
                fail_count = fail_count + 1;
                $display("Test %d: Failed (read_enable=%b, write_enable=%b, write_data=%b, address=%b, read_data_generated=%b, read_data_ref=%b, read_active_generated=%b, read_active_ref=%b)", 
                         pass_count + fail_count, read_enable, write_enable, write_data, address, read_data_generated, read_data_ref, read_active_generated, read_active_ref);
            end
        end
    endtask

endmodule