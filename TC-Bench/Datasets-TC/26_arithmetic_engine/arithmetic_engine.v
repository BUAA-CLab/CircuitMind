module arithmetic_engine(
        input [7:0] A,        // 8-bit input A
        input [7:0] B,        // 8-bit input B
        input [2:0] opcode,   // 2-bit opcode to select operation
        output reg [7:0] result // 8-bit result
    );

    always @(*) begin
        case (opcode)
            3'b000: result = A | B;        // OR operation
            3'b001: result = ~(A & B);    // NAND operation
            3'b010: result = ~(A | B);    // NOR operation
            3'b011: result = A & B;       // AND operation
            3'b100: result = A + B;
            3'b101: result = A - B;
            default: result = 8'b00000000; // Default case (should not occur)
        endcase
    end

endmodule
