module conditional_checker_ref (
    input signed [7:0] value,        // Signed 8-bit input value (修正为 signed)
    input [2:0] condition,    // 3-bit condition code
    output reg result         // Output result: high for true, low for false
);

always @(*) begin
    case (condition)
        3'b000: result = 0;                       // Never
        3'b001: result = (value == 0);         // value = 0 (有符号数 0)
        3'b010: result = (value < 0);                // value < 0 (Signed Comparison)
        3'b011: result = (value <= 0);               // value <= 0 (Signed Comparison)
        3'b100: result = 1;                       // Always
        3'b101: result = (value != 0);         // value != 0 (有符号数 0)
        3'b110: result = (value >= 0);               // value >= 0 (Signed Comparison)
        3'b111: result = (value > 0);                // value > 0 (Signed Comparison)
        default: result = 0;                      // Default to low
    endcase
end

endmodule