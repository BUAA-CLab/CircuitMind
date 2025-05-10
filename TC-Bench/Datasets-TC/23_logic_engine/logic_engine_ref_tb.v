`timescale 1ns / 1ps

module tb_logic_engine_ref_tb(

    );

    reg [7:0] A;
    reg [7:0] B;
    reg [1:0] opcode;
    wire [7:0] result;

    initial begin
        $monitor("Time=%0t: A=%b, B=%b, opcode=%b, result=%b", $time, A, B, opcode, result);
    end

    // Test procedure
    initial begin
        // Test case 1: OR operation
        A = 8'b10101010; B = 8'b01010101; opcode = 2'b00;

        // Test case 2: NAND operation
        A = 8'b11110000; B = 8'b00001111; opcode = 2'b01;

        // Test case 3: NOR operation
        A = 8'b10101010; B = 8'b01010101; opcode = 2'b10;

        // Test case 4: AND operation
        A = 8'b11110000; B = 8'b11001100; opcode = 2'b11;

        // Finish simulation
        $finish(0);
    end

    // Instantiate the module under test
    logic_engine_ref logic_engine_inst (
        .A(A),
        .B(B),
        .opcode(opcode),
        .result(result)
    );

endmodule
