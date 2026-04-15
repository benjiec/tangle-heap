import math
import duckdb
import itertools
from tangle import unique_batch
from tangle.models import Schema, Table, Column, CSVSource
from tangle.detected import DetectedTable


KOThresholdTable = Table("ko_threshold", [
    Column("model"),
    Column("threshold", type=float),
    Column("alen", type=int)
])


def filter_detected_by_target_length(detection_tsv, threshold_tsv, output_tsv, target_field=None, min_match_to_threshold_ratio=0.5):
    """
    Keeps only entries in detection_tsv whose total matched target length
    divided by corresponding (by target_model) KO threshold is equal or greater
    than min_match_to_threshold_ratio. I.e. only entries that are likely to be
    assigned or close to assigned to that KO.
    """

    if target_field is None:
        target_field = "target_model"

    hmm_csv = CSVSource(DetectedTable, detection_tsv)
    threshold_csv = CSVSource(KOThresholdTable, threshold_tsv)

    rows = hmm_csv.values()
    thresholds = {t["model"]:t["threshold"] for t in threshold_csv.values()}

    group_f = lambda row: (row["query_accession"], row["query_database"], row["query_type"],
                           row["target_accession"], row["target_database"], row["target_type"])
    rows = sorted(rows, key=group_f)

    keep_rows = []
    for k,group in itertools.groupby(rows, group_f):
        group = list(group)
        total_target_length = sum([abs(row["target_end"]-row["target_start"]) for row in group])
        target_model = group[0][target_field]

        if target_model not in thresholds:
            # print(f"Target model {target_model} not in threshold file, keeping match")
            pass
        else:
            # print(group[0], target_model, total_target_length, thresholds[target_model])
            pass
        
        if target_model not in thresholds or (1.0*total_target_length/thresholds[target_model]) >= min_match_to_threshold_ratio:
            keep_rows.extend(group)

    DetectedTable.write_tsv(output_tsv, keep_rows)


def assign_ko(detection_tsv, threshold_tsv, result_tsv,
              scoring_ratio_min=0.99,
              keep_missing_threshold=False,
              compare_against_alen_if_no_threshold=True,
              append=False):

    hmm_csv = CSVSource(DetectedTable, detection_tsv)
    threshold_csv = CSVSource(KOThresholdTable, threshold_tsv)

    schema = Schema("schema_"+unique_batch())
    schema.add_table(hmm_csv)
    schema.add_table(threshold_csv)
    schema.duckdb_load()

    threshold_field = "ko_threshold_value"
    rank_field = "assignment_rank" 

    conditions = [
        f"(TRY_CAST(B.threshold AS DOUBLE) > 0 AND TRY_CAST(A.bitscore AS DOUBLE) >= TRY_CAST(B.threshold AS DOUBLE) * {scoring_ratio_min})"
    ]
    if keep_missing_threshold:
        conditions.append("(B.threshold IS NULL OR TRY_CAST(B.threshold AS DOUBLE) <= 0)")
    if compare_against_alen_if_no_threshold:
        conditions.append("(TRY_CAST(B.threshold AS DOUBLE) <= 0 AND TRY_CAST(A.bitscore AS DOUBLE) >= TRY_CAST(B.alen AS DOUBLE))")

    for x in conditions:
        assert x.startswith("(") and x.endswith(")")
    condition_sql = " OR ".join(conditions)

    con = duckdb.connect(":default:")
    sql = f"""
SELECT A.*,
       B.threshold as {threshold_field},
       ROW_NUMBER() OVER (
          PARTITION BY A.query_accession, A.query_database, A.query_type
          ORDER BY A.evalue ASC
      ) as {rank_field}
  FROM {schema.name}.{DetectedTable.name} as A
  LEFT JOIN {schema.name}.{KOThresholdTable.name} as B ON (A.target_model = B.model OR A.target_accession = B.model)
 WHERE {condition_sql}
 ORDER BY A.query_database, A.query_type, A.query_accession, A.evalue
"""

    data = con.sql(sql).df().to_dict(orient='records')
    rows = []
    for row in data:
        if row[threshold_field] and not math.isnan(float(row[threshold_field])):
            row["bitscore_threshold"] = row[threshold_field]
            row["custom_metric_name"] = "evalue-rank"
            row["custom_metric_value"] = row[rank_field]
        del row[threshold_field]
        del row[rank_field]
        rows.append(row)

    DetectedTable.write_tsv(result_tsv, rows, append=append)
    schema.duckdb_drop()
