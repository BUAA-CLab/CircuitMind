`timescale 1ns / 1ps

module adder_8bit_ref_tb;

    // Testbench signals
    reg  [7:0] a;
    reg  [7:0] b;
    reg        carry_in;

    wire [7:0] sum_generated;
    wire       carry_out_generated;
    wire [7:0] sum_ref;
    wire       carry_out_ref;

    integer pass_count = 0;
    integer fail_count = 0;

    // Instantiate the DUT (Device Under Test)
    adder_8bit adder_8bit_inst (
        .a(a),
        .b(b),
        .carry_in(carry_in),
        .sum(sum_generated),
        .carry_out(carry_out_generated)
    );

    // Instantiate the reference module
    adder_8bit_ref adder_8bit_ref_inst (
        .a(a),
        .b(b),
        .carry_in(carry_in),
        .sum(sum_ref),
        .carry_out(carry_out_ref)
    );

    initial begin
        $monitor("Time=%0t: a=%b, b=%b, carry_in=%b, sum_generated=%b, carry_out_generated=%b, sum_ref=%b, carry_out_ref=%b", 
                 $time, a, b, carry_in, sum_generated, carry_out_generated, sum_ref, carry_out_ref);
    end

    initial begin
        // Test case 1: 0 + 0 + 0
        a = 8'b00000000; b = 8'b00000000; carry_in = 1'b0; #10 check_result();

        // Test case 2: 255 + 1 + 0
        a = 8'b11111111; b = 8'b00000001; carry_in = 1'b0; #10 check_result();

        // Test case 3: 128 + 128 + 0
        a = 8'b10000000; b = 8'b10000000; carry_in = 1'b0; #10 check_result();

        // Test case 4: 127 + 127 + 1
        a = 8'b01111111; b = 8'b01111111; carry_in = 1'b1; #10 check_result();

        // Test case 5: 200 + 55 + 1
        a = 8'b11001000; b = 8'b00110111; carry_in = 1'b1; #10 check_result();

        // Test case 6: 0 + 255 + 1
        a = 8'b00000000; b = 8'b11111111; carry_in = 1'b1; #10 check_result();

        // Final result
        if (fail_count == 0) begin
            $display("All tests passed: Passed");
        end else begin
            $display("%d tests failed: Failed", fail_count);
        end

        $finish(0);
    end

    task check_result;
        begin
            if (sum_generated === sum_ref && carry_out_generated === carry_out_ref) begin
                pass_count = pass_count + 1;
                $display("Test %d: Passed", pass_count + fail_count);
            end else begin
                fail_count = fail_count + 1;
                $display("Test %d: Failed (a=%b, b=%b, carry_in=%b, sum_generated=%b, carry_out_generated=%b, sum_ref=%b, carry_out_ref=%b)",
                         pass_count + fail_count, a, b, carry_in, sum_generated, carry_out_generated, sum_ref, carry_out_ref);
            end
        end
    endtask

endmodule