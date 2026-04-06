import os
import tempfile
import unittest

from heap.ko import assign_ko, filter_detected_by_target_length
from tangle.detected import DetectedTable
from tangle.models import CSVSource


class TestKOAssignmentLogic(unittest.TestCase):

    def test_finds_entries_above_min_threshold_by_target_model(self):

        with tempfile.TemporaryDirectory() as temp_dir:
            ko_threshold_tsv = os.path.join(temp_dir, "ko_threshold.tsv")
            with open(ko_threshold_tsv, 'w') as f:
                f.write("model	threshold	score_type	profile_type\n")
                f.write("K00001	400.01	domain	trim\n")
                f.write("K00002	200.00	domain	all\n")

            hmm_res_tsv = os.path.join(temp_dir, "results.tsv")
            with open(hmm_res_tsv, 'w') as f:
                f.write("detection_type	detection_method	batch	query_accession	query_database	query_type	target_accession	target_database	target_type	target_model	query_start	query_end	target_start	target_end	evalue	bitscore	bitscore_threshold	custom_metric_name	custom_metric_value\n")
                f.write("sequence	hmm	20260327_ff30c5d5	test	a	protein	x	KO	protein	K00001	60	151	544	628	0.067	400.02			\n")
                f.write("sequence	hmm	20260327_ff30c5d5	test	b	protein	y	KO	protein	K00001	193	232	552	592	0.01	100			\n")
                f.write("sequence	hmm	20260327_ff30c5d5	test	b	protein	z	KO	protein	K00002	193	232	552	592	0.1	300			\n")
                f.write("sequence	hmm	20260327_ff30c5d5	test	c	protein	w	KO	protein	K00002	193	232	552	592	0.1	3			\n")

            assignment_tsv = os.path.join(temp_dir, "assigned.tsv")
            assign_ko(hmm_res_tsv, ko_threshold_tsv, assignment_tsv, scoring_ratio_min=1.0)

            expected = """
detection_type	detection_method	batch	query_accession	query_database	query_type	target_accession	target_database	target_type	target_model	query_start	query_end	target_start	target_end	evalue	bitscore	bitscore_threshold	custom_metric_name	custom_metric_value
sequence	hmm	20260327_ff30c5d5	test	a	protein	x	KO	protein	K00001	60	151	544	628	0.067	400.02	400.01	evalue-rank	1.0
sequence	hmm	20260327_ff30c5d5	test	b	protein	z	KO	protein	K00002	193	232	552	592	0.1	300.0	200.0	evalue-rank	1.0
"""

            with open(assignment_tsv, "r") as f:
                self.maxDiff = None
                self.assertEqual(f.read().strip(), expected.strip())

    def test_finds_entries_above_min_threshold_by_target_accession(self):

        with tempfile.TemporaryDirectory() as temp_dir:
            ko_threshold_tsv = os.path.join(temp_dir, "ko_threshold.tsv")
            with open(ko_threshold_tsv, 'w') as f:
                f.write("model	threshold	score_type	profile_type\n")
                f.write("K00001	400.01	domain	trim\n")
                f.write("K00002	200.00	domain	all\n")

            hmm_res_tsv = os.path.join(temp_dir, "results.tsv")
            with open(hmm_res_tsv, 'w') as f:
                f.write("detection_type	detection_method	batch	query_accession	query_database	query_type	target_accession	target_database	target_type	target_model	query_start	query_end	target_start	target_end	evalue	bitscore	bitscore_threshold	custom_metric_name	custom_metric_value\n")
                f.write("sequence	hmm	20260327_ff30c5d5	test	a	protein	K00001	KO	protein		60	151	544	628	0.067	400.02			\n")
                f.write("sequence	hmm	20260327_ff30c5d5	test	b	protein	K00001	KO	protein		193	232	552	592	0.01	100			\n")
                f.write("sequence	hmm	20260327_ff30c5d5	test	b	protein	K00002	KO	protein		193	232	552	592	0.1	300			\n")
                f.write("sequence	hmm	20260327_ff30c5d5	test	c	protein	K00002	KO	protein		193	232	552	592	0.1	3			\n")

            assignment_tsv = os.path.join(temp_dir, "assigned.tsv")
            assign_ko(hmm_res_tsv, ko_threshold_tsv, assignment_tsv, scoring_ratio_min=1.0)

            expected = """
detection_type	detection_method	batch	query_accession	query_database	query_type	target_accession	target_database	target_type	target_model	query_start	query_end	target_start	target_end	evalue	bitscore	bitscore_threshold	custom_metric_name	custom_metric_value
sequence	hmm	20260327_ff30c5d5	test	a	protein	K00001	KO	protein		60	151	544	628	0.067	400.02	400.01	evalue-rank	1.0
sequence	hmm	20260327_ff30c5d5	test	b	protein	K00002	KO	protein		193	232	552	592	0.1	300.0	200.0	evalue-rank	1.0
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
                f.write("detection_type	detection_method	batch	query_accession	query_database	query_type	target_accession	target_database	target_type	target_model	query_start	query_end	target_start	target_end	evalue	bitscore	bitscore_threshold	custom_metric_name	custom_metric_value\n")
                f.write("sequence	hmm	20260327_ff30c5d5	test	a	protein	K00001	KO	protein		60	151	544	628	0.067	400.02			\n")
                f.write("sequence	hmm	20260327_ff30c5d5	test	b	protein	K00001	KO	protein		193	232	552	592	0.01	100			\n")
                f.write("sequence	hmm	20260327_ff30c5d5	test	b	protein	K00002	KO	protein		193	232	552	592	0.1	300			\n")

            assignment_tsv = os.path.join(temp_dir, "assigned.tsv")
            assign_ko(hmm_res_tsv, ko_threshold_tsv, assignment_tsv, scoring_ratio_min=0.24)

            expected = """
