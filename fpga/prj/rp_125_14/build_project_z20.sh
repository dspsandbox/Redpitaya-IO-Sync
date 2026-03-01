FROM="xc7z010clg400-1"
TO="xc7z020clg400-1"
IN="project.tcl"
OUT="project_z20.tcl"

sed "s/${FROM}/${TO}/g" "$IN" > "$OUT"
vivado -mode batch -source "$OUT"

