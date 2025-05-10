`timescale 1ns / 1ps

module inverter_1bit_tb;

    reg a;
    reg inv_signal;
    wire y_generated;
    wire y_ref;

    integer pass_count = 0;
    integer fail_count = 0;

    // 实例化待测模块
    inverter_1bit inverter_1bit_inst (
        .a(a),
        .inv_signal(inv_signal),
        .y(y_generated)
    );

    // 实例化参考模块
    inverter_1bit_ref inverter_1bit_ref_inst (
        .a(a),
        .inv_signal(inv_signal),
        .y(y_ref)
    );

    initial begin
        $monitor("Time=%0t: a=%b, inv_signal=%b, y_generated=%b, y_ref=%b", 
                 $time, a, inv_signal, y_generated, y_ref);
    end

    initial begin
        // Test case 1
        a = 1'b0;   inv_signal = 1'b0;  #10 check_result();
        // Test case 2
        a = 1'b1;   inv_signal = 1'b0;  #10 check_result();
        // Test case 3
        a = 1'b0;   inv_signal = 1'b1;  #10 check_result();
        // Test case 4
        a = 1'b1;   inv_signal = 1'b1;  #10 check_result();

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
            if (y_generated === y_ref) begin
                pass_count = pass_count + 1;
                $display("Test %d: Passed", pass_count + fail_count);
            end else begin
                fail_count = fail_count + 1;
                $display("Test %d: Failed (a=%b, inv_signal=%b, y_generated=%b, y_ref=%b)",
                         pass_count + fail_count, a, inv_signal, y_generated, y_ref);
            end
        end
    endtask

endmodule