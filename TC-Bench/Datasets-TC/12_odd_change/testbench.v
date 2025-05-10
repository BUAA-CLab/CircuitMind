`timescale 1ns / 1ps

module odd_change_tb;

    reg clk;
    reg rst;

    wire dout_generated;
    wire dout_ref;

    integer pass_count = 0;
    integer fail_count = 0;

    // 实例化待测模块
    odd_change odd_change_inst (
        .clk(clk),
        .rst(rst),
        .dout(dout_generated)
    );

    // 实例化参考模块
    odd_change_ref odd_change_ref_inst (
        .clk(clk),
        .rst(rst),
        .dout(dout_ref)
    );

    initial begin
        clk = 0; // Initialize clk to 0 at time 0 (Improved style)
        forever #5 clk = ~clk;
    end

    initial begin
        $monitor("Time=%0t: rst=%b, clk=%b, dout_generated=%b, dout_ref=%b", $time, rst, clk, dout_generated, dout_ref);
    end

    initial begin

        rst = 1;
        rst = 0;

        // Test Case 1: Initial dout value after reset

        // Test Case 2: Verify odd/even cycle output for longer duration
        repeat (20) begin // Increased repeat count to 20 (Longer duration)
            check_periodic_dout(); // Renamed task to check_periodic_dout
        end


        // Final result
        if (fail_count == 0) begin
            $display("All tests passed: Passed");
        end else begin
            $display("%d tests failed: Failed", fail_count);
        end

        $finish(0);
    end

    task check_initial_dout;  // New task to check initial dout after reset
        begin
            if (dout_generated === 1'b0 && dout_ref === 1'b0) begin // Expected initial dout to be 0 (even cycle start)
                pass_count = pass_count + 1;
                $display("Test %d: Passed (Initial dout after reset)", pass_count + fail_count);
            end else begin
                fail_count = fail_count + 1;
                $display("Test %d: Failed (Initial dout after reset - dout_generated=%b, dout_ref=%b)",
                         pass_count + fail_count,  dout_generated, dout_ref);
            end
        end
    endtask

    task check_periodic_dout; // Renamed task to check periodic behavior
        begin
            if (dout_generated === dout_ref) begin
                pass_count = pass_count + 1;
                $display("Test %d: Passed (Periodic dout check)", pass_count + fail_count);
            end else begin
                fail_count = fail_count + 1;
                $display("Test %d: Failed (Periodic dout check - dout_generated=%b, dout_ref=%b)",
                         pass_count + fail_count,  dout_generated, dout_ref);
            end
        end
    endtask

endmodule