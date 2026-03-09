module stream_ctrl #(
    parameter DATA_WIDTH = 16,
    localparam SAMPLES_WIDTH = 32
)(
    input clk,
    input resetn,
    input err_i, 
    output err_o,
    input en,
    input [SAMPLES_WIDTH-1:0] samples_total,
    input trig, 
    input [SAMPLES_WIDTH-1:0] samples,
    input [DATA_WIDTH - 1 : 0] stream_i_tdata,
    input stream_i_tvalid,
    output stream_i_tready,
    output [DATA_WIDTH - 1 : 0] stream_o_tdata,
    output stream_o_tvalid,
    output stream_o_tlast,
    input stream_o_tready
);
    
    localparam IDLE=0, RUNNING=1, ERROR=2;
    reg [0 : 1] state;
    reg [SAMPLES_WIDTH-1 : 0] counter;
    reg [SAMPLES_WIDTH-1 : 0] counter_total;
    
    


    always @(posedge clk) begin
        if ((resetn == 0) || (en == 0)) begin
            state <= IDLE;
            counter <= 1;
            counter_total <= 1;
            
        end else begin
            case(state)
                IDLE: begin
                    counter <= 1;
                    if(trig == 1) begin
                        state <= RUNNING;
                    end 
                end

                RUNNING: begin 
                    if((trig == 1) || ((stream_i_tvalid == 1) && (stream_o_tready == 0))) begin
                        state <= ERROR;
                    end else begin
                        if((stream_i_tvalid == 1) && (stream_o_tready == 1)) begin
                            counter <= counter + 1;
                            counter_total <= counter_total + 1;
                            if(counter == samples) begin
                                state <= IDLE;
                            end
                        end
                    end
                end

                ERROR: begin
                    state <= ERROR;  //Stay in error state until reset or disable
                end

                default: begin
                    state <= IDLE;
                end 
            endcase
        end
    end

    assign stream_o_tdata = stream_i_tdata;
    assign stream_o_tvalid = (state == RUNNING) ? stream_i_tvalid : 0;
    assign stream_i_tready = (state == RUNNING) ? stream_o_tready : 0;
    assign stream_o_tlast = ((state == RUNNING) && (counter_total == samples_total)) ? 1 : 0;
    assign err_o = (state == ERROR) || (err_i == 1) ? 1 : 0;

endmodule


