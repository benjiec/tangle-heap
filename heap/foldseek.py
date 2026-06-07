import os
import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from pathlib import Path
from tangle import unique_batch
from tangle.detected import DetectedTable


class DataClusteringProcessor(object):
    """
    Groups data using DBSCAN to avoid bin-boundary artifacts.
    Processes data per-query to maintain modularity and performance.
    """
    
    def __init__(self, group_col, feature_cols, log_cols, sort_bits_col):
        self.df = None
        self.group_col = group_col
        self.feature_cols = feature_cols
        self.log_cols = log_cols
        self.sort_bits_col = sort_bits_col

    def _cluster_group(self, group, feature_cols, log_cols, sort_bits_col, eps):
        """Applies DBSCAN to a single query group."""
        if len(group) <= 1:
            return group

        # Prepare features: Log-transform e-values if present
        data_to_fit = group[feature_cols].copy()
        for col in data_to_fit.columns:
            if col in log_cols:
                data_to_fit[col] = np.log10(data_to_fit[col].replace(0, 1e-300))

        # Standardize features (Z-score) so distance is relative to variance
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(data_to_fit)

        # epsilon (eps) is the max distance between two samples for one to be 
        # considered as in the neighborhood of the other.
        db = DBSCAN(eps=eps, min_samples=1).fit(scaled_data)
        
        group['cluster_id'] = db.labels_
        
        # Representative selection: Sort by bits (assumed 4th col) and keep top per cluster
        # Replace 'bits' with your ranking column name
        return group.sort_values(sort_bits_col, ascending=False).drop_duplicates('cluster_id')

    def process(self, df, eps: float = 0.5):
        """Iterates through queries and collapses clusters."""

        clustered_groups = []
        grouped = df.groupby(self.group_col, sort=False)
        
        for name, group in grouped:
            refined_group = self._cluster_group(group, self.feature_cols, self.log_cols, self.sort_bits_col, eps)
            clustered_groups.append(refined_group)

        self.df = pd.concat(clustered_groups)
        return self.df


class DataContainmentProcessor:
    """Handles geometric filtering of nested intervals based on significance."""

    def __init__(self, group_col, qstart_col, qend_col, evalue_col):
        self.query_col = group_col
        self.qs = qstart_col
        self.qe = qend_col
        self.ev = evalue_col
        self.df = None

    def process(self, df):
        grouped = df.groupby(self.query_col, group_keys=False, sort=False)
        filtered_df = grouped.apply(self._filter_contained)
        filtered_df = filtered_df.reset_index()
        self.df = filtered_df
        return self.df

    def _filter_contained(self, group):
        query_value = group.name

        if len(group) <= 1:
            return group.assign(**{self.query_col: query_value}) 

        # Primary sort by evalue (significance), secondary by interval span
        group = group.sort_values(by=[self.ev, self.qs])

        rows = group[[self.qs, self.qe]].values
        keep = np.ones(len(rows), dtype=bool)
        
        for i in range(len(rows)):
            if not keep[i]: continue
            a_start, a_end = rows[i]
            
            for j in range(i + 1, len(rows)):
                if not keep[j]: continue
                b_start, b_end = rows[j]
                
                # Condition: B is fully contained within A
                if a_start <= b_start and a_end >= b_end:
                    keep[j] = False

        result = group[keep].copy()
        result[self.query_col] = query_value
        return result


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
    batch = None,
    filter_by_query = True
  ):

    df = pd.read_csv(foldseek_output_fn, sep='\t', names=HEADERS)

    if filter_by_query:
        cluster_proc = DataClusteringProcessor("query", ["qstart", "qend", "bits", "evalue"], ["evalue"], "bits")
        contain_proc = DataContainmentProcessor("query", "qstart", "qend", "evalue")
        cluster_proc.process(df)
        contain_proc.process(cluster_proc.df)
        fsrows = contain_proc.df.to_dict(orient='records')
    else:
        fsrows = df.to_dict(orient='records')

    batch = unique_batch() if batch is None else batch

    rows = []
    for fsrow in fsrows:
        row = {}
        row["detection_type"] = "sequence"
        row["detection_method"] = "prost-t5-foldseek"
        row["batch"] = batch
        row["query_accession"] = fsrow["query"]
        row["query_database"] = query_database
        row["query_type"] = query_type
        row["target_accession"] = fsrow["target"]
        row["target_database"] = target_database
        row["target_type"] = target_type
        row["query_start"] = fsrow["qstart"]
        row["query_end"] = fsrow["qend"]
        row["target_start"] = fsrow["tstart"]
        row["target_end"] = fsrow["tend"]
        row["evalue"] = fsrow["evalue"]
        row["bitscore"] = fsrow["bits"]

        if target_accession_rewriter_func is not None:
            row["target_accession"] = target_accession_rewriter_func(row["target_accession"])

        if evalue_threshold is None or float(row["evalue"]) < evalue_threshold:
            rows.append(row)

    DetectedTable.write_tsv(result_tsv, rows)
