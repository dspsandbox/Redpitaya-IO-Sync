IN="project.tcl"
OUT="project_z10.tcl"

cp "$IN" "$OUT"
vivado -mode batch -source "$OUT"

