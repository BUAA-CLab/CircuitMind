module counter (
    input clk,              // Clock signal
    input rst,              // Reset signal
    input mode,             // Mode: 0 for step, 1 for overwrite
    input [7:0] write_data, // 8-bit data to write
    output reg [7:0] count  // 8-bit counter output
);

    // Always block for counter logic
    always @(posedge clk) begin
        if (rst) begin
            count <= 8'b00000000; // Reset counter to 0
        end 
        else begin
            if (mode) begin
                count <= write_data; // Overwrite mode
            end 
            else begin
                count <= count + 1; // Step mode
            end
        end
    end

endmodule
