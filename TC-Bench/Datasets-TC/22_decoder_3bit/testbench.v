`timescale 1ns / 1ps

module decoder_3bit_tb;

    reg [2:0] in;
    wire [7:0] out_generated;
    wire [7:0] out_ref;

    integer pass_count = 0;
    integer fail_count = 0;

    // Instantiate the DUT (Device Under Test)
    decoder_3bit decoder_3bit_inst (
        .in(in),
        .out(out_generated)
    );

    // Instantiate the reference module
    decoder_3bit_ref decoder_3bit_ref_inst (
        .in(in),
        .out(out_ref)
    );

    initial begin
        $monitor("Time=%0t: in=%b, out_generated=%b, out_ref=%b", 
                 $time, in, out_generated, out_ref);
    end

    initial begin
        // Test case 1: in = 000
        in = 3'b000; #10 check_result();
        // Test case 2: in = 001
        in = 3'b001; #10 check_result();
        // Test case 3: in = 010
        in = 3'b010; #10 check_result();
        // Test case 4: in = 011
        in = 3'b011; #10 check_result();
        // Test case 5: in = 100
        in = 3'b100; #10 check_result();
        // Test case 6: in = 101
        in = 3'b101; #10 check_result();
        // Test case 7: in = 110
        in = 3'b110; #10 check_result();
        // Test case 8: in = 111
        in = 3'b111; #10 check_result();

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
            if (out_generated === out_ref) begin
                pass_count = pass_count + 1;
                $display("Test %d: Passed", pass_count + fail_count);
            end else begin
                fail_count = fail_count + 1;
                $display("Test %d: Failed (in=%b, out_generated=%b, out_ref=%b)", 
                         pass_count + fail_count, in, out_generated, out_ref);
            end
        end
    endtask

endmodule