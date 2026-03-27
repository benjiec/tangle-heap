import os
import tempfile
import unittest

from heap.foldseek import foldseek_output_to_detected_table


class TestParsingFoldSeekResultsToTable(unittest.TestCase):

    def test_writes_results_correctly(self):

        with tempfile.TemporaryDirectory() as tmpd:
            foldseek_fn = os.path.join(tmpd, "foldseek.tsv")
            with open(foldseek_fn, "w") as f:
                f.write("a\tb\t11\t12\t13\t14\t15\t16\n")
                f.write("c\td\t21\t22\t23\t24\t25\t26\n")

            res_fn = os.path.join(tmpd, "test.tsv")
            foldseek_output_to_detected_table(
                foldseek_fn,
                res_fn,
                "q", "protein", "t", "protein",
                batch = "20260327_530fecb5"
            )

            expected = """
detection_type	detection_method	batch	query_accession	query_database	query_type	target_accession	target_database	target_type	query_start	query_end	target_start	target_end	evalue	bitscore	bitscore_threshold	custom_metric_name	custom_metric_value
structure	prost-t5-foldseek	20260327_530fecb5	a	q	protein	b	t	protein	13	14	15	16	11.0	12.0			
structure	prost-t5-foldseek	20260327_530fecb5	c	q	protein	d	t	protein	23	24	25	26	21.0	22.0			
"""

            with open(res_fn, "r") as f:
                self.assertEqual(f.read().strip(), expected.strip())

    def test_can_rewrite_target_accession(self):

        with tempfile.TemporaryDirectory() as tmpd:
            foldseek_fn = os.path.join(tmpd, "foldseek.tsv")
            with open(foldseek_fn, "w") as f:
                f.write("a\tb\t11\t12\t13\t14\t15\t16\n")
                f.write("c\td\t21\t22\t23\t24\t25\t26\n")

            res_fn = os.path.join(tmpd, "test.tsv")
            foldseek_output_to_detected_table(
                foldseek_fn,
                res_fn,
                "q", "protein", "t", "protein",
                batch = "20260327_530fecb5",
                target_accession_rewriter_func = lambda x: "x"
            )

            expected = """
detection_type	detection_method	batch	query_accession	query_database	query_type	target_accession	target_database	target_type	query_start	query_end	target_start	target_end	evalue	bitscore	bitscore_threshold	custom_metric_name	custom_metric_value
structure	prost-t5-foldseek	20260327_530fecb5	a	q	protein	x	t	protein	13	14	15	16	11.0	12.0			
structure	prost-t5-foldseek	20260327_530fecb5	c	q	protein	x	t	protein	23	24	25	26	21.0	22.0			
"""

            with open(res_fn, "r") as f:
                self.assertEqual(f.read().strip(), expected.strip())

    def test_can_filter_by_evalue(self):

        with tempfile.TemporaryDirectory() as tmpd:
            foldseek_fn = os.path.join(tmpd, "foldseek.tsv")
            with open(foldseek_fn, "w") as f:
                f.write("a\tb\t11\t12\t13\t14\t15\t16\n")
                f.write("c\td\t21\t22\t23\t24\t25\t26\n")

            res_fn = os.path.join(tmpd, "test.tsv")
            foldseek_output_to_detected_table(
                foldseek_fn,
                res_fn,
                "q", "protein", "t", "protein",
                batch = "20260327_530fecb5",
                evalue_threshold = 15
            )

            expected = """
detection_type	detection_method	batch	query_accession	query_database	query_type	target_accession	target_database	target_type	query_start	query_end	target_start	target_end	evalue	bitscore	bitscore_threshold	custom_metric_name	custom_metric_value
structure	prost-t5-foldseek	20260327_530fecb5	a	q	protein	b	t	protein	13	14	15	16	11.0	12.0			
"""

            with open(res_fn, "r") as f:
                self.assertEqual(f.read().strip(), expected.strip())
