`timescale 1ns / 1ps

module not_gate_tb;

    reg in;
    wire out_generated;
    wire out_ref;

    // 实例化待测模块
    not_gate not_gate_inst (
        .in(in),
        .out(out_generated)
    );

    // 实例化参考模块
    not_gate_ref not_gate_ref_inst (
        .in(in),
        .out(out_ref)
    );

    integer pass_count = 0;
    integer fail_count = 0;

    initial begin
        // Test case 1
        in = 1'b0;

        // Test case 2
        in = 1'b1;

        // Final result
        if (fail_count == 0) begin
            $display("All tests passed: Passed");
        end else begin
            $display("%d tests failed: Failed", fail_count);
        end

        $finish;
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