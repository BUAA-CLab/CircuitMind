`timescale 1ns / 1ps

module instruction_decoder_tb(

    );

    reg [7:0] instruction; // 8-bit input for the testbench
    wire mode0;
    wire mode1;
    wire mode2;
    wire mode3;

    // Instantiate the Decoder module
    instruction_decoder instruction_decoder_inst (
        .instruction(instruction),
        .mode0(mode0),
        .mode1(mode1),
        .mode2(mode2),
        .mode3(mode3)
    );

    initial begin
        // Test case 1: instruction[7:6] = 2'b00
        instruction = 8'b00000000; // Mode 0

        // Test case 2: instruction[7:6] = 2'b01
        instruction = 8'b01000000; // Mode 1

        // Test case 3: instruction[7:6] = 2'b10
        instruction = 8'b10000000; // Mode 2

        // Test case 4: instruction[7:6] = 2'b11
        instruction = 8'b11000000; // Mode 3

        // End simulation
        $finish(0);
    end

    initial begin
        // Monitor the signals
        $monitor("Time = %0d: instruction = %b, mode0 = %b, mode1 = %b, mode2 = %b, mode3 = %b", $time, instruction, mode0, mode1, mode2, mode3);
    end
endmodule
