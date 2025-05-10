module and3_gate_ref(
        input wire a,
        input wire b,
        input wire c,
        output wire y
    );

    assign y = a & b & c;

endmodule
