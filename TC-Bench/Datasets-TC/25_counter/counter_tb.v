module counter_tb(

);
    // Testbench signals
    reg clk;
    reg rst;
    reg mode;
    reg [7:0] write_data;
    wire [7:0] count;

    // Clock generation
    initial begin
        clk = 1;
        forever #5 clk = ~clk; // 10 time units clock period
    end

    initial begin
        $monitor("Time=%0t: mode=%b, write_data=%b, count=%b", $time, mode, write_data, count);
    end

    // Test procedure
    initial begin
        // Initialize signals
        rst = 0;
        mode = 0;
        write_data = 8'b00000000;

        // Test case 1: Reset the counter
        rst = 1;
        rst = 0;

        // Test case 2: Step mode operation
        mode = 0; // Step mode

        // Test case 3: Overwrite mode operation
        mode = 1; // Overwrite mode
        write_data = 8'b10101010;

        // Test case 4: Switch back to step mode
        mode = 0;

        // Test case 5: Overwrite with another value
        mode = 1;
        write_data = 8'b11001100;

        // Finish simulation
        $finish(0);
    end

    // Instantiate the module under test
    counter counter_inst (
        .clk(clk),
        .rst(rst),
        .mode(mode),
        .write_data(write_data),
        .count(count)
    );

endmodule
