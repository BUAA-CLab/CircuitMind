`timescale 1ns / 1ps

module full_adder_tb;

    reg a;
    reg b;
    reg c;

    wire Sum_generated;
    wire Carry_generated;
    wire Sum_ref;
    wire Carry_ref;

    integer pass_count = 0;
    integer fail_count = 0;

    // 实例化待测模块
    full_adder full_adder_inst (
        .a(a),
        .b(b),
        .c(c),
        .Sum(Sum_generated),
        .Carry(Carry_generated)
    );

    // 实例化参考模块
    full_adder_ref full_adder_ref_inst (
        .a(a),
        .b(b),
        .c(c),
        .Sum(Sum_ref),
        .Carry(Carry_ref)
    );

    initial begin
        $monitor("Time=%0t: a=%b, b=%b, c=%b, Sum_generated=%b, Carry_generated=%b, Sum_ref=%b, Carry_ref=%b", 
                 $time, a, b, c, Sum_generated, Carry_generated, Sum_ref, Carry_ref);
    end

    initial begin
        // Test case 1
        a = 1'b0;   b = 1'b0;   c = 1'b0;   #10 check_result();
        // Test case 2
        a = 1'b1;   b = 1'b0;   c = 1'b0;   #10 check_result();
        // Test case 3
        a = 1'b0;   b = 1'b1;   c = 1'b0;   #10 check_result();
        // Test case 4
        a = 1'b1;   b = 1'b1;   c = 1'b0;   #10 check_result();
        // Test case 5
        a = 1'b0;   b = 1'b0;   c = 1'b1;   #10 check_result();
        // Test case 6
        a = 1'b1;   b = 1'b0;   c = 1'b1;   #10 check_result();
        // Test case 7
        a = 1'b0;   b = 1'b1;   c = 1'b1;   #10 check_result();
        // Test case 8
        a = 1'b1;   b = 1'b1;   c = 1'b1;   #10 check_result();

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
            if (Sum_generated === Sum_ref && Carry_generated === Carry_ref) begin
                pass_count = pass_count + 1;
                $display("Test %d: Passed", pass_count + fail_count);
            end else begin
                fail_count = fail_count + 1;
                $display("Test %d: Failed (a=%b, b=%b, c=%b, Sum_generated=%b, Carry_generated=%b, Sum_ref=%b, Carry_ref=%b)",
                         pass_count + fail_count, a, b, c, Sum_generated, Carry_generated, Sum_ref, Carry_ref);
            end
        end
    endtask

endmodule