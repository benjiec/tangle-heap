import re
import os
import tempfile
import subprocess
from dataclasses import dataclass
from typing import List
from Bio import SearchIO
from tangle import unique_batch
from tangle.detected import DetectedTable


def run_command(cmd: str):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def parse_hmm_domtbl(domtbl_path):
    expected_header = "# target name  accession  tlen  query name  accession  qlen  E-value  score  bias  #  of  c-Evalue  i-Evalue  score  bias  from  to  from  to"
    idx_target = 0
    idx_target_acc = 1
    idx_t_len = 2
    idx_query = 3
    idx_query_acc = 4
    idx_q_len = 5
    idx_seq_eval = 6
    idx_seq_score = 7
    idx_dom_eval_cond = 11
    idx_dom_eval = 12
    idx_dom_score = 13
    idx_h_from = 15
    idx_h_to = 16
    idx_a_from = 17
    idx_a_to = 18

    # first, sanity check these indices
    expected_header_parts = re.split(r'\s\s+', expected_header)
    assert expected_header_parts[idx_target] == "# target name"
    assert expected_header_parts[idx_target_acc] == "accession"
    assert expected_header_parts[idx_t_len] == "tlen"
    assert expected_header_parts[idx_query] == "query name"
    assert expected_header_parts[idx_query_acc] == "accession"
    assert expected_header_parts[idx_q_len] == "qlen"
    assert expected_header_parts[idx_seq_eval] == "E-value"
    assert expected_header_parts[idx_seq_score] == "score"
    assert expected_header_parts[idx_dom_eval_cond] == "c-Evalue"
    assert expected_header_parts[idx_dom_eval] == "i-Evalue"
    assert expected_header_parts[idx_dom_score] == "score"
    assert expected_header_parts[idx_h_from] == "from"
    assert expected_header_parts[idx_h_to] == "to"
    assert expected_header_parts[idx_a_from] == "from"
    assert expected_header_parts[idx_a_to] == "to"

    has_headers = False
    expected_header = " ".join(expected_header.split())

    matches = []
    with open(domtbl_path, "r") as domf:
        for line in domf:
            if " ".join(line.split()).startswith(expected_header):
                has_headers = True
            if not line or line.startswith("#") or has_headers is False:
                continue
            parts = line.strip().split()
            match = dict(
                target_name = parts[idx_target],
                target_accession = parts[idx_target_acc],
                query_name = parts[idx_query],
                query_accession = parts[idx_query_acc],
                seq_evalue = float(parts[idx_seq_eval]),
                seq_score = float(parts[idx_seq_score]),
                dom_evalue = float(parts[idx_dom_eval]),
                dom_evalue_cond = float(parts[idx_dom_eval_cond]),
                dom_score = float(parts[idx_dom_score]),
                query_length = int(parts[idx_q_len]),
                hmm_from = int(parts[idx_h_from]),
                hmm_to = int(parts[idx_h_to]),
                target_length = int(parts[idx_t_len]),
                ali_from = int(parts[idx_a_from]),
                ali_to = int(parts[idx_a_to])
            )
            matches.append(match)

    assert has_headers
    return matches


def hmmscan(hmm_file_name, fasta_path, cutoff=True, cpu=None):
    with tempfile.TemporaryDirectory() as tmpdir:
        domtbl_path = os.path.join(tmpdir, "out.domtbl")
        cmd = ["hmmscan"]
        if cpu is not None:
            cmd.extend(["--cpu", str(cpu)])
        if cutoff:
            cmd.append("--cut_ga")
        cmd.extend(["--domtblout", domtbl_path, hmm_file_name, fasta_path])
        run_command(cmd)
        return parse_hmm_domtbl(domtbl_path)


def hmm_results_to_detected_table(
    results,
    result_tsv,
    query_database,
    query_type,
    target_database,
    target_type,
    hmm_mode,
    batch=None
  ):

    assert hmm_mode in ("hmmscan", "hmmsearch")

    rows = []
    batch = unique_batch() if batch is None else batch

    for res in results:
        row = {}
        row["detection_type"] = "sequence"
        row["detection_method"] = "hmm"
        row["batch"] = batch
        row["query_database"] = query_database
        row["query_type"] = query_type
        row["target_database"] = target_database
        row["target_type"] = target_type

        if hmm_mode == "hmmscan":
            row["query_accession"] = res["query_accession"].strip() if res["query_accession"].strip() not in ("-", "") else res["query_name"].strip()
            row["target_accession"] = res["target_accession"].strip() if res["target_accession"].strip() not in ("-", "") else res["target_name"].strip()
            row["query_start"] = res["ali_from"]
            row["query_end"] = res["ali_to"]
            row["target_start"] = res["hmm_from"]
            row["target_end"] = res["hmm_to"]
        else:
            row["target_accession"] = res["query_accession"].strip() if res["query_accession"].strip() != "-" else res["query_name"].strip()
            row["query_accession"] = res["target_accession"].strip() if res["target_accession"].strip() != "-" else res["target_name"].strip()
            row["query_start"] = res["hmm_from"]
            row["query_end"] = res["hmm_to"]
            row["target_start"] = res["ali_from"]
            row["target_end"] = res["ali_to"]

        row["evalue"] = res["dom_evalue"]
        row["bitscore"] = res["dom_score"]
        rows.append(row)

    DetectedTable.write_tsv(result_tsv, rows)
