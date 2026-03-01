module scope#(
    parameter DATA_0_WIDTH = 32,
    parameter DATA_1_WIDTH = 32,
    parameter DATA_2_WIDTH = 32,
    parameter DATA_3_WIDTH = 32,
    parameter DATA_4_WIDTH = 32,
    parameter DATA_5_WIDTH = 32,
    parameter DATA_6_WIDTH = 32,
    parameter DATA_7_WIDTH = 32,
    parameter DATA_8_WIDTH = 32,
    parameter DATA_9_WIDTH = 32,
    parameter DATA_10_WIDTH = 32,
    parameter DATA_11_WIDTH = 32,
    parameter DATA_12_WIDTH = 32,
    parameter DATA_13_WIDTH = 32,
    parameter DATA_14_WIDTH = 32,
    parameter DATA_15_WIDTH = 32,
    
    localparam INSTR_CMD_WIDTH = 4,
    localparam INSTR_DATA_WIDTH = 32,
    localparam SCOPE_WIDTH = 16,
    localparam COUNTER_WIDTH = 24

)(
    input clk,
    input resetn,
    input en,
    input flush_fifo,
    input instr_valid,
    input [INSTR_CMD_WIDTH-1:0] instr_cmd,
    input [INSTR_DATA_WIDTH-1:0] instr_data,

    input [DATA_0_WIDTH-1:0] data_0,
    input [DATA_1_WIDTH-1:0] data_1,
    input [DATA_2_WIDTH-1:0] data_2,
    input [DATA_3_WIDTH-1:0] data_3,
    input [DATA_4_WIDTH-1:0] data_4,
    input [DATA_5_WIDTH-1:0] data_5,
    input [DATA_6_WIDTH-1:0] data_6,    
    input [DATA_7_WIDTH-1:0] data_7,
    input [DATA_8_WIDTH-1:0] data_8,
    input [DATA_9_WIDTH-1:0] data_9,
    input [DATA_10_WIDTH-1:0] data_10,
    input [DATA_11_WIDTH-1:0] data_11,
    input [DATA_12_WIDTH-1:0] data_12,
    input [DATA_13_WIDTH-1:0] data_13,
    input [DATA_14_WIDTH-1:0] data_14,
    input [DATA_15_WIDTH-1:0] data_15,
    
    output reg [SCOPE_WIDTH-1:0] scope_tdata,
    output reg scope_tvalid
);

    //instruction commands
    localparam CMD_SRC = 'h0, CMD_ACQ = 'h1;
    reg [COUNTER_WIDTH-1:0] counter;
    reg [COUNTER_WIDTH-1:0] counter_max;
    reg [3 : 0] src;



    always @(posedge clk) begin
        if(resetn == 0) begin
            src <= 0;
            counter_max <= 0;
        end else begin
            if((en==1) && (instr_valid == 1)) begin
                case(instr_cmd)
                    CMD_SRC: begin
                        src <= instr_data[3:0];
                        counter_max <= counter_max;
                    end
                    CMD_ACQ: begin
                        counter_max <= counter_max + instr_data[COUNTER_WIDTH-1:0];
                        src <= src;
                    end
                    default: begin
                        src <= src;
                        counter_max <= counter_max;
                    end
                endcase

            end else begin
                src <= src;
                counter_max <= counter_max;
            end
        end
    end

    
    always @(posedge clk) begin
        if(resetn == 0) begin
            scope_tdata <= 0;
            scope_tvalid <= 0;
        end
        else begin
            //tvalid
            if ((en==1) && (counter != counter_max)) begin
                scope_tvalid <= 1;
                counter <= counter + 1;

            end else begin
                counter <= counter_max;
                scope_tvalid <= 0;
            end

            //tdata
            case(src) 
                0: scope_tdata <= data_0[SCOPE_WIDTH-1:0];
                1: scope_tdata <= data_1[SCOPE_WIDTH-1:0];
                2: scope_tdata <= data_2[SCOPE_WIDTH-1:0];
                3: scope_tdata <= data_3[SCOPE_WIDTH-1:0];
                4: scope_tdata <= data_4[SCOPE_WIDTH-1:0];
                5: scope_tdata <= data_5[SCOPE_WIDTH-1:0];
                6: scope_tdata <= data_6[SCOPE_WIDTH-1:0];
                7: scope_tdata <= data_7[SCOPE_WIDTH-1:0];
                8: scope_tdata <= data_8[SCOPE_WIDTH-1:0];
                9: scope_tdata <= data_9[SCOPE_WIDTH-1:0];
                10: scope_tdata <= data_10[SCOPE_WIDTH-1:0];
                11: scope_tdata <= data_11[SCOPE_WIDTH-1:0];
                12: scope_tdata <= data_12[SCOPE_WIDTH-1:0];
                13: scope_tdata <= data_13[SCOPE_WIDTH-1:0];
                14: scope_tdata <= data_14[SCOPE_WIDTH-1:0];
                15: scope_tdata <= data_15[SCOPE_WIDTH-1:0];
                default: scope_tdata <= 0;
            endcase
        end
    end

endmodule