`timescale 1ns / 1ps

module not_8bit_tb;

    reg [7:0] a;
    wire [7:0] y_generated;
    wire [7:0] y_ref;

    integer pass_count = 0;
    integer fail_count = 0;

    // 实例化待测模块
    not_8bit not_8bit_inst (
        .a(a),
        .y(y_generated)
    );

    // 实例化参考模块
    not_8bit_ref not_8bit_ref_inst (
        .a(a),
        .y(y_ref)
    );

    initial begin
        $monitor("Time=%0t: a=%b, y_generated=%b, y_ref=%b", 
                 $time, a, y_generated, y_ref);
    end

    initial begin
        // Test case 1
        a = 8'b11111111;
        // Test case 2
        a = 8'b00000000;
        
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
                $display("Test %d: Failed (a=%b, y_generated=%b, y_ref=%b)",
                         pass_count + fail_count, a, y_generated, y_ref);
            end
        end
    endtask

endmodule