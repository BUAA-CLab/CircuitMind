module conditional_checker (
    input [7:0] value,        // 8-bit input value
    input [2:0] condition,    // 3-bit condition code
    output reg result         // Output result: high for true, low for false
);

always @(*) begin
    case (condition)
        3'b000: result = 0;                       // Never
        3'b001: result = (value == 8'b0);         // value = 0
        3'b010: result = value[7];                // value < 0 (negative if MSB is 1)
        3'b011: result = value[7] || (value == 8'b0); // value <= 0
        3'b100: result = 1;                       // Always
        3'b101: result = (value != 8'b0);         // value != 0
        3'b110: result = ~value[7];               // value >= 0 (non-negative if MSB is 0)
        3'b111: result = ~value[7] && (value != 8'b0); // value > 0
        default: result = 0;                      // Default to low
    endcase
end

endmodule

