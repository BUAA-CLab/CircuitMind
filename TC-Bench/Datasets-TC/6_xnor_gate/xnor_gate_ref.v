module xnor_gate_ref(
        input wire a,
        input wire b,
        output wire y
    );

    assign y = ~(a ^ b);

endmodule
