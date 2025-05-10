module odd_change_ref(
        input wire clk,
        input wire rst,
        output wire dout
    );

    reg delay_line;
    reg initial_state; // 新增寄存器：initial_state

    always @(posedge clk) begin
        if (rst) begin
            delay_line <= 1'b0;      // 复位时：delay_line 置为 0
            initial_state <= 1'b1; // 复位时：initial_state 置为 1 (关键修改)
        end
        else begin
            delay_line <= ~delay_line;
            if (initial_state) begin
                delay_line <= 1'b0; // 复位释放后第一个周期：强制 delay_line 为 0
                initial_state <= 1'b0; // 复位后第一个周期：清除 initial_state 标志
            end
        end
    end

    assign dout = delay_line;

endmodule