import argparse
from heap.hmm import hmmscan, hmm_results_to_detected_table


if __name__ == "__main__":

    ap = argparse.ArgumentParser()
    ap.add_argument("--query-database-name", required=True)
    ap.add_argument("--query-type", required=True)
    ap.add_argument("--target-database-name", required=True)
    ap.add_argument("--target-type", required=True)
    ap.add_argument("--cpus", default=2)
    ap.add_argument("--disable-cutoff", action='store_true', default=False)
    ap.add_argument("query_faa")
    ap.add_argument("target_db")
    ap.add_argument("result_tsv")
    args = ap.parse_args()

    results = hmmscan(args.target_db, args.query_faa, cpu=args.cpus, cutoff=not args.disable_cutoff)
    hmm_results_to_detected_table(
        results,
        args.result_tsv,
        args.query_database_name,
        args.query_type,
        args.target_database_name,
        args.target_type,
        "hmmscan"
    )
