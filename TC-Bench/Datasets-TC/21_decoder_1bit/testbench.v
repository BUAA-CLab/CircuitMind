`timescale 1ns / 1ps

module decoder_1bit_tb;

    reg in;
    wire out1_generated, out2_generated;
    wire out1_ref, out2_ref;

    integer pass_count = 0;
    integer fail_count = 0;

    // Instantiate the DUT (Device Under Test)
    decoder_1bit decoder_1bit_inst (
        .in(in),
        .out1(out1_generated),
        .out2(out2_generated)
    );

    // Instantiate the reference module
    decoder_1bit_ref decoder_1bit_ref_inst (
        .in(in),
        .out1(out1_ref),
        .out2(out2_ref)
    );

    initial begin
        $monitor("Time=%0t: in=%b, out1_generated=%b, out2_generated=%b, out1_ref=%b, out2_ref=%b", 
                 $time, in, out1_generated, out2_generated, out1_ref, out2_ref);
    end

    initial begin
        // Test case 1: in = 0
        in = 1'b0;

        // Test case 2: in = 1
        in = 1'b1;

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
            if (out1_generated === out1_ref && out2_generated === out2_ref) begin
                pass_count = pass_count + 1;
                $display("Test %d: Passed", pass_count + fail_count);
            end else begin
                fail_count = fail_count + 1;
                $display("Test %d: Failed (in=%b, out1_generated=%b, out2_generated=%b, out1_ref=%b, out2_ref=%b)", 
                         pass_count + fail_count, in, out1_generated, out2_generated, out1_ref, out2_ref);
            end
        end
    endtask

endmodule