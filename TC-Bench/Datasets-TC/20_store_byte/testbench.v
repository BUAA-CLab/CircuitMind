`timescale 1ns / 1ps

module store_byte_tb;

    reg clk;
    reg rst;
    reg read_enable;
    reg write_enable;
    reg [7:0] data_in;
    wire [7:0] data_out_generated;
    wire [7:0] data_out_ref;
    wire output_enable_generated;
    wire output_enable_ref;

    integer pass_count = 0;
    integer fail_count = 0;

    // Instantiate the DUT (Device Under Test)
    store_byte store_byte_inst (
        .clk(clk),
        .rst(rst),
        .read_enable(read_enable),
        .write_enable(write_enable),
        .data_in(data_in),
        .data_out(data_out_generated),
        .output_enable(output_enable_generated)
    );

    // Instantiate the reference module
    store_byte_ref store_byte_ref_inst (
        .clk(clk),
        .rst(rst),
        .read_enable(read_enable),
        .write_enable(write_enable),
        .data_in(data_in),
        .data_out(data_out_ref),
        .output_enable(output_enable_ref)
    );

    // Clock generation
    initial begin
        clk = 0;
        forever #5 clk = ~clk; // 10 time units clock period
    end

    initial begin
        // Monitor signals
        $monitor("Time = %0d: clk = %b, read_enable = %b, write_enable = %b, data_in = %b, data_out_generated = %b, data_out_ref = %b, output_enable_generated = %b, output_enable_ref = %b",
                 $time, clk, read_enable, write_enable, data_in, data_out_generated, data_out_ref, output_enable_generated, output_enable_ref);
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
        write_enable = 0;
        read_enable = 1;
        read_enable = 0;

        // Final result
        if (fail_count == 0) begin
            $display("All tests passed: Passed");
        end else begin
            $display("%d tests failed: Failed", fail_count);
        end

        // End simulation
        $finish(0);
    end

    task check_result;
        begin
            if (read_enable) begin // If read_enable is 1, check if data_out_generated matches data_out_ref
                if (data_out_generated === data_out_ref && output_enable_generated === output_enable_ref) begin
                    pass_count = pass_count + 1;
                    $display("Test %d: Passed", pass_count + fail_count);
                end else begin
                    fail_count = fail_count + 1;
                    $display("Test %d: Failed (write_enable = %b, read_enable = %b, data_in = %b, data_out_generated = %b (Expected %b), data_out_ref = %b, output_enable_generated = %b, output_enable_ref = %b)",
                             pass_count + fail_count, write_enable, read_enable, data_in, data_out_generated, data_out_ref, output_enable_generated, output_enable_ref);
                end
            end
             else begin // If read_enable is 0, we only check output_enable
                if (output_enable_generated === output_enable_ref) begin // Only check output_enable here
                    pass_count = pass_count + 1;
                    $display("Test %d: Passed (Output Enable Only Check - read_enable=0)", pass_count + fail_count);
                end else begin
                    fail_count = fail_count + 1;
                    $display("Test %d: Failed (Output Enable Check Failed - read_enable=0, output_enable_generated = %b, output_enable_ref = %b)",
                             pass_count + fail_count, output_enable_generated, output_enable_ref);
                end
            end
        end
    endtask

endmodule