import duckdb
from . import unique_batch
from tangle.models import Schema, Table, Column, CSVSource
from tangle.detected import DetectedTable


KOThresholdTable = Table("ko_threshold", [
    Column("model"),
    Column("threshold", type=float)
])


def assign_ko(detection_tsv, threshold_tsv, result_tsv, scoring_ratio_min=0.99):

    hmm_csv = CSVSource(DetectedTable, detection_tsv)
    threshold_csv = CSVSource(KOThresholdTable, threshold_tsv)

    schema = Schema("schema_"+unique_batch())
    schema.add_table(hmm_csv)
    schema.add_table(threshold_csv)
    schema.duckdb_load()

    threshold_field = "ko_threshold_value"
    rank_field = "assignment_rank" 

    con = duckdb.connect(":default:")
    sql = f"""
SELECT A.*,
       B.threshold as {threshold_field},
       ROW_NUMBER() OVER (
          PARTITION BY A.query_accession, A.query_database, A.query_type
          ORDER BY A.evalue ASC
      ) as {rank_field}
  FROM {schema.name}.{DetectedTable.name} as A
  JOIN {schema.name}.{KOThresholdTable.name} as B ON A.target_accession = B.model
 WHERE A.bitscore >= B.threshold*{scoring_ratio_min}
 ORDER BY A.query_database, A.query_type, A.query_accession, A.evalue
"""

    data = con.sql(sql).df().to_dict(orient='records')
    rows = []
    for row in data:
        row["bitscore_threshold"] = row[threshold_field]
        row["custom_metric_name"] = "evalue-rank"
        row["custom_metric_value"] = row[rank_field]
        del row[threshold_field]
        del row[rank_field]
        rows.append(row)

    DetectedTable.write_tsv(result_tsv, rows)
