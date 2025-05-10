module box_ref(
        input clk,
        input rst,
        input read_enable,
        input write_enable,
        input [7:0] write_data,
        input [1:0] address,

        output reg [7:0] read_data,
        output reg read_active
    );

    // Define 4 registers, each 8-bit wide
    reg [7:0] registers [3:0];

    always @(posedge clk) begin
        if(rst) begin
            registers[0] <= 8'b00000000;
            registers[1] <= 8'b00000000;
            registers[2] <= 8'b00000000;
            registers[3] <= 8'b00000000;
            read_data <= 8'b00000000;
            read_active <= 1'b0;
        end
        else begin
            if(write_enable) begin
                registers[address] <= write_data;
            end
            if(read_enable) begin
                read_data <= registers[address];
                read_active <= 1'b1;
            end
            else begin
                read_active <= 1'b0;
            end
        end
    end

endmodule
