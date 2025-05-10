`timescale 1ns / 1ps

module adder_8bit_tb(

);

    // Testbench signals
    reg  [7:0] a;
    reg  [7:0] b;
    reg        carry_in;

    wire [7:0] sum;
    wire       carry_out;

    initial begin
        $monitor("Time=%0t: a=%b, b=%b, carry_in=%b, sum=%b, carry_out=%b", $time, a, b, carry_in, sum, carry_out);
    end

    // Testbench process
    initial begin
        // Test case 1: 0 + 0 + 0
        a = 8'b00000000; b = 8'b00000000; carry_in = 1'b0;

        // Test case 2: 255 + 1 + 0
        a = 8'b11111111; b = 8'b00000001; carry_in = 1'b0;

        // Test case 3: 128 + 128 + 0
        a = 8'b10000000; b = 8'b10000000; carry_in = 1'b0;

        // Test case 4: 127 + 127 + 1
        a = 8'b01111111; b = 8'b01111111; carry_in = 1'b1;

        // Test case 5: 200 + 55 + 1
        a = 8'b11001000; b = 8'b00110111; carry_in = 1'b1;

        // Test case 6: 0 + 255 + 1
        a = 8'b00000000; b = 8'b11111111; carry_in = 1'b1;

        // Finish simulation
        $finish(0);
    end

    // Instantiate the DUT (Device Under Test)
    adder_8bit adder_8bit_inst (
        .a(a),
        .b(b),
        .carry_in(carry_in),
        .sum(sum),
        .carry_out(carry_out)
    );

endmodule
