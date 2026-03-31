import os
import re
import random
import subprocess
from pathlib import Path
from tangle import unique_batch
from tangle.sequence import read_fasta_as_dict, write_fasta_from_dict


def from_template(template_fn, out_fn, env):
    envsubst_path = os.environ.get("ENVSUBST_PATH")
    if envsubst_path is None:
        envsubst_path = "envsubst"
        print("Missing ENVSUBST_PATH variable, assuming command exists")

    whitelist = ",".join(f"${k}" for k in env.keys())
    env = {k:str(v) for k,v in env.items()}
    with open(template_fn, "rt") as f_in, open(out_fn, "wt") as f_out:
        result = subprocess.run(
            [envsubst_path, whitelist],
            stdin=f_in,
            stdout=f_out,
            env=env,
            check=True
        )


def split_fasta(input_fn, entries_per_file, parent_dir, fn_prefix):
    sequences = read_fasta_as_dict(input_fn)
    accs = [x for x in sequences.keys()]
    random.shuffle(accs)

    j = 0
    outputs = []
    for i in range(0, len(accs), entries_per_file):
        target_fn = str(Path(parent_dir) / f"{fn_prefix}{j}")
        # print(target_fn)
        selected = {k:sequences[k] for k in accs[i:i+entries_per_file]}
        write_fasta_from_dict(selected, target_fn)
        outputs.append(target_fn)
        j += 1

    return outputs


class GCHelperBase():

    def __init__(self, host_run_dir_parent):

        self.run_batch = unique_batch()
        self.batch_name = re.sub("[^a-z0-9-]", "-", self.run_batch)

        gc_run_dir = os.environ.get("GCLOUD_RUN_DIR")
        if gc_run_dir is None:
            raise Exception("Missing GCLOUD_RUN_DIR env variable")
        if gc_run_dir.endswith("/"):
            gc_run_dir = gc_run_dir[:-1]

        self.gc_run_dir = f"{gc_run_dir}/{self.run_batch}"
        self.gc_run_input_dir = f"{self.gc_run_dir}/inputs"
        self.gc_run_output_dir = f"{self.gc_run_dir}/outputs"

        run_dir = Path(host_run_dir_parent) / self.run_batch
        run_dir.mkdir()
        input_rel_path = "inputs"
        input_dir = run_dir / input_rel_path
        input_dir.mkdir()

        self.host_run_dir = str(run_dir)
        self.host_run_input_dir = str(input_dir)

        self._env = dict(
          BATCH_NAME=self.batch_name,
          HOST_RUN_DIR=self.host_run_dir,
          HOST_RUN_INPUT_DIR=self.host_run_input_dir,
          HOST_RUN_INPUT_REL_PATH=input_rel_path,
          GC_RUN_DIR=self.gc_run_dir,
          GC_RUN_INPUT_DIR=self.gc_run_input_dir,
          GC_RUN_OUTPUT_DIR=self.gc_run_output_dir
        )

    def setenv(self, **kwargs):
        self._env = self._env | kwargs

    def instantiate_template(self, template_fn, instantiated_fn):
        instantiated_fn = Path(self.host_run_dir) / instantiated_fn
        from_template(template_fn, instantiated_fn, self._env)


class GCHMMHelper(GCHelperBase):

    def __init__(self, host_run_dir_parent):
        super(GCHMMHelper, self).__init__(host_run_dir_parent)

        gc_hmm_path = os.environ.get("GCLOUD_HMM_DB_DIR")
        if gc_hmm_path is None:
            raise Exception("Missing GCLOUD_HMM_DB_DIR env variable")
        if gc_hmm_path.endswith("/"):
            gc_hmm_path = gc_hmm_path[:-1]
        self.gc_hmm_path = gc_hmm_path

        self.setenv(GC_HMM_PATH=self.gc_hmm_path)
