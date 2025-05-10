module elegant_storage_ref(
        input clk,
        input write_enable,       // Write enable signal
        input [7:0] data_in,      // Data input for writing
        output reg [7:0] data_out // Data output, always reflects stored value
    );

    reg [7:0] memory; // 8-bit memory storage

    always @(posedge clk) begin
        if (write_enable) begin
            memory <= data_in; // Overwrite stored data
        end
        
    end

    always @(posedge clk) begin
        data_out <= memory; // Output current stored value
    end

endmodule