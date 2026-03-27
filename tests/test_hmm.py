import os
import tempfile
import unittest

from heap.hmm import parse_hmm_domtbl, hmm_results_to_detected_table


class TestDomTblParser(unittest.TestCase):

    def test_parse_hmm_domtbl_returns_matches(self):

        with tempfile.TemporaryDirectory() as temp_dir:

            temp_file_path = os.path.join(temp_dir, 'domtbl.txt')
            with open(temp_file_path, 'w') as f:
                f.write("# target name  accession  tlen  query name  accession  qlen  E-value  score  bias  #  of  c-Evalue  i-Evalue  score  bias  from  to  from  to\n")
                f.write("cand_0 _ 81 _ _ 5 0.1 100 _ _ _ 0.005 0.05 201 _ 11 12 13 14\n")
                f.write("cand_0 _ 82 _ _ 6 0.2 101 _ _ _ 0.004 0.04 202 _ 21 22 23 24\n")

            matches = parse_hmm_domtbl(temp_file_path)
            self.assertEqual(len(matches), 2)
            self.assertEqual(matches[0]["target_name"], "cand_0")
            self.assertEqual(matches[0]["target_length"], 81)
            self.assertEqual(matches[0]["seq_evalue"], 0.1)
            self.assertEqual(matches[0]["seq_score"], 100)
            self.assertEqual(matches[0]["dom_evalue"], 0.05) # using i-Evalue, not c-Evalue
            self.assertEqual(matches[0]["dom_evalue_cond"], 0.005)
            self.assertEqual(matches[0]["dom_score"], 201)
            self.assertEqual(matches[0]["query_length"], 5)
            self.assertEqual(matches[0]["hmm_from"], 11)
            self.assertEqual(matches[0]["hmm_to"], 12)
            self.assertEqual(matches[0]["ali_from"], 13)
            self.assertEqual(matches[0]["ali_to"], 14)
            self.assertEqual(matches[1]["target_name"], "cand_0")
            self.assertEqual(matches[1]["target_length"], 82)
            self.assertEqual(matches[1]["seq_evalue"], 0.2)
            self.assertEqual(matches[1]["seq_score"], 101)
            self.assertEqual(matches[1]["dom_evalue"], 0.04) # using i-Evalue, not c-Evalue
            self.assertEqual(matches[1]["dom_evalue_cond"], 0.004)
            self.assertEqual(matches[1]["dom_score"], 202)
            self.assertEqual(matches[1]["query_length"], 6)
            self.assertEqual(matches[1]["hmm_from"], 21)
            self.assertEqual(matches[1]["hmm_to"], 22)
            self.assertEqual(matches[1]["ali_from"], 23)
            self.assertEqual(matches[1]["ali_to"], 24)

    def test_parse_hmm_domtbl_asserts_has_expected_headers(self):

        with tempfile.TemporaryDirectory() as temp_dir:

            temp_file_path = os.path.join(temp_dir, 'domtbl.txt')
            with open(temp_file_path, 'w') as f:
                # BAD unexpected header
                f.write("# target name  accession  tlen  query name  accession  qlen  E-value  score  from  to  from  to\n")
                f.write("cand_0 _ _ _ _ _ 0.1 100 11 12 13 14\n")
                f.write("cand_0 _ _ _ _ _ 0.2 101 21 22 23 24\n")

            with self.assertRaises(AssertionError):
                parse_hmm_domtbl(temp_file_path)


