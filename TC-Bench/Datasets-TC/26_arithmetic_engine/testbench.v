`timescale 1ns / 1ps

module arithmetic_engine_tb;

    reg [7:0] A;
    reg [7:0] B;
    reg [2:0] opcode;
    wire [7:0] result_generated;
    wire [7:0] result_ref;

    integer pass_count = 0;
    integer fail_count = 0;

    // Instantiate the DUT (Device Under Test)
    arithmetic_engine arithmetic_engine_inst (
        .A(A),
        .B(B),
        .opcode(opcode),
        .result(result_generated)
    );

    // Instantiate the reference module
    arithmetic_engine_ref arithmetic_engine_ref_inst (
        .A(A),
        .B(B),
        .opcode(opcode),
        .result(result_ref)
    );

    initial begin
        $monitor("Time = %0d: A = %b, B = %b, opcode = %b, result_generated = %b, result_ref = %b", 
                 $time, A, B, opcode, result_generated, result_ref);
    end

    // Test procedure
    initial begin
        // Test case 1: OR operation
        A = 8'b00001111; B = 8'b11110000; opcode = 3'b000; 
        $display("Test %d: OR Operation", pass_count + fail_count); 

        // Test case 2: NAND operation
        A = 8'b10101010; B = 8'b11001100; opcode = 3'b001;
        $display("Test %d: NAND Operation", pass_count + fail_count); 

        // Test case 3: NOR operation
        A = 8'b10101010; B = 8'b01010101; opcode = 3'b010;
        $display("Test %d: NOR Operation", pass_count + fail_count); 

        // Test case 4: AND operation
        A = 8'b11110000; B = 8'b11001100; opcode = 3'b011;
        $display("Test %d: AND Operation", pass_count + fail_count); 

        // Test case 5: ADD operation
        A = 8'b00001111; B = 8'b00000001; opcode = 3'b100;
        $display("Test %d: ADD Operation", pass_count + fail_count); 

        // Test case 6: SUB operation
        A = 8'b00001111; B = 8'b00000001; opcode = 3'b101;
        $display("Test %d: SUB Operation", pass_count + fail_count); 

        // Test case 7: Boundary value test - A=0, B=0, OR
        A = 8'b00000000; B = 8'b00000000; opcode = 3'b000;
        $display("Test %d: OR - Zero Inputs", pass_count + fail_count); 

        // Test case 8: Boundary value test - A=FF, B=FF, AND
        A = 8'b11111111; B = 8'b11111111; opcode = 3'b011;
        $display("Test %d: AND - All Ones Inputs", pass_count + fail_count); 

        // Test case 9: Boundary value test - A=FF, B=0, ADD (Overflow)
        A = 8'b11111111; B = 8'b00000001; opcode = 3'b100;
        $display("Test %d: ADD - Overflow", pass_count + fail_count); 

        // Test case 10: Boundary value test - A=0, B=1, SUB (Underflow)
        A = 8'b00000000; B = 8'b00000001; opcode = 3'b101;
        $display("Test %d: SUB - Underflow", pass_count + fail_count); 

        // Test case 11: Mixed data pattern test - A=alternating, B=inverted alternating, OR
        A = 8'b10101010; B = 8'b01010101; opcode = 3'b000;
        $display("Test %d: OR - Alternating Patterns", pass_count + fail_count); 

        // Test case 12: Mixed data pattern test - A=alternating, B=inverted alternating, AND
        A = 8'b10101010; B = 8'b01010101; opcode = 3'b011;
        $display("Test %d: AND - Alternating Patterns", pass_count + fail_count); 

        // Test case 13: Different data patterns - A=incrementing, B=decrementing, ADD
        A = 8'b00000000; B = 8'b11111111; opcode = 3'b100;
        $display("Test %d: ADD - Increment/Decrement", pass_count + fail_count); 

        // Test case 14: Different data patterns - A=incrementing, B=decrementing, SUB
        A = 8'b00000001; B = 8'b00000000; opcode = 3'b101;
        $display("Test %d: SUB - Increment/Decrement", pass_count + fail_count); 


        // Final result 
        if (fail_count == 0) begin
            $display("All tests passed: Passed");
        end else begin
            $display("%d tests failed: Failed", fail_count);
        end

        // End simulation 
        $finish(0);
    end

    task check_result; // Modified check_result task - No arguments
        begin
            if (result_generated === result_ref) begin
                pass_count = pass_count + 1;
                $display("Test %d: Passed", pass_count + fail_count); // Simplified Pass message
            end else begin
                fail_count = fail_count + 1;
                $display("Test %d: Failed - Expected=%b, Generated=%b (A=%b, B=%b, opcode=%b)", // More detailed failure message
                         pass_count + fail_count, result_ref, result_generated, A, B, opcode);
            end
        end
    endtask

endmodule