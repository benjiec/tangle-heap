# extracts PF matches from protein2ipr.dat.gz file downloaded from
# UniProt/InterPro FTP site, into detected table

# first use this command to just extract the PF entries
#
# gzcat protein2ipr.dat.gz| awk -F'\t' '$4 ~ "PF"' - > protein-pfam.txt
#
# then call this script

import argparse
from heap import unique_batch
from tangle.detected import DetectedTable

ap = argparse.ArgumentParser()
ap.add_argument("ipr_pfam_file")
ap.add_argument("detected_tsv")
args = ap.parse_args()

rows = []
batch = unique_batch()

with open(args.ipr_pfam_file, "r") as f:
    for line in f:
        tokens = line.split("\t")
        query_accession = tokens[0]
        target_accession = tokens[3]
        query_start = tokens[4]
        query_end = tokens[5]

        row = dict(
            detection_type="sequence",
            detection_method="hmm",
            batch=batch,
            query_accession=query_accession,
            query_database="SwissProt",
            query_type="protein",
            target_accession=target_accession,
            target_database="Pfam-A",
            target_type="protein",
            query_start=query_start,
            query_end=query_end
        )
        rows.append(row)

    DetectedTable.write_tsv(args.detected_tsv, rows)
