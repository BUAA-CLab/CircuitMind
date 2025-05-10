`timescale 1ns / 1ps

module counter_tb;

    // Testbench signals
    reg clk;
    reg rst;
    reg mode;
    reg [7:0] write_data;
    wire [7:0] count_generated;
    wire [7:0] count_ref;

    integer pass_count = 0;
    integer fail_count = 0;
    integer test_count = 0;

    // Instantiate the DUT (Device Under Test)
    counter counter_inst (
        .clk(clk),
        .rst(rst),
        .mode(mode),
        .write_data(write_data),
        .count(count_generated)
    );

    // Instantiate the reference module
    counter_ref counter_ref_inst (
        .clk(clk),
        .rst(rst),
        .mode(mode),
        .write_data(write_data),
        .count(count_ref)
    );

    // Clock generation
    initial begin
        clk = 0;
        forever #5 clk = ~clk; // 10 time units clock period
    end

    initial begin
        $monitor("Time=%0t: mode=%b, write_data=%b, count_generated=%b, count_ref=%b",
                 $time, mode, write_data, count_generated, count_ref);
    end

    // Test procedure
    initial begin
        // Initialize signals
        rst = 1;
        mode = 0;
        write_data = 8'b00000000;
        rst = 0;

        // Test case 1: Reset and initial state (check after reset)
        test_count = test_count + 1;

        // Test case 2: Step mode - increment by 1
        mode = 0; // Step mode
        test_count = test_count + 1;

        // Test case 3: Overwrite mode - write data 8'b10101010
        mode = 1; // Overwrite mode
        write_data = 8'b10101010;
        test_count = test_count + 1;

        // Test case 4: Step mode again after overwrite - continue incrementing
        mode = 0;
        test_count = test_count + 1;

        // Test case 5: Overwrite mode again - write data 8'b11001100
        mode = 1;
        write_data = 8'b11001100;
        test_count = test_count + 1;

        // Finish simulation
        if (fail_count == 0) begin
            $display("All tests passed: Passed");
        end else begin
            $display("%d tests failed: Failed", fail_count);
        end
        $finish(0);
    end

    always @(posedge clk) begin
        check_result(test_count); // Removed the time condition
    end

    task check_result (input current_test);
        begin
            if (count_generated === count_ref) begin
                pass_count = pass_count + 1;
                $display("Test %0d: Passed", current_test);
            end else begin
                fail_count = fail_count + 1;
                $display("Test %0d: Failed (Test=%0d, mode=%b, write_data=%b, Generated=%b, Expected=%b)",
                         current_test, current_test, mode, write_data, count_generated, count_ref); // Added Expected output
            end
        end
    endtask

endmodule