module odd_change(
    input wire clk,
    input wire rst,
    output dout
);

    reg delay_line;

    always @(posedge clk) begin
        if (rst) begin
            delay_line <= 1'b0;
        end 
        else begin
            delay_line <= ~delay_line;  
        end
    end

    assign dout = delay_line;

endmodule
