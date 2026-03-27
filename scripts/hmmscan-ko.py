import os
import argparse
from heap.hmm import hmmscan, hmm_results_to_detected_table


if __name__ == "__main__":

    ap = argparse.ArgumentParser()
    ap.add_argument("--query-database-name", required=True)
    ap.add_argument("--query-type", default="protein")
    ap.add_argument("--cpus", default=2)
    ap.add_argument("query_faa")
    ap.add_argument("result_tsv")
    args = ap.parse_args()

    db_dir = os.environ.get("HMM_DB_DIR")
    if db_dir is None:
        raise Exception("Please set HMM_DB_DIR to directory with KO HMM profiles")

    hmm_db = os.path.join(db_dir, "ko.hmm")
    if not os.path.exists(hmm_db):
        raise Exception(f"Cannot find KO HMM profile at {hmm_db}")
    if not os.path.exists(hmm_db+".h3i"):
        raise Exception(f"KO HMM profile {hmm_db} is not pressed")

    results = hmmscan(hmm_db, args.query_faa, cpu=args.cpus, cutoff=False)
    hmm_results_to_detected_table(
        results,
        args.result_tsv,
        args.query_database_name,
        args.query_type,
        "KO",
        "protein",
        "hmmscan"
    )
