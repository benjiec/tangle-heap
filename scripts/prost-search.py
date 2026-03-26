"""
PYTHONPATH=. python3 scripts/prost-search.py \
  --query-database-name a \
  --query-type protein \
  --target-database-name c \
  --target-type protein \
  ~/Downloads/query.faa \
  /Volumes/Extreme_Pro/foldseek/afdb-swissprot \
  /Volumes/Extreme_Pro/foldseek/prost-t5-weights \
  test.tsv
"""

import os
import argparse
import tempfile
import subprocess
from pathlib import Path
from heap import unique_batch
from tangle.detected import DetectedTable


ap = argparse.ArgumentParser()
ap.add_argument("--query-database-name", required=True)
ap.add_argument("--query-type", required=True)
ap.add_argument("--target-database-name", required=True)
ap.add_argument("--target-type", required=True)
ap.add_argument("query_faa")
ap.add_argument("target_db")
ap.add_argument("prost_db")
ap.add_argument("result_tsv")
args = ap.parse_args()


foldseek_docker_image = os.environ.get("FOLDSEEK_DOCKER_IMAGE", "ghcr.io/steineggerlab/foldseek")

query_path = Path(args.query_faa).resolve()
query_dir = query_path.parent
query_fn = query_path.name

target_path = Path(args.target_db).resolve()
target_dir = target_path.parent
target_fn = target_path.name

prost_path = Path(args.prost_db).resolve()
prost_dir = prost_path.parent
prost_fn = prost_path.name

headers = "query,target,evalue,bits,fident,qstart,qend,tstart,tend"
header_array = headers.split(",")


results = []

with tempfile.NamedTemporaryFile(delete=False, suffix=".tsv", mode="w", dir=query_dir) as res_f:
    res_f.close()
    res_fn = Path(res_f.name).name

    cmd = [
      "docker", "run", "--rm",
      "-v", f"{query_dir}:/work",
      "-v", f"{target_dir}:/db",
      "-v", f"{prost_dir}:/prost",
      foldseek_docker_image, "easy-search",
      f"/work/{query_fn}", f"/db/{target_fn}", f"/work/{res_fn}", "/tmp",
      "--format-output", headers,
      "--prostt5-model", f"/prost/{prost_fn}"
    ]
    print(" ".join(cmd))

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        raise e

    with open(res_f.name, "r") as f:
        for line in f:
            res = {header_array[i]:t for i,t in enumerate(line.strip().split('\t'))}
            results.append(res)

    os.remove(res_f.name)

rows = []
for res in results:
    row = {}
    row["detection_type"] = "structure"
    row["detection_method"] = "prost-t5-foldseek"
    row["batch"] = unique_batch()
    row["query_accession"] = res["query"]
    row["query_database"] = args.query_database_name
    row["query_type"] = args.query_type
    row["target_accession"] = res["target"]
    row["target_database"] = args.target_database_name
    row["target_type"] = args.target_type
    row["query_start"] = res["qstart"]
    row["query_end"] = res["qend"]
    row["target_start"] = res["tstart"]
    row["target_end"] = res["tend"]
    row["evalue"] = res["evalue"]
    row["bitscore"] = res["bits"]
    rows.append(row)

DetectedTable.write_tsv(args.result_tsv, rows)
