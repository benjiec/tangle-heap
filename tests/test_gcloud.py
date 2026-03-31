import random
import tempfile
import unittest
from pathlib import Path

from heap.gcloud import split_fasta, from_template
from tangle.sequence import read_fasta_as_dict, write_fasta_from_dict


def random_sequence(n):
    return "".join([random.choice("agct") for i in range(n)])


class TestSplitFasta(unittest.TestCase):

    def test_splits_fasta_file_into_files_with_provided_prefix(self):

        sequences = {
          f"s{i}": random_sequence(20)
          for i in range(21)
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            input_fn = Path(temp_dir) / "input.faa"
            write_fasta_from_dict(sequences, str(input_fn))

            split_fasta(input_fn, 10, temp_dir, "split.faa.pre_")

            self.assertEqual((Path(temp_dir) / "split.faa.pre_0").exists(), True)
            self.assertEqual((Path(temp_dir) / "split.faa.pre_1").exists(), True)
            self.assertEqual((Path(temp_dir) / "split.faa.pre_2").exists(), True)
            self.assertEqual((Path(temp_dir) / "split.faa.pre_3").exists(), False)

            part1 = read_fasta_as_dict(str(Path(temp_dir) / "split.faa.pre_0"))
            part2 = read_fasta_as_dict(str(Path(temp_dir) / "split.faa.pre_1"))
            part3 = read_fasta_as_dict(str(Path(temp_dir) / "split.faa.pre_2"))

            self.assertEqual(sequences, part1 | part2 | part3)
            self.assertEqual(len(part1), 10)
            self.assertEqual(len(part2), 10)
            self.assertEqual(len(part3), 1)

    def test_splits_fasta_file_can_evenly_split(self):

        sequences = {
          f"s{i}": random_sequence(20)
          for i in range(21)
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            input_fn = Path(temp_dir) / "input.faa"
            write_fasta_from_dict(sequences, str(input_fn))

            split_fasta(input_fn, 7, temp_dir, "pre_")

            self.assertEqual((Path(temp_dir) / "pre_0").exists(), True)
            self.assertEqual((Path(temp_dir) / "pre_1").exists(), True)
            self.assertEqual((Path(temp_dir) / "pre_2").exists(), True)
            self.assertEqual((Path(temp_dir) / "pre_3").exists(), False)

            part1 = read_fasta_as_dict(str(Path(temp_dir) / "pre_0"))
            part2 = read_fasta_as_dict(str(Path(temp_dir) / "pre_1"))
            part3 = read_fasta_as_dict(str(Path(temp_dir) / "pre_2"))

            self.assertEqual(sequences, part1 | part2 | part3)
            self.assertEqual(len(part1), 7)
            self.assertEqual(len(part2), 7)
            self.assertEqual(len(part3), 7)


class TestFromTemplate(unittest.TestCase):

    def test_generates_file(self):
        
        with tempfile.TemporaryDirectory() as temp_dir:
            template_fn = Path(temp_dir) / "template"
            out_fn = Path(temp_dir) / "out"

            with open(template_fn, "wt") as f:
                f.write("${A}${B}_${C}\nD{E}")

            env = dict(A="foo", B="bar", E=3)
            from_template(template_fn, out_fn, env)

            with open(out_fn, "rt") as f:
                written = f.read()
            self.assertEqual(written, "foobar_${C}\nD{E}")
