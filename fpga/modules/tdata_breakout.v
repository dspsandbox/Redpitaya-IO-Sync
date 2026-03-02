module tdata_breakout #(
    parameter DATA_WIDTH = 32
)(
    input clk,
    input resetn,
    input S00_AXIS_tvalid,
    input [DATA_WIDTH-1:0] S00_AXIS_tdata,
    input [DATA_WIDTH-1:0] S00_AXIS_tlast,
    output S00_AXIS_tready,

    output M00_AXIS_tvalid,
    output [DATA_WIDTH-1:0] M00_AXIS_tdata,
    output [DATA_WIDTH-1:0] M00_AXIS_tlast,
    input M00_AXIS_tready,

    output[DATA_WIDTH-1:0] tdata
);

    assign S00_AXIS_tready = M00_AXIS_tready;
    assign M00_AXIS_tvalid = S00_AXIS_tvalid;
    assign M00_AXIS_tdata = S00_AXIS_tdata;
    assign M00_AXIS_tlast = S00_AXIS_tlast;

    assign tdata = S00_AXIS_tdata;

    endmodule