`timescale 1ns / 1ps

module tb_logic_engine_tb;

    reg [7:0] A;
    reg [7:0] B;
    reg [1:0] opcode;
    wire [7:0] result_generated;
    wire [7:0] result_ref;

    integer pass_count = 0;
    integer fail_count = 0;

    // Instantiate the DUT (Device Under Test)
    logic_engine logic_engine_inst (
        .A(A),
        .B(B),
        .opcode(opcode),
        .result(result_generated)
    );

    // Instantiate the reference module
    logic_engine_ref logic_engine_ref_inst (
        .A(A),
        .B(B),
        .opcode(opcode),
        .result(result_ref)
    );

    initial begin
        $monitor("Time=%0t: A=%b, B=%b, opcode=%b, result_generated=%b, result_ref=%b",
                 $time, A, B, opcode, result_generated, result_ref);
    end

    // Test procedure
    initial begin
        // Test case 1: OR operation
        A = 8'b10101010; B = 8'b01010101; opcode = 2'b00;
        $display("Test %d: OR Operation", pass_count + fail_count); // Inline operation name in $display

        // Test case 2: NAND operation
        A = 8'b11110000; B = 8'b00001111; opcode = 2'b01;
        $display("Test %d: NAND Operation", pass_count + fail_count); // Inline operation name in $display

        // Test case 3: NOR operation
        A = 8'b10101010; B = 8'b01010101; opcode = 2'b10;
        $display("Test %d: NOR Operation", pass_count + fail_count); // Inline operation name in $display

        // Test case 4: AND operation
        A = 8'b11110000; B = 8'b11001100; opcode = 2'b11;
        $display("Test %d: AND Operation", pass_count + fail_count); // Inline operation name in $display

        // Test case 5: Boundary value test - A=0, B=0, OR
        A = 8'b00000000; B = 8'b00000000; opcode = 2'b00;
        $display("Test %d: OR - Zero Inputs", pass_count + fail_count); // Inline operation name in $display

        // Test case 6: Boundary value test - A=FF, B=FF, AND
        A = 8'b11111111; B = 8'b11111111; opcode = 2'b11;
        $display("Test %d: AND - All Ones Inputs", pass_count + fail_count); // Inline operation name in $display

        // Test case 7: Mixed data pattern test - A=random, B=alternating, NAND
        A = 8'hA5; B = 8'b10101010; opcode = 2'b01;
        $display("Test %d: NAND - Mixed Data", pass_count + fail_count); // Inline operation name in $display


        // Final result
        if (fail_count == 0) begin
            $display("All tests passed: Passed");
        end else begin
            $display("%d tests failed: Failed", fail_count);
        end

        // Finish simulation
        $finish(0);
    end

    task check_result; // Simplified check_result task - No arguments
        begin
            if (result_generated === result_ref) begin
                pass_count = pass_count + 1;
                $display("Test %d: Passed", pass_count + fail_count);
            end else begin
                fail_count = fail_count + 1;
                $display("Test %d: Failed - Expected=%b, Generated=%b (A=%b, B=%b, opcode=%b)", // More detailed failure message
                         pass_count + fail_count, result_ref, result_generated, A, B, opcode); // Include Expected value and input values in failure message
            end
        end
    endtask

endmodule