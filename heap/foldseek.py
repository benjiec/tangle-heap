import os
from pathlib import Path
from tangle.detected import DetectedTable
from . import unique_batch


HEADERS = ["query", "target", "evalue", "bits", "qstart", "qend", "tstart", "tend"]
HEADER_STR = ",".join(HEADERS)


def foldseek_output_to_detected_table(
    foldseek_output_fn,
    result_tsv,
    query_database,
    query_type,
    target_database,
    target_type
  ):
    rows = []

    with open(foldseek_output_fn, "r") as f:
        for line in f:
            tsv_tokens = line.strip().split('\t')

            row = {}
            row["detection_type"] = "structure"
            row["detection_method"] = "prost-t5-foldseek"
            row["batch"] = unique_batch()
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
            row["evalue"] = tsv_tokens[HEADERS.index("evalue")]
            row["bitscore"] = tsv_tokens[HEADERS.index("bits")]
            rows.append(row)

    DetectedTable.write_tsv(result_tsv, rows)
