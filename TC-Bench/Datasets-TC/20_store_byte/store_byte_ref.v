module store_byte_ref (
    input clk,                // Clock signal
    input rst,
    input read_enable,        // Read enable signal
    input write_enable,       // Write enable signal
    input [7:0] data_in,      // Data input for writing
    output reg [7:0] data_out,// Data output for reading
    output reg output_enable  // Output enable signal
);

    reg [7:0] memory; // 8-bit memory storage

    always @(posedge clk) begin
        if(rst) begin
            memory <= 8'b0; // Explicitly reset memory
            data_out <= 8'b0;
            output_enable <= 1'b0;
        end
        else begin
            if (write_enable) begin
                memory <= data_in; // Write data to memory
            end
            if (read_enable) begin
                data_out <= memory; // Read data from memory
            end
        end

    end

    always @(*) begin
        // Enable output only during read operation
        output_enable = read_enable;
    end

endmodule