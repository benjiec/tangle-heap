import re
import os
import tempfile
import argparse
from heap.foldseek import foldseek_output_to_detected_table
from foldseek import run_foldseek


def accession_rewriter(acc):
    m = re.match(r"^AF\-(\w+)\-.+$", acc)
    if not m:
        raise Exception(f"Don't know how to parse and rewrite {acc}")
    return m.group(1)


if __name__ == "__main__":

    ap = argparse.ArgumentParser()
    ap.add_argument("--query-database-name", required=True)
    ap.add_argument("--query-type", default="protein")
    ap.add_argument("--evalue-threshold", type=float, default=1e-3)
    ap.add_argument("--input-from-foldseek", action="store_true", default=False)
    ap.add_argument("input_fn")
    ap.add_argument("result_tsv")
    args = ap.parse_args()

    db_dir = os.environ.get("FOLDSEEK_DB_DIR")
    if db_dir is None:
        raise Exception("Please set FOLDSEEK_DB_DIR to directory with the SwissProt and Prost-T5 databases")

    target_db = os.path.join(db_dir, "afdb-swissprot")
    prost_db = os.path.join(db_dir, "prost-t5-weights")

    if not os.path.exists(target_db):
        raise Exception(f"Cannot find the afdb-swissprot database at {target_db}")
    if not os.path.exists(prost_db):
        raise Exception(f"Cannot find the prost-t5 database at {prost_db}")

    with tempfile.TemporaryDirectory() as tmpd:
        if args.input_from_foldseek:
            tmpf = args.input_fn
        else:
            tmpf = os.path.join(tmpd, "foldseek-results.tsv")
            run_foldseek(
                args.input_fn,
                target_db,
                prost_db,
                tmpf
            )

        foldseek_output_to_detected_table(
            tmpf,
            args.result_tsv,
            args.query_database_name,
            args.query_type,
            "afdb-swissprot",
            "protein",
            target_accession_rewriter_func = accession_rewriter,
            evalue_threshold = args.evalue_threshold
        )
