import os
import argparse
from heap.ko import assign_ko


if __name__ == "__main__":

    ap = argparse.ArgumentParser()
    ap.add_argument("hmm_result_tsv")
    ap.add_argument("assigned_tsv")
    ap.add_argument("--scoring-ratio-min", default=0.99, type=float)
    args = ap.parse_args()

    db_dir = os.environ.get("HMM_DB_DIR")
    if db_dir is None:
        raise Exception("Please set HMM_DB_DIR to directory with KO HMM profiles")

    ko_threshold = os.path.join(db_dir, "ko_thresholds.tsv")
    if not os.path.exists(ko_threshold):
        raise Exception(f"Cannot find KO threshold TSV at {ko_threshold}")

    assign_ko(args.hmm_result_tsv, ko_threshold, args.assigned_tsv, scoring_ratio_min=args.scoring_ratio_min)
