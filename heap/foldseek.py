import os
from pathlib import Path
from tangle import unique_batch
from tangle.detected import DetectedTable


HEADERS = ["query", "target", "evalue", "bits", "qstart", "qend", "tstart", "tend"]
HEADER_STR = ",".join(HEADERS)


def foldseek_output_to_detected_table(
    foldseek_output_fn,
    result_tsv,
    query_database,
    query_type,
    target_database,
    target_type,
    target_accession_rewriter_func = None,
    evalue_threshold = None,
    batch = None
  ):

    rows = []
    batch = unique_batch() if batch is None else batch

    with open(foldseek_output_fn, "r") as f:
        for line in f:
            tsv_tokens = line.strip().split('\t')

            row = {}
            row["detection_type"] = "sequence"
            row["detection_method"] = "prost-t5-foldseek"
            row["batch"] = batch
            row["query_accession"] = tsv_tokens[HEADERS.index("query")]
            row["query_database"] = query_database
            row["query_type"] = query_type
            row["target_accession"] = tsv_tokens[HEADERS.index("target")]
            row["target_database"] = target_database
            row["target_type"] = target_type
            row["query_start"] = tsv_tokens[HEADERS.index("qstart")]
            row["query_end"] = tsv_tokens[HEADERS.index("qend")]
            row["target_start"] = tsv_tokens[HEADERS.index("tstart")]
            row["target_end"] = tsv_tokens[HEADERS.index("tend")]
            row["evalue"] = float(tsv_tokens[HEADERS.index("evalue")])
            row["bitscore"] = float(tsv_tokens[HEADERS.index("bits")])

            if target_accession_rewriter_func is not None:
                row["target_accession"] = target_accession_rewriter_func(row["target_accession"])

            if evalue_threshold is None or row["evalue"] < evalue_threshold:
                rows.append(row)

    DetectedTable.write_tsv(result_tsv, rows)
