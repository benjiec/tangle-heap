import os
import argparse
import tempfile
import subprocess
from pathlib import Path
from heap.foldseek import HEADER_STR, foldseek_output_to_detected_table
from tangle import unique_batch
from tangle.detected import DetectedTable


def run_foldseek(
    query_faa,
    target_db,
    prost_db,
    result_tsv,
    query_database_name,
    query_type,
    target_database_name,
    target_type,
    target_accession_rewriter_func = None,
    evalue_threshold = 1e-3
):

    foldseek_docker_image = os.environ.get("FOLDSEEK_DOCKER_IMAGE", "ghcr.io/steineggerlab/foldseek")

    query_path = Path(query_faa).resolve()
    query_dir = query_path.parent
    query_fn = query_path.name

    target_path = Path(target_db).resolve()
    target_dir = target_path.parent
    target_fn = target_path.name

    prost_path = Path(prost_db).resolve()
    prost_dir = prost_path.parent
    prost_fn = prost_path.name


    with tempfile.TemporaryDirectory() as tmpd:
        tmpf = os.path.join(tmpd, "foldseek-results.tsv")
        res_file = Path(tmpf).name
        output_dir = Path(tmpf).parent

        cmd = [
          "docker", "run", "--rm",
          "-v", f"{query_dir}:/input",
          "-v", f"{output_dir}:/output",
          "-v", f"{target_dir}:/db",
          "-v", f"{prost_dir}:/prost",
          foldseek_docker_image, "easy-search",
          f"/input/{query_fn}", f"/db/{target_fn}", f"/output/{res_file}", "/tmp",
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
            tmpf,
            result_tsv,
            query_database_name,
            query_type,
            target_database_name,
            target_type,
            target_accession_rewriter_func = target_accession_rewriter_func,
            evalue_threshold = evalue_threshold
        )


if __name__ == "__main__":

    ap = argparse.ArgumentParser()
    ap.add_argument("--query-database-name", required=True)
    ap.add_argument("--query-type", required=True)
    ap.add_argument("--target-database-name", required=True)
    ap.add_argument("--target-type", required=True)
    ap.add_argument("--evalue-threshold", type=float, default=1e-3)
    ap.add_argument("query_faa")
    ap.add_argument("target_db")
    ap.add_argument("prost_db")
    ap.add_argument("result_tsv")
    args = ap.parse_args()

    run_foldseek(
        args.query_faa,
        args.target_db,
        args.prost_db,
        args.result_tsv,
        args.query_database_name,
        args.query_type,
        args.target_database_name,
        args.target_type,
        evalue_threshold = args.evalue_threshold
    )
