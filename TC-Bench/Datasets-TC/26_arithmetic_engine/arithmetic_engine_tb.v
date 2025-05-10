`timescale 1ns / 1ps

module arithmetic_engine_tb(

    );

    reg [7:0] A;
    reg [7:0] B;
    reg [2:0] opcode;
    wire [7:0] result;

    initial begin
        // Monitor the signals
        $monitor("Time = %0d: A = %b, B = %b, opcode = %b, result = %b", $time, A, B, opcode, result);
    end

    initial begin
        // Initialize inputs
        A = 8'b00001111; B = 8'b11110000; opcode = 3'b000; // Test OR
        A = 8'b10101010; B = 8'b11001100; opcode = 3'b001; // Test NAND
        A = 8'b10101010; B = 8'b11001100; opcode = 3'b010; // Test NOR
        A = 8'b10101010; B = 8'b11001100; opcode = 3'b011; // Test AND
        A = 8'b00001111; B = 8'b00000001; opcode = 3'b100; // Test ADD
        A = 8'b00001111; B = 8'b00000001; opcode = 3'b101; // Test SUB

        // End simulation
        $finish(0);
    end

    arithmetic_engine arithmetic_engine_inst
    (
        .A(A),
        .B(B),
        .opcode(opcode),
        .result(result)
    );

endmodule
