`timescale 1ns / 1ps

module counting_signals_tb;

    reg a;
    reg b;
    reg c;
    reg d;
    wire [2:0] count_generated;
    wire [2:0] count_ref;

    integer pass_count = 0;
    integer fail_count = 0;

    // 实例化待测模块
    counting_signals counting_signals_inst (
        .a(a),
        .b(b),
        .c(c),
        .d(d),
        .count(count_generated)
    );

    // 实例化参考模块
    counting_signals_ref counting_signals_ref_inst (
        .a(a),
        .b(b),
        .c(c),
        .d(d),
        .count(count_ref)
    );

    initial begin
        $monitor("Time=%0t: a=%b, b=%b, c=%b, d=%b, count_generated=%b, count_ref=%b", 
                 $time, a, b, c, d, count_generated, count_ref);
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
            if (count_generated === count_ref) begin
                pass_count = pass_count + 1;
                $display("Test %d: Passed", pass_count + fail_count);
            end else begin
                fail_count = fail_count + 1;
                $display("Test %d: Failed (a=%b, b=%b, c=%b, d=%b, count_generated=%b, count_ref=%b)",
                         pass_count + fail_count, a, b, c, d, count_generated, count_ref);
            end
        end
    endtask

endmodule