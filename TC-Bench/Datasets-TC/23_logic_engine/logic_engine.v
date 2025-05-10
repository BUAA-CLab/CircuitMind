module logic_engine(
    input [7:0] A,        // 8-bit input A
    input [7:0] B,        // 8-bit input B
    input [1:0] opcode,   // 2-bit opcode to select operation
    output reg [7:0] result // 8-bit result
);

    // Always block to compute result based on opcode
    always @(*) begin
        case (opcode)
            2'b00: result = A | B;        // OR operation
            2'b01: result = ~(A & B);    // NAND operation
            2'b10: result = ~(A | B);    // NOR operation
            2'b11: result = A & B;       // AND operation
            default: result = 8'b00000000; // Default case (should not occur)
        endcase
    end

endmodule

