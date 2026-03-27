import os
import tempfile
import unittest

from heap.ko import assign_ko


class TestKOAssignmentLogic(unittest.TestCase):

    def test_finds_entries_above_min_threshold(self):

        with tempfile.TemporaryDirectory() as temp_dir:
            ko_threshold_tsv = os.path.join(temp_dir, "ko_threshold.tsv")
            with open(ko_threshold_tsv, 'w') as f:
                f.write("model	threshold	score_type	profile_type\n")
                f.write("K00001	400.01	domain	trim\n")
                f.write("K00002	200.00	domain	all\n")

            hmm_res_tsv = os.path.join(temp_dir, "results.tsv")
            with open(hmm_res_tsv, 'w') as f:
                f.write("detection_type	detection_method	batch	query_accession	query_database	query_type	target_accession	target_database	target_type	query_start	query_end	target_start	target_end	evalue	bitscore	bitscore_threshold	custom_metric_name	custom_metric_value\n")
                f.write("sequence	hmm	20260327_ff30c5d5	test	a	protein	K00001	KO	protein	60	151	544	628	0.067	400.02			\n")
                f.write("sequence	hmm	20260327_ff30c5d5	test	b	protein	K00001	KO	protein	193	232	552	592	0.01	100			\n")
                f.write("sequence	hmm	20260327_ff30c5d5	test	b	protein	K00002	KO	protein	193	232	552	592	0.1	300			\n")
                f.write("sequence	hmm	20260327_ff30c5d5	test	c	protein	K00002	KO	protein	193	232	552	592	0.1	3			\n")

            assignment_tsv = os.path.join(temp_dir, "assigned.tsv")
            assign_ko(hmm_res_tsv, ko_threshold_tsv, assignment_tsv, scoring_ratio_min=1.0)

            expected = """
detection_type	detection_method	batch	query_accession	query_database	query_type	target_accession	target_database	target_type	query_start	query_end	target_start	target_end	evalue	bitscore	bitscore_threshold	custom_metric_name	custom_metric_value
sequence	hmm	20260327_ff30c5d5	test	a	protein	K00001	KO	protein	60	151	544	628	0.067	400.02	400.01	evalue-rank	1.0
sequence	hmm	20260327_ff30c5d5	test	b	protein	K00002	KO	protein	193	232	552	592	0.1	300.0	200.0	evalue-rank	1.0
"""

            with open(assignment_tsv, "r") as f:
                self.maxDiff = None
                self.assertEqual(f.read().strip(), expected.strip())

    def test_can_adjust_min_scoring_ratio(self):

        with tempfile.TemporaryDirectory() as temp_dir:
            ko_threshold_tsv = os.path.join(temp_dir, "ko_threshold.tsv")
            with open(ko_threshold_tsv, 'w') as f:
                f.write("model	threshold	score_type	profile_type\n")
                f.write("K00001	400.01	domain	trim\n")
                f.write("K00002	200.00	domain	all\n")

            hmm_res_tsv = os.path.join(temp_dir, "results.tsv")
            with open(hmm_res_tsv, 'w') as f:
                f.write("detection_type	detection_method	batch	query_accession	query_database	query_type	target_accession	target_database	target_type	query_start	query_end	target_start	target_end	evalue	bitscore	bitscore_threshold	custom_metric_name	custom_metric_value\n")
                f.write("sequence	hmm	20260327_ff30c5d5	test	a	protein	K00001	KO	protein	60	151	544	628	0.067	400.02			\n")
                f.write("sequence	hmm	20260327_ff30c5d5	test	b	protein	K00001	KO	protein	193	232	552	592	0.01	100			\n")
                f.write("sequence	hmm	20260327_ff30c5d5	test	b	protein	K00002	KO	protein	193	232	552	592	0.1	300			\n")

            assignment_tsv = os.path.join(temp_dir, "assigned.tsv")
            assign_ko(hmm_res_tsv, ko_threshold_tsv, assignment_tsv, scoring_ratio_min=0.24)

            expected = """
detection_type	detection_method	batch	query_accession	query_database	query_type	target_accession	target_database	target_type	query_start	query_end	target_start	target_end	evalue	bitscore	bitscore_threshold	custom_metric_name	custom_metric_value
sequence	hmm	20260327_ff30c5d5	test	a	protein	K00001	KO	protein	60	151	544	628	0.067	400.02	400.01	evalue-rank	1.0
sequence	hmm	20260327_ff30c5d5	test	b	protein	K00001	KO	protein	193	232	552	592	0.01	100.0	400.01	evalue-rank	1.0
sequence	hmm	20260327_ff30c5d5	test	b	protein	K00002	KO	protein	193	232	552	592	0.1	300.0	200.0	evalue-rank	2.0
"""

            with open(assignment_tsv, "r") as f:
                self.maxDiff = None
                self.assertEqual(f.read().strip(), expected.strip())

    def test_separately_rank_by_each_query_accession(self):

        with tempfile.TemporaryDirectory() as temp_dir:
            ko_threshold_tsv = os.path.join(temp_dir, "ko_threshold.tsv")
            with open(ko_threshold_tsv, 'w') as f:
                f.write("model	threshold	score_type	profile_type\n")
                f.write("K00001	400.01	domain	trim\n")
                f.write("K00002	200.00	domain	all\n")

            hmm_res_tsv = os.path.join(temp_dir, "results.tsv")
            with open(hmm_res_tsv, 'w') as f:
                f.write("detection_type	detection_method	batch	query_accession	query_database	query_type	target_accession	target_database	target_type	query_start	query_end	target_start	target_end	evalue	bitscore	bitscore_threshold	custom_metric_name	custom_metric_value\n")
                f.write("sequence	hmm	20260327_ff30c5d5	test	a	protein	K00001	KO	protein	60	151	544	628	0.03	600			\n")
                f.write("sequence	hmm	20260327_ff30c5d5	test	a	protein	K00002	KO	protein	60	151	544	628	0.02	500			\n")
                f.write("sequence	hmm	20260327_ff30c5d5	test	b	protein	K00001	KO	protein	193	232	552	592	0.01	100			\n")
                f.write("sequence	hmm	20260327_ff30c5d5	test	b	protein	K00002	KO	protein	193	232	552	592	0.1	300			\n")

            assignment_tsv = os.path.join(temp_dir, "assigned.tsv")
            assign_ko(hmm_res_tsv, ko_threshold_tsv, assignment_tsv, scoring_ratio_min=0)

            expected = """
detection_type	detection_method	batch	query_accession	query_database	query_type	target_accession	target_database	target_type	query_start	query_end	target_start	target_end	evalue	bitscore	bitscore_threshold	custom_metric_name	custom_metric_value
sequence	hmm	20260327_ff30c5d5	test	a	protein	K00002	KO	protein	60	151	544	628	0.02	500.0	200.0	evalue-rank	1.0
sequence	hmm	20260327_ff30c5d5	test	a	protein	K00001	KO	protein	60	151	544	628	0.03	600.0	400.01	evalue-rank	2.0
sequence	hmm	20260327_ff30c5d5	test	b	protein	K00001	KO	protein	193	232	552	592	0.01	100.0	400.01	evalue-rank	1.0
sequence	hmm	20260327_ff30c5d5	test	b	protein	K00002	KO	protein	193	232	552	592	0.1	300.0	200.0	evalue-rank	2.0
"""

            with open(assignment_tsv, "r") as f:
                self.maxDiff = None
                self.assertEqual(f.read().strip(), expected.strip())
