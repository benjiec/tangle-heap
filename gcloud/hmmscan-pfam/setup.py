import os
import argparse
from pathlib import Path
from tangle import unique_batch
from heap.gcloud import split_fasta, from_template

PREP_GENERAL_TEMPLATE = "prep-general.sh.template"
PREP_GENERAL_SCRIPT = "prep-general.sh"
PREP_TASK_TEMPLATE = "prep-task.sh.template"
PREP_TASK_SCRIPT = "prep-task.sh"
JOB_TEMPLATE = "job.json.template"
JOB_SCRIPT = "job.json"
INSTRUCTION_TEMPLATE = "instruction.template"
INSTRUCTION_FILE = "README"


if __name__ == "__main__":

    ap = argparse.ArgumentParser()
    ap.add_argument("--query-database-name", required=True)
    ap.add_argument("query_faa")
    ap.add_argument("--entries-per-task", type=int, default=5000)
    ap.add_argument("--parallelism", type=int, default=45)
    ap.add_argument("--run-dir-parent", default=None)
    args = ap.parse_args()

    run_batch = unique_batch()
    batch_name = re.sub("[^a-z0-9-]", "-", run_batch)

    fn_prefix = "input.faa."
    script_dir = Path(__file__).resolve().parent

    gc_hmm_path = os.environ.get("GCLOUD_HMM_DB_DIR")
    if gc_hmm_path is None:
        raise Exception("Missing GCLOUD_HMM_DB_DIR env variable")
    if gc_hmm_path.endswith("/"):
        gc_hmm_path = gc_hmm_path[:-1]

    gc_run_dir = os.environ.get("GCLOUD_RUN_DIR")
    if gc_run_dir is None:
        raise Exception("Missing GCLOUD_RUN_DIR env variable")
    if gc_run_dir.endswith("/"):
        gc_run_dir = gc_run_dir[:-1]

    gc_run_dir = f"{gc_run_dir}/{run_batch}"
    gc_run_input_dir = f"{gc_run_dir}/inputs"
    gc_run_output_dir = f"{gc_run_dir}/outputs"
    gc_input_path_pre_index = f"{gc_run_dir}/inputs/{fn_prefix}"

    run_dir_parent = "." if args.run_dir_parent is None else args.run_dir_parent
    run_dir = Path(run_dir_parent) / run_batch
    run_dir.mkdir()
    input_dir = run_dir / "inputs"
    input_dir.mkdir()

    fasta_files = split_fasta(args.query_faa, args.entries_per_task, str(input_dir), fn_prefix)

    env = dict(
        RUN_DIR=str(run_dir),
        PARALLELISM=args.parallelism,
        NTASKS=len(fasta_files),
        BATCH_NAME=batch_name,
        GC_HMM_PATH=gc_hmm_path,
        GC_RUN_DIR=gc_run_dir,
        GC_RUN_INPUT_DIR=gc_run_input_dir,
        GC_RUN_OUTPUT_DIR=gc_run_output_dir,
        GC_INPUT_PATH_PRE_INDEX=gc_input_path_pre_index,
        QUERY_DATABASE_NAME=args.query_database_name,
    )

    print(str(run_dir))
    from_template(script_dir / PREP_GENERAL_TEMPLATE, run_dir / PREP_GENERAL_SCRIPT, env)
    from_template(script_dir / PREP_TASK_TEMPLATE, run_dir / PREP_TASK_SCRIPT, env)
    from_template(script_dir / JOB_TEMPLATE, run_dir / JOB_SCRIPT, env)
    from_template(script_dir / INSTRUCTION_TEMPLATE, run_dir / INSTRUCTION_FILE, env)
