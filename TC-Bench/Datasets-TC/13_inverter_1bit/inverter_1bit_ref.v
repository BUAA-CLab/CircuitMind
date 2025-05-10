module inverter_1bit_ref(
        input wire a,
        input wire inv_signal,
        output wire y
    );

    assign y =inv_signal ^ a;

endmodule
