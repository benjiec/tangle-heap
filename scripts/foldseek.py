"""
PYTHONPATH=. python3 scripts/foldseek.py \
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
from heap.foldseek import HEADER_STR, foldseek_output_to_detected_table
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


with tempfile.NamedTemporaryFile(delete=False, suffix=".tsv", mode="w", dir=query_dir) as res_f:
    res_f.close()
    res_file = Path(res_f.name).name

    cmd = [
      "docker", "run", "--rm",
      "-v", f"{query_dir}:/work",
      "-v", f"{target_dir}:/db",
      "-v", f"{prost_dir}:/prost",
      foldseek_docker_image, "easy-search",
      f"/work/{query_fn}", f"/db/{target_fn}", f"/work/{res_file}", "/tmp",
      "--format-output", HEADER_STR,
      "--prostt5-model", f"/prost/{prost_fn}"
    ]
    print(" ".join(cmd))

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        raise e

    foldseek_output_to_detected_table(
        res_f.name,
        args.result_tsv,
        args.query_database_name,
        args.query_type,
        args.target_database_name,
        args.target_type
    )

    os.remove(res_f.name)
