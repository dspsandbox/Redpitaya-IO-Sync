PART="xc7z010clg400-1"
IN="project.tcl"
OUT="project_z10.tcl"

cat "$IN" > "$OUT"
echo "set_property part $PART [current_project]" >> "$OUT"
echo "report_ip_status -name ip_status" >> "$OUT"
echo "report_ip_status -name ip_status" >> "$OUT"
echo "upgrade_ip [get_ips *]" >> "$OUT"

vivado -mode batch -source "$OUT"