detection_type	detection_method	batch	query_accession	query_database	query_type	target_accession	target_database	target_type	target_model	query_start	query_end	target_start	target_end	evalue	bitscore	bitscore_threshold	custom_metric_name	custom_metric_value
sequence	hmm	20260327_ff30c5d5	test	a	protein	K00001	KO	protein		60	151	544	628	0.067	400.02	400.01	evalue-rank	1.0
sequence	hmm	20260327_ff30c5d5	test	b	protein	K00001	KO	protein		193	232	552	592	0.01	100.0	400.01	evalue-rank	1.0
sequence	hmm	20260327_ff30c5d5	test	b	protein	K00002	KO	protein		193	232	552	592	0.1	300.0	200.0	evalue-rank	2.0
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
                f.write("detection_type	detection_method	batch	query_accession	query_database	query_type	target_accession	target_database	target_type	target_model	query_start	query_end	target_start	target_end	evalue	bitscore	bitscore_threshold	custom_metric_name	custom_metric_value\n")
                f.write("sequence	hmm	20260327_ff30c5d5	test	a	protein	K00001	KO	protein		60	151	544	628	0.03	600			\n")
                f.write("sequence	hmm	20260327_ff30c5d5	test	a	protein	K00002	KO	protein		60	151	544	628	0.02	500			\n")
                f.write("sequence	hmm	20260327_ff30c5d5	test	b	protein	K00001	KO	protein		193	232	552	592	0.01	100			\n")
                f.write("sequence	hmm	20260327_ff30c5d5	test	b	protein	K00002	KO	protein		193	232	552	592	0.1	300			\n")

            assignment_tsv = os.path.join(temp_dir, "assigned.tsv")
            assign_ko(hmm_res_tsv, ko_threshold_tsv, assignment_tsv, scoring_ratio_min=0)

            expected = """
detection_type	detection_method	batch	query_accession	query_database	query_type	target_accession	target_database	target_type	target_model	query_start	query_end	target_start	target_end	evalue	bitscore	bitscore_threshold	custom_metric_name	custom_metric_value
sequence	hmm	20260327_ff30c5d5	test	a	protein	K00002	KO	protein		60	151	544	628	0.02	500.0	200.0	evalue-rank	1.0
sequence	hmm	20260327_ff30c5d5	test	a	protein	K00001	KO	protein		60	151	544	628	0.03	600.0	400.01	evalue-rank	2.0
sequence	hmm	20260327_ff30c5d5	test	b	protein	K00001	KO	protein		193	232	552	592	0.01	100.0	400.01	evalue-rank	1.0
sequence	hmm	20260327_ff30c5d5	test	b	protein	K00002	KO	protein		193	232	552	592	0.1	300.0	200.0	evalue-rank	2.0
"""

            with open(assignment_tsv, "r") as f:
                self.maxDiff = None
                self.assertEqual(f.read().strip(), expected.strip())


