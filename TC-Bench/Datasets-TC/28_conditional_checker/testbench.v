`timescale 1ns / 1ps

module conditional_checker_tb;

    reg [7:0] value;          // 8-bit input value for testing
    reg [2:0] condition;      // 3-bit condition code for testing
    wire result_generated;    // Output result from DUT
    wire result_ref;          // Output result from reference module

    integer pass_count = 0;
    integer fail_count = 0;

    // Instantiate the DUT (Device Under Test)
    conditional_checker conditional_checker_inst (
        .value(value),
        .condition(condition),
        .result(result_generated)
    );

    // Instantiate the reference module
    conditional_checker_ref conditional_checker_ref_inst (
        .value(value),
        .condition(condition),
        .result(result_ref)
    );

    initial begin
        $monitor("Time = %0d: value = %b, condition = %b, result_generated = %b, result_ref = %b", 
                 $time, value, condition, result_generated, result_ref);
    end

    initial begin
        // Test case 1: condition = 000 (Never)
        value = 8'b00000000; condition = 3'b000;

        // Test case 2: condition = 001 (value = 0)
        value = 8'b00000000; condition = 3'b001;
        value = 8'b00000001; condition = 3'b001;

        // Test case 3: condition = 010 (value < 0)
        value = 8'b10000000; condition = 3'b010; // Negative
        value = 8'b01111111; condition = 3'b010; // Non-negative

        // Test case 4: condition = 011 (value <= 0)
        value = 8'b00000000; condition = 3'b011;
        value = 8'b10000000; condition = 3'b011;
        value = 8'b00000001; condition = 3'b011;

        // Test case 5: condition = 100 (Always)
        value = 8'b10101010; condition = 3'b100;

        // Test case 6: condition = 101 (value != 0)
        value = 8'b00000000; condition = 3'b101;
        value = 8'b11111111; condition = 3'b101;

        // Test case 7: condition = 110 (value >= 0)
        value = 8'b00000000; condition = 3'b110;
        value = 8'b01111111; condition = 3'b110;
        value = 8'b10000000; condition = 3'b110;

        // Test case 8: condition = 111 (value > 0)
        value = 8'b00000001; condition = 3'b111;
        value = 8'b00000000; condition = 3'b111;
        value = 8'b10000000; condition = 3'b111;

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
            if (result_generated === result_ref) begin
                pass_count = pass_count + 1;
                $display("Test %d: Passed", pass_count + fail_count);
            end else begin
                fail_count = fail_count + 1;
                $display("Test %d: Failed (value = %b, condition = %b, result_generated = %b, result_ref = %b)", 
                         pass_count + fail_count, value, condition, result_generated, result_ref);
            end
        end
    endtask

endmodule