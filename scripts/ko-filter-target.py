import os
import shutil
import argparse
from heap.ko import filter_detected_by_target_length

if __name__ == "__main__":

    ap = argparse.ArgumentParser()
    ap.add_argument("hmm_result_tsv", nargs="+")
    ap.add_argument("--match-to-threshold-ratio-min", default=0.5, type=float)
    ap.add_argument("--forget-original", action="store_true", default=False)
    args = ap.parse_args()

    db_dir = os.environ.get("HMM_DB_DIR")
    if db_dir is None:
        raise Exception("Please set HMM_DB_DIR to directory with KO HMM profiles")

    ko_threshold = os.path.join(db_dir, "ko_thresholds.tsv")
    if not os.path.exists(ko_threshold):
        raise Exception(f"Cannot find KO threshold TSV at {ko_threshold}")

    for tsv_fn in args.hmm_result_tsv:
        if args.forget_original is False:
            orig_fn = tsv_fn+".orig"
            shutil.copy(tsv_fn, orig_fn)
        filter_detected_by_target_length(tsv_fn, ko_threshold, tsv_fn, min_match_to_threshold_ratio=args.match_to_threshold_ratio_min)
        print(tsv_fn)