class TestKOFilteringLogic(unittest.TestCase):

    def test_filters_away_small_matches(self):

        with tempfile.TemporaryDirectory() as temp_dir:

            ko_threshold_tsv = os.path.join(temp_dir, "ko_threshold.tsv")
            with open(ko_threshold_tsv, 'w') as f:
                f.write("model	threshold	score_type	profile_type\n")
                f.write("K00001	160.0	domain	trim\n")
                f.write("K00002	80.0	domain	all\n")

            hmm_res_tsv = os.path.join(temp_dir, "results.tsv")
            with open(hmm_res_tsv, 'w') as f:
                f.write("detection_type	detection_method	batch	query_accession	query_database	query_type	target_accession	target_database	target_type	target_model	query_start	query_end	target_start	target_end	evalue	bitscore	bitscore_threshold	custom_metric_name	custom_metric_value\n")
                f.write("sequence	hmm	20260327_ff30c5d5	test	a	protein	x	KO	protein	K00001	60	151	544	625	0.01	800			\n")
                f.write("sequence	hmm	20260327_ff30c5d5	test	a	protein	y	KO	protein	K00001	60	151	544	623	0.01	800			\n")
                f.write("sequence	hmm	20260327_ff30c5d5	test	b	protein	z	KO	protein	K00002	193	232	552	572	0.01	800			\n")
                f.write("sequence	hmm	20260327_ff30c5d5	test	b	protein	z	KO	protein	K00002	332	352	572	592	0.01	800			\n")

            out_tsv = os.path.join(temp_dir, "filtered.tsv")
            filter_detected_by_target_length(hmm_res_tsv, ko_threshold_tsv, out_tsv, min_match_to_threshold_ratio=0.5)

            filtered = CSVSource(DetectedTable, out_tsv).values()

            # x target length 625-544, >160*0.5
            # y target length 623-544, <160*0.5
            # z target length 572-552 + 592-572, =80*0.5
            self.assertCountEqual([(row["target_accession"], row["target_start"]) for row in filtered], [("x", 544), ("z", 552), ("z", 572)])
                

    def test_groupby_query_acc_db_type_and_target_acc_db_type_together(self):

        with tempfile.TemporaryDirectory() as temp_dir:

            ko_threshold_tsv = os.path.join(temp_dir, "ko_threshold.tsv")
            with open(ko_threshold_tsv, 'w') as f:
                f.write("model	threshold	score_type	profile_type\n")
                f.write("K00001	160.0	domain	trim\n")
                f.write("K00002	80.0	domain	all\n")

            hmm_res_tsv = os.path.join(temp_dir, "results.tsv")
            with open(hmm_res_tsv, 'w') as f:
                f.write("detection_type	detection_method	batch	query_accession	query_database	query_type	target_accession	target_database	target_type	target_model	query_start	query_end	target_start	target_end	evalue	bitscore	bitscore_threshold	custom_metric_name	custom_metric_value\n")
                f.write("sequence	hmm	20260327_ff30c5d5	a	db1	protein	x	KO	protein	K00001	60	151	544	623	0.01	800			\n")
                f.write("sequence	hmm	20260327_ff30c5d5	a	db2	protein	x	KO	protein	K00001	60	151	626	646	0.01	800			\n")
                f.write("sequence	hmm	20260327_ff30c5d5	a	db1	dna	x	KO	protein	K00001	60	151	626	646	0.01	800			\n")
                f.write("sequence	hmm	20260327_ff30c5d5	a	db1	protein	x	KO	dna	K00001	60	151	626	646	0.01	800			\n")
                f.write("sequence	hmm	20260327_ff30c5d5	a	db1	protein	x	KO2	protein	K00001	60	151	626	646	0.01	800			\n")
                f.write("sequence	hmm	20260327_ff30c5d5	b	db1	protein	z	KO	protein	K00002	193	232	552	572	0.01	800			\n")
                f.write("sequence	hmm	20260327_ff30c5d5	b	db1	protein	z	KO	protein	K00002	332	352	572	592	0.01	800			\n")

            out_tsv = os.path.join(temp_dir, "filtered.tsv")
            filter_detected_by_target_length(hmm_res_tsv, ko_threshold_tsv, out_tsv, min_match_to_threshold_ratio=0.5)

            filtered = CSVSource(DetectedTable, out_tsv).values()

            # x - everything after first row have different query_db, query_type, target_db, target_type values
            # z target length 572-552 + 592-572, =80*0.5
            self.assertCountEqual([(row["target_accession"], row["target_start"]) for row in filtered], [("z", 552), ("z", 572)])

    def test_handles_target_coordinates_reversed(self):

        with tempfile.TemporaryDirectory() as temp_dir:

            ko_threshold_tsv = os.path.join(temp_dir, "ko_threshold.tsv")
            with open(ko_threshold_tsv, 'w') as f:
                f.write("model	threshold	score_type	profile_type\n")
                f.write("K00001	160.0	domain	trim\n")
                f.write("K00002	80.0	domain	all\n")

            hmm_res_tsv = os.path.join(temp_dir, "results.tsv")
            with open(hmm_res_tsv, 'w') as f:
                f.write("detection_type	detection_method	batch	query_accession	query_database	query_type	target_accession	target_database	target_type	target_model	query_start	query_end	target_start	target_end	evalue	bitscore	bitscore_threshold	custom_metric_name	custom_metric_value\n")
                f.write("sequence	hmm	20260327_ff30c5d5	test	a	protein	x	KO	protein	K00001	60	151	625	544	0.01	800			\n")
                f.write("sequence	hmm	20260327_ff30c5d5	test	a	protein	y	KO	protein	K00001	60	151	623	544	0.01	800			\n")
                f.write("sequence	hmm	20260327_ff30c5d5	test	b	protein	z	KO	protein	K00002	193	232	552	572	0.01	800			\n")
                f.write("sequence	hmm	20260327_ff30c5d5	test	b	protein	z	KO	protein	K00002	332	352	572	592	0.01	800			\n")

            out_tsv = os.path.join(temp_dir, "filtered.tsv")
            filter_detected_by_target_length(hmm_res_tsv, ko_threshold_tsv, out_tsv, min_match_to_threshold_ratio=0.5)

            filtered = CSVSource(DetectedTable, out_tsv).values()

            # x target length 625-544, >160*0.5
            # y target length 623-544, <160*0.5
            # z target length 572-552 + 592-572, =80*0.5
            self.assertCountEqual([(row["target_accession"], row["target_start"]) for row in filtered], [("x", 625), ("z", 552), ("z", 572)])

    def test_can_adjust_min_ratio(self):

        with tempfile.TemporaryDirectory() as temp_dir:

            ko_threshold_tsv = os.path.join(temp_dir, "ko_threshold.tsv")
            with open(ko_threshold_tsv, 'w') as f:
                f.write("model	threshold	score_type	profile_type\n")
                f.write("K00001	160.0	domain	trim\n")
                f.write("K00002	80.0	domain	all\n")

            hmm_res_tsv = os.path.join(temp_dir, "results.tsv")
            with open(hmm_res_tsv, 'w') as f:
                f.write("detection_type	detection_method	batch	query_accession	query_database	query_type	target_accession	target_database	target_type	target_model	query_start	query_end	target_start	target_end	evalue	bitscore	bitscore_threshold	custom_metric_name	custom_metric_value\n")
                f.write("sequence	hmm	20260327_ff30c5d5	test	a	protein	x	KO	protein	K00001	60	151	625	544	0.01	800			\n")
                f.write("sequence	hmm	20260327_ff30c5d5	test	a	protein	y	KO	protein	K00001	60	151	623	544	0.01	800			\n")
                f.write("sequence	hmm	20260327_ff30c5d5	test	b	protein	z	KO	protein	K00002	193	232	552	572	0.01	800			\n")
                f.write("sequence	hmm	20260327_ff30c5d5	test	b	protein	z	KO	protein	K00002	332	352	572	592	0.01	800			\n")

            out_tsv = os.path.join(temp_dir, "filtered.tsv")

            filter_detected_by_target_length(hmm_res_tsv, ko_threshold_tsv, out_tsv, min_match_to_threshold_ratio=0.5)
            filtered = CSVSource(DetectedTable, out_tsv).values()
            # x target length 625-544, >160*0.5
            # y target length 623-544, <160*0.5
            # z target length 572-552 + 592-572, =80*0.5
            self.assertCountEqual([(row["target_accession"], row["target_start"]) for row in filtered], [("x", 625), ("z", 552), ("z", 572)])

            filter_detected_by_target_length(hmm_res_tsv, ko_threshold_tsv, out_tsv, min_match_to_threshold_ratio=0.4)
            filtered = CSVSource(DetectedTable, out_tsv).values()
            # x target length 625-544, >160*0.4
            # y target length 623-544, >160*0.4
            # z target length 572-552 + 592-572, =80*0.4
            self.assertCountEqual([(row["target_accession"], row["target_start"]) for row in filtered], [("x", 625), ("y", 623), ("z", 552), ("z", 572)])
