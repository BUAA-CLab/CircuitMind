`timescale 1ns / 1ps

module elegant_storage_tb;

    reg clk;
    reg write_enable;
    reg [7:0] data_in;
    wire [7:0] data_out_generated;
    wire [7:0] data_out_ref;

    integer pass_count = 0;
    integer fail_count = 0;

    // Instantiate the DUT (Device Under Test)
    elegant_storage elegant_storage_inst (
        .clk(clk),
        .write_enable(write_enable),
        .data_in(data_in),
        .data_out(data_out_generated)
    );

    // Instantiate the reference module (behavioral model)
    elegant_storage_ref elegant_storage_ref_inst (
        .clk(clk),
        .write_enable(write_enable),
        .data_in(data_in),
        .data_out(data_out_ref)
    );

    initial begin
        $monitor("Time = %0d: write_enable = %b, data_in = %b, data_out_generated = %b, data_out_ref = %b",
                 $time, write_enable, data_in, data_out_generated, data_out_ref);
    end

    initial begin
        clk = 0; // Initialize to 0, not 1
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
        check_result();

        // Test case 2: Write 0xAA to memory
        write_enable = 1;
        data_in = 8'hAA;
        write_enable = 0;
        check_result();

        // Test case 3: Write 0xFF (boundary value) to memory
        write_enable = 1;
        data_in = 8'hFF; // Boundary value test: Maximum 8-bit value
        write_enable = 0;
        check_result();

        // Test case 4: Write 0x00 (boundary value) to memory
        write_enable = 1;
        data_in = 8'h00; // Boundary value test: Minimum 8-bit value
        write_enable = 0;
        check_result();

        // Test case 5: Consecutive writes with different data
        write_enable = 1;
        data_in = 8'h12;
        check_result();
        data_in = 8'h34;
        check_result();
        data_in = 8'h56;
        write_enable = 0;

        // Final result
        if (fail_count == 0) begin
            $display("All tests passed: Passed");
        end else begin
            $display("%d tests failed: Failed", fail_count);
        end

        // End simulation (increased simulation time)
        $finish;
    end

    task check_result;
        begin
            if (data_out_generated === data_out_ref) begin
                pass_count = pass_count + 1;
                $display("Test %d: Passed", pass_count + fail_count);
            end else begin
                fail_count = fail_count + 1;
                $display("Test %d: Failed (write_enable = %b, data_in = %b, data_out_generated = %b, data_out_ref = %b)",
                         pass_count + fail_count, write_enable, data_in, data_out_generated, data_out_ref);
            end
        end
    endtask

endmodule