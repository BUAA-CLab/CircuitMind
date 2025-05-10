`timescale 1ns / 1ps

module mux_8bit_tb;

    reg [7:0] A;
    reg [7:0] B;
    reg select;

    wire [7:0] Y_generated;
    wire [7:0] Y_ref;

    integer pass_count = 0;
    integer fail_count = 0;

    // 实例化待测模块
    mux_8bit mux_8bit_inst (
        .A(A),
        .B(B),
        .select(select),
        .Y(Y_generated)
    );

    // 实例化参考模块
    mux_8bit_ref mux_8bit_ref_inst (
        .A(A),
        .B(B),
        .select(select),
        .Y(Y_ref)
    );

    initial begin
        $monitor("Time=%0t: A=%b, B=%b, select=%b, Y_generated=%b, Y_ref=%b", 
                 $time, A, B, select, Y_generated, Y_ref);
    end

    initial begin
        // Test case 1
        A = 8'd216;
        B = 8'd20; 
        select = 1;

        // Test case 2
        A = 8'd63;
        B = 8'd202; 
        select = 0;

        // Test case 3
        A = 8'd231;
        B = 8'd185; 
        select = 1;

        // Test case 4
        A = 8'd229;
        B = 8'd84; 
        select = 0;

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
            if (Y_generated === Y_ref) begin
                pass_count = pass_count + 1;
                $display("Test %d: Passed", pass_count + fail_count);
            end else begin
                fail_count = fail_count + 1;
                $display("Test %d: Failed (A=%b, B=%b, select=%b, Y_generated=%b, Y_ref=%b)",
                         pass_count + fail_count, A, B, select, Y_generated, Y_ref);
            end
        end
    endtask

endmodule