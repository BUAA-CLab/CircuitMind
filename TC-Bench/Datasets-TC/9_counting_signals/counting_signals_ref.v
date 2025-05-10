module counting_signals_ref (
        input wire a,
        input wire b,
        input wire c,
        input wire d,
        output reg [2:0]count 
    );

    always @(*) begin
        count = a + b + c + d;
    end


endmodule
