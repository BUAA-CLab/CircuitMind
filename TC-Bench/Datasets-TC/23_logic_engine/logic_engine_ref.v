module logic_engine_ref(
    input [7:0] A,        // 8-bit input A
    input [7:0] B,        // 8-bit input B
    input [1:0] opcode,   // 2-bit opcode to select operation
    output reg [7:0] result // 修改为 output reg result
);

    // Always block to compute result based on opcode
    always @(*) begin
        case (opcode)
            2'b00: result <= A | B;        // OR operation  (使用非阻塞赋值 <=)
            2'b01: result <= ~(A & B);    // NAND operation (使用非阻塞赋值 <=)
            2'b10: result <= ~(A | B);    // NOR operation (使用非阻塞赋值 <=)
            2'b11: result <= A & B;       // AND operation (使用非阻塞赋值 <=)
            default: result <= 8'b00000000; // Default case (should not occur) (使用非阻塞赋值 <=)
        endcase
    end

endmodule