class TestParsingHMMResultsToTable(unittest.TestCase):

    def test_hmmscan_mode_writes_results_correctly(self):

        hmm_results = [
          dict(query_accession="a",
               query_name="b",
               target_accession="c",
               target_name="d",
               hmm_from=2,
               hmm_to=3,
               ali_from=4,
               ali_to=5,
               dom_evalue=1e-11,
               dom_score=13,
               dom_evalue_cond=5e-13),
          dict(query_accession="e",
               query_name="f",
               target_accession="g",
               target_name="h",
               hmm_from=12,
               hmm_to=13,
               ali_from=14,
               ali_to=15,
               dom_evalue=2e-11,
               dom_score=15,
               dom_evalue_cond=7e-13)
        ]

        with tempfile.TemporaryDirectory() as tmpd:
            tmpf = os.path.join(tmpd, "test.tsv")

            hmm_results_to_detected_table(
                hmm_results, 
                tmpf,
                "q", "protein", "t", "protein",
                "hmmscan",
                batch = "20260327_530fecb5"
            )

            expected = """
detection_type	detection_method	batch	query_accession	query_database	query_type	target_accession	target_database	target_type	query_start	query_end	target_start	target_end	evalue	bitscore	bitscore_threshold	custom_metric_name	custom_metric_value
sequence	hmm	20260327_530fecb5	a	q	protein	c	t	protein	4	5	2	3	1e-11	13.0			
sequence	hmm	20260327_530fecb5	e	q	protein	g	t	protein	14	15	12	13	2e-11	15.0			
"""

            with open(tmpf, "r") as f:
                self.assertEqual(f.read().strip(), expected.strip())


    def test_non_hmmscan_mode_reverses_query_target(self):

        hmm_results = [
          dict(query_accession="a",
               query_name="b",
               target_accession="c",
               target_name="d",
               hmm_from=2,
               hmm_to=3,
               ali_from=4,
               ali_to=5,
               dom_evalue=1e-11,
               dom_score=13,
               dom_evalue_cond=5e-13)
        ]

        with tempfile.TemporaryDirectory() as tmpd:
            tmpf = os.path.join(tmpd, "test.tsv")

            hmm_results_to_detected_table(
                hmm_results, 
                tmpf,
                "q", "protein", "t", "protein",
                "hmmsearch",
                batch = "20260327_530fecb5"
            )

            expected = """
detection_type	detection_method	batch	query_accession	query_database	query_type	target_accession	target_database	target_type	query_start	query_end	target_start	target_end	evalue	bitscore	bitscore_threshold	custom_metric_name	custom_metric_value
sequence	hmm	20260327_530fecb5	c	q	protein	a	t	protein	2	3	4	5	1e-11	13.0			
"""

            with open(tmpf, "r") as f:
                self.assertEqual(f.read().strip(), expected.strip())

    def test_uses_name_if_accession_is_empty_or_dash(self):

        hmm_results = [
          dict(query_accession="",
               query_name="b",
               target_accession=" - ",
               target_name="d",
               hmm_from=2,
               hmm_to=3,
               ali_from=4,
               ali_to=5,
               dom_evalue=1e-11,
               dom_score=13,
               dom_evalue_cond=5e-13),
          dict(query_accession="-",
               query_name="f",
               target_accession=" ",
               target_name="h",
               hmm_from=12,
               hmm_to=13,
               ali_from=14,
               ali_to=15,
               dom_evalue=2e-11,
               dom_score=15,
               dom_evalue_cond=7e-13)
        ]

        with tempfile.TemporaryDirectory() as tmpd:
            tmpf = os.path.join(tmpd, "test.tsv")

            hmm_results_to_detected_table(
                hmm_results, 
                tmpf,
                "q", "protein", "t", "protein",
                "hmmscan",
                batch = "20260327_530fecb5"
            )

            expected = """
detection_type	detection_method	batch	query_accession	query_database	query_type	target_accession	target_database	target_type	query_start	query_end	target_start	target_end	evalue	bitscore	bitscore_threshold	custom_metric_name	custom_metric_value
sequence	hmm	20260327_530fecb5	b	q	protein	d	t	protein	4	5	2	3	1e-11	13.0			
sequence	hmm	20260327_530fecb5	f	q	protein	h	t	protein	14	15	12	13	2e-11	15.0			
"""

            with open(tmpf, "r") as f:
                self.assertEqual(f.read().strip(), expected.strip())
