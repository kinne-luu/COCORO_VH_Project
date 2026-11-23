import glob
import os
import re

out_files = sorted(glob.glob("out/scn*.txt"))
print(f"Scanning {len(out_files)} files in out/ for dashes...")

dash_pattern = re.compile(r'(――|——|—|–)')

occurrences = []
for p in out_files:
    fname = os.path.basename(p)
    with open(p, "r", encoding="utf-8") as f:
        for line in f:
            if "|" in line:
                sid, text = line.split("|", 1)
                sid = sid.strip()
                text = text.strip()
                matches = dash_pattern.findall(text)
                if matches:
                    occurrences.append((fname, sid, matches, text))

print(f"Found {len(occurrences)} lines with dashes in out/:")
for fname, sid, matches, text in occurrences[:20]:
    print(f"[{fname}] {sid}: {text}")

if len(occurrences) > 20:
    print(f"... and {len(occurrences) - 20} more.")
