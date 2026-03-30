import os
import random
import subprocess
from pathlib import Path
from tangle.sequence import read_fasta_as_dict, write_fasta_from_dict


def from_template(template_fn, script_fn, env):
    envsubst_path = os.environ.get("ENVSUBST_PATH")
    if envsubst_path is None:
        envsubst_path = "envsubst"
        print("Missing ENVSUBST_PATH variable, assuming command exists")

    whitelist = ",".join(f"${k}" for k in env.keys())
    env = {k:str(v) for k,v in env.items()}
    with open(template_fn, "rt") as f_in, open(script_fn, "wt") as f_out:
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
        print(target_fn)
        selected = {k:sequences[k] for k in accs[i:i+entries_per_file]}
        write_fasta_from_dict(selected, target_fn)
        outputs.append(target_fn)
        j += 1

    return outputs
