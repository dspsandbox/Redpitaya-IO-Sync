module digital_io #(
    parameter IO_WIDTH = 4,
    localparam INSTR_CMD_WIDTH = 4,
    localparam INSTR_DATA_WIDTH = 32
    
)(
    input clk,
    input resetn,
    input en,
    input instr_valid,
    input [INSTR_CMD_WIDTH-1:0] instr_cmd,
    input [INSTR_DATA_WIDTH-1:0] instr_data,
    output reg [IO_WIDTH-1:0] io_o,
    output reg [IO_WIDTH-1:0] io_t

);
    //cmd format
    localparam CMD_OUTPUT = 'h0, CMD_TRISTATE = 'h1;

    always @(posedge clk) begin
        if(resetn==0) begin
            io_o <= 0;
            io_t <= {IO_WIDTH{1'b1}}; //tristate by default
        end else begin
            if ((en == 1) && (instr_valid==1)) begin
                case(instr_cmd)
                    CMD_OUTPUT: begin
                        io_o <= instr_data[IO_WIDTH-1:0];
                        io_t <= io_t;
                    end
                    CMD_TRISTATE: begin
                        io_o <= io_o;
                        io_t <= instr_data[IO_WIDTH-1:0];
                    end
                    default: begin
                        io_o <= io_o;
                        io_t <= io_t;
                    end
                endcase
            end else begin
                io_o <= io_o;
                io_t <= io_t;
            end
        end
    end

endmodule