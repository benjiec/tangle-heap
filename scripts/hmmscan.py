import os
import argparse
from heap.hmm import hmmscan, hmm_results_to_detected_table


if __name__ == "__main__":

    ap = argparse.ArgumentParser()
    ap.add_argument("--query-database-name", required=True)
    ap.add_argument("--query-type", default="protein")
    ap.add_argument("--target-database-name", required=True)
    ap.add_argument("--target-type", default="protein")
    ap.add_argument("--cpus", default=2)
    ap.add_argument("hmm_db")
    ap.add_argument("query_faa")
    ap.add_argument("result_tsv")
    args = ap.parse_args()

    hmm_db = args.hmm_db
    if not os.path.exists(hmm_db+".h3i"):
        raise Exception(f"Cannot find pressed HMM profile at {hmm_db}")

    results = hmmscan(hmm_db, args.query_faa, cpu=args.cpus, cutoff=False)
    hmm_results_to_detected_table(
        results,
        args.result_tsv,
        args.query_database_name,
        args.query_type,
        args.target_database_name,
        args.target_type,
        "hmmscan"
    )
