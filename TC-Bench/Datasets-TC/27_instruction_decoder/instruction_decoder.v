module instruction_decoder(
        input [7:0] instruction, // 8-bit input instruction
        output reg mode0,        // Output for mode 0
        output reg mode1,        // Output for mode 1
        output reg mode2,        // Output for mode 2
        output reg mode3         // Output for mode 3
    );

    always @(*) begin
        // Default all modes to 0
        mode0 = 0;
        mode1 = 0;
        mode2 = 0;
        mode3 = 0;

        // Decode based on the two most significant bits
        case (instruction[7:6])
            2'b00: mode0 = 1; // Mode 0
            2'b01: mode1 = 1; // Mode 1
            2'b10: mode2 = 1; // Mode 2
            2'b11: mode3 = 1; // Mode 3
            default: ;        // Default case (not strictly necessary)
        endcase
    end
    
endmodule
