`timescale 1ns / 1ps

module double_trouble_tb;

    reg a;
    reg b;
    reg c;
    reg d;
    wire out_generated;
    wire out_ref;

    integer pass_count = 0;
    integer fail_count = 0;

    // 实例化待测模块
    double_trouble double_trouble_inst (
        .a(a),
        .b(b),
        .c(c),
        .d(d),
        .out(out_generated)
    );

    // 实例化参考模块
    double_trouble_ref double_trouble_ref_inst (
        .a(a),
        .b(b),
        .c(c),
        .d(d),
        .out(out_ref)
    );

    initial begin
        $monitor("Time=%0t: a=%b, b=%b, c=%b, d=%b, out_generated=%b, out_ref=%b", 
                 $time, a, b, c, d, out_generated, out_ref);
    end

    initial begin
        // Test case 1
        a = 1'b0;   b = 1'b0;   c = 1'b0;   d = 1'b0;   #10 check_result();
        // Test case 2
        a = 1'b1;   b = 1'b0;   c = 1'b0;   d = 1'b0;   #10 check_result();
        // Test case 3
        a = 1'b0;   b = 1'b1;   c = 1'b0;   d = 1'b0;   #10 check_result();
        // Test case 4
        a = 1'b1;   b = 1'b1;   c = 1'b0;   d = 1'b0;   #10 check_result();
        // Test case 5
        a = 1'b0;   b = 1'b0;   c = 1'b1;   d = 1'b0;   #10 check_result();
        // Test case 6
        a = 1'b1;   b = 1'b0;   c = 1'b1;   d = 1'b0;   #10 check_result();
        // Test case 7
        a = 1'b0;   b = 1'b1;   c = 1'b1;   d = 1'b0;   #10 check_result();
        // Test case 8
        a = 1'b1;   b = 1'b1;   c = 1'b1;   d = 1'b0;   #10 check_result();
        // Test case 9
        a = 1'b0;   b = 1'b0;   c = 1'b0;   d = 1'b1;   #10 check_result();
        // Test case 10
        a = 1'b1;   b = 1'b0;   c = 1'b0;   d = 1'b1;   #10 check_result();
        // Test case 11
        a = 1'b0;   b = 1'b1;   c = 1'b0;   d = 1'b1;   #10 check_result();
        // Test case 12
        a = 1'b1;   b = 1'b1;   c = 1'b0;   d = 1'b1;   #10 check_result();
        // Test case 13
        a = 1'b0;   b = 1'b0;   c = 1'b1;   d = 1'b1;   #10 check_result();
        // Test case 14
        a = 1'b1;   b = 1'b0;   c = 1'b1;   d = 1'b1;   #10 check_result();
        // Test case 15
        a = 1'b0;   b = 1'b1;   c = 1'b1;   d = 1'b1;   #10 check_result();
        // Test case 16
        a = 1'b1;   b = 1'b1;   c = 1'b1;   d = 1'b1;   #10 check_result();

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
                $display("Test %d: Failed (a=%b, b=%b, c=%b, d=%b, out_generated=%b, out_ref=%b)",
                         pass_count + fail_count, a, b, c, d, out_generated, out_ref);
            end
        end
    endtask

endmodule