`timescale 1ns / 1ps

module instruction_decoder_tb;

    reg [7:0] instruction; // 8-bit input for the testbench
    wire mode0_generated;
    wire mode1_generated;
    wire mode2_generated;
    wire mode3_generated;
    wire mode0_ref;
    wire mode1_ref;
    wire mode2_ref;
    wire mode3_ref;

    integer pass_count = 0;
    integer fail_count = 0;

    // Instantiate the DUT (Device Under Test)
    instruction_decoder instruction_decoder_inst (
        .instruction(instruction),
        .mode0(mode0_generated),
        .mode1(mode1_generated),
        .mode2(mode2_generated),
        .mode3(mode3_generated)
    );

    // Instantiate the reference module
    instruction_decoder_ref instruction_decoder_ref_inst (
        .instruction(instruction),
        .mode0(mode0_ref),
        .mode1(mode1_ref),
        .mode2(mode2_ref),
        .mode3(mode3_ref)
    );

    initial begin
        $monitor("Time = %0d: instruction = %b, mode0_generated = %b, mode1_generated = %b, mode2_generated = %b, mode3_generated = %b, mode0_ref = %b, mode1_ref = %b, mode2_ref = %b, mode3_ref = %b", 
                 $time, instruction, mode0_generated, mode1_generated, mode2_generated, mode3_generated, mode0_ref, mode1_ref, mode2_ref, mode3_ref);
    end

    // Test procedure
    initial begin
        // Test case 1: instruction[7:6] = 2'b00
        instruction = 8'b00000000; // Mode 0

        // Test case 2: instruction[7:6] = 2'b01
        instruction = 8'b01000000; // Mode 1

        // Test case 3: instruction[7:6] = 2'b10
        instruction = 8'b10000000; // Mode 2

        // Test case 4: instruction[7:6] = 2'b11
        instruction = 8'b11000000; // Mode 3

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
            if (mode0_generated === mode0_ref &&
                mode1_generated === mode1_ref &&
                mode2_generated === mode2_ref &&
                mode3_generated === mode3_ref) begin
                pass_count = pass_count + 1;
                $display("Test %d: Passed", pass_count + fail_count);
            end else begin
                fail_count = fail_count + 1;
                $display("Test %d: Failed (instruction = %b, mode0_generated = %b, mode1_generated = %b, mode2_generated = %b, mode3_generated = %b, mode0_ref = %b, mode1_ref = %b, mode2_ref = %b, mode3_ref = %b)", 
                         pass_count + fail_count, instruction, mode0_generated, mode1_generated, mode2_generated, mode3_generated, mode0_ref, mode1_ref, mode2_ref, mode3_ref);
            end
        end
    endtask

endmodule