`timescale 1ns / 1ps

module opposite_number_tb;

    reg [7:0] in;

    wire [7:0] out_generated;
    wire [7:0] out_ref;

    integer pass_count = 0;
    integer fail_count = 0;

    // 实例化待测模块
    opposite_number opposite_number_inst (
        .in(in),
        .out(out_generated)
    );

    // 实例化参考模块
    opposite_number_ref opposite_number_ref_inst (
        .in(in),
        .out(out_ref)
    );

    initial begin
        $monitor("Time=%0t: in=%b, out_generated=%b, out_ref=%b", 
                 $time, in, out_generated, out_ref);
    end

    initial begin
        for (integer i = -128; i < 128; i = i + 1) begin
            in = $signed(i[7:0]); // 强制转换为有符号的8位值
        end

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