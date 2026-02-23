module analog #(
    localparam AMPL_WIDTH = 16,
    localparam PHASE_WIDTH = 32,
    localparam INSTR_CMD_WIDTH = 4,
    localparam INSTR_DATA_WIDTH = 32
    
)(
    input clk,
    input resetn,
    input en,
    input instr_valid,
    input [INSTR_CMD_WIDTH-1:0] instr_cmd,
    input [INSTR_DATA_WIDTH-1:0] instr_data,
    output reg [AMPL_WIDTH-1:0] ampl,
    output reg [PHASE_WIDTH-1:0] ph_off,
    output reg [PHASE_WIDTH-1:0] ph_inc,
    output reg ph_rst

);

    reg [AMPL_WIDTH-1:0] ampl_reg;
    reg [PHASE_WIDTH-1:0] ph_off_reg;
    reg [PHASE_WIDTH-1:0] ph_inc_reg;
    reg ph_rst_reg;
    reg update_reg;
    
    
    //cmd format
    localparam CMD_PH = 'h0, CMD_PH_RST = 'h1, CMD_FREQ = 'h2, CMD_AMPL = 'h3;

    //Update internal registers based on instruction
    always @(posedge clk) begin
        if resetn == 0 begin
            ph_off_reg <= 0;
            ph_rst_reg <= 0;
            ph_inc_reg <= 0;
            ampl_reg <= 0;
            update_reg <= 0;
        end else begin
            if ((en == 1) && (instr_valid == 1)) begin
                case(instr_cmd[INSTR_CMD_WIDTH-2:0])
                    CMD_PH: begin
                        ph_off_reg <= instr_data[PHASE_WIDTH-1:0];
                        ph_rst_reg <= 0;
                        ph_inc_reg <= ph_inc_reg;
                        ampl_reg <= ampl_reg;
                        update_reg <= instr_cmd[INSTR_CMD_WIDTH-1];
                    end
                    CMD_PH_RST: begin
                        ph_off_reg <= ph_off_reg;
                        ph_rst_reg <= instr_data[0];
                        ph_inc_reg <= ph_inc_reg;
                        ampl_reg <= ampl_reg;
                        update_reg <= instr_cmd[INSTR_CMD_WIDTH-1];
                    end
                    CMD_FREQ: begin
                        ph_off_reg <= ph_off_reg;
                        ph_rst_reg <= 0;
                        ph_inc_reg <= instr_data[PHASE_WIDTH-1:0];
                        ampl_reg <= ampl_reg;
                        update_reg <= instr_cmd[INSTR_CMD_WIDTH-1];
                    end
                    CMD_AMPL: begin
                        ph_off_reg <= ph_off_reg;
                        ph_rst_reg <= 0;
                        ph_inc_reg <= ph_inc_reg;
                        ampl_reg <= instr_data[AMPL_WIDTH-1:0];
                        update_reg <= instr_cmd[INSTR_CMD_WIDTH-1];
                    end
                    default: begin
                        ampl_reg <= ampl_reg;
                        ph_off_reg <= ph_off_reg;
                        ph_inc_reg <= ph_inc_reg;
                        ph_rst_reg <= 0;
                        update_reg <= 0;
                    end
                endcase

            end else begin
                ampl_reg <= ampl_reg;
                ph_off_reg <= ph_off_reg;
                ph_inc_reg <= ph_inc_reg;
                ph_rst_reg <= 0;
                update_reg <= 0;
            end
        end
        
    end


    //Transfer from internal registers to output when UPDATE=1
    always @(posedge clk) begin
        if(resetn==0) begin
            ampl <= 0;
            ph_off <= 0;
            ph_inc <= 0;
            ph_rst <= 0;
            
        end else begin
            if (update_reg == 1) begin
                ampl <= ampl_reg;
                ph_off <= ph_off_reg;
                ph_inc <= ph_inc_reg;
                ph_rst <= ph_rst_reg;
            end else begin
                ampl <= ampl;
                ph_off <= ph_off;
                ph_inc <= ph_inc;
                ph_rst <= ph_rst;
            end

        end
    end
endmodule