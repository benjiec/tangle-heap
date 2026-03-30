# Heap

Heap: (noun) a disorderly collection of objects placed haphazardly on top of
each other, or (verb) put objects or loose substances on top of each other.

In this case: loosely organized collection of probabilistic annotations for
transcripts and proteins, to help figure out what these transcripts and
proteins do.


## Setup

### HMM

Install hmmer3 package: e.g. on MacOS run `brew install hmmer`

Download the following profiles

  * KEGG KO profile HMMs: `https://www.genome.jp/ftp/db/kofam/profiles.tar.gz`
    * Then concatenate all the profiles together: `cat profiles/*.hmm > ko.hmm`
    * Run `hmmpress ko.hmm`
    * Also create `ko_thresholds.tsv` from KEGG FTP site `https://www.genome.jp/ftp/db/kofam/ko_list.gz`
      * Filter away rows without a threshold, using `grep -v "\-\t\-" ko_thresholds.txt`

  * Pfam HMM profiles: `https://ftp.ebi.ac.uk/pub/databases/Pfam/current_release/Pfam-A.hmm.gz`
    * Run `hmmpress Pfam-A.hmm`

Put these files in the same directory then set the following environment variable

```
HMM_DB_DIR=</host/hmm_dir>
```

### FoldSeek

```
docker pull ghcr.io/steineggerlab/foldseek:latest
```

Then download databases to a host directory mounted onto the container

```
docker run -v /host/db_dir:/app --rm \
  ghcr.io/steineggerlab/foldseek databases \
  Alphafold/Swiss-Prot /app/afdb-swissprot /tmp

docker run -v /host/db_dir:/app --rm \
  ghcr.io/steineggerlab/foldseek databases \
  PDB /app/pdb /tmp

docker run -v /host/db_dir:/app --rm \
  ghcr.io/steineggerlab/foldseek databases \
  ProstT5 /app/prost-t5-weights /tmp
```

Then, to use foldseek scripts, set the following environment variables

```
FOLDSEEK_DB_DIR=</host/db_dir>
```


## Hosting Docker Images on Google Cloud

This repo

```
docker build --platform linux/amd64 -t us-east1-docker.pkg.dev/needle-489321/tangle-docker/heap:latest .
docker push us-east1-docker.pkg.dev/needle-489321/tangle-docker/heap:latest
```

Foldseek image

(Note you may need to cleanup existing non-amd64 versions of the foldseem image first, using `docker rmi`)

```
docker pull --platform linux/amd64 ghcr.io/steineggerlab/foldseek:latest
docker tag ghcr.io/steineggerlab/foldseek:latest us-east1-docker.pkg.dev/needle-489321/tangle-docker/foldseek:amd64
docker push us-east1-docker.pkg.dev/needle-489321/tangle-docker/foldseek:amd64
```

And, to use these images on Google Cloud, make sure everything under
FOLDSEEK_DB_DIR or HMM_DB_DIR are synced to Google Cloud storage, into a
bucket.


## HMM Searching

### Pfam

Following script can be used to search for Pfam domains

```
PYTHONPATH=. python3 scripts/hmmscan-pfam.py \
  --query-database-name exp-doi:10.1126_sciadv.aba2498 \
  query.faa test_result.tsv
```

The query database name should uniquely identify the source of the query
accessions in the query fasta file.

This script uses hmmscan with GA cutoff scores as the reporting threshold, so
reported domains are likely correct.

To prepare and submit this job to run on Google Cloud, use the following script
to create a run directory under `runs` (or whatever value for `--run-dir`), and
then follow instructions in the README file in that run directory.

```
PYTHPATH=. python3 gcloud/hmmscan-pfam/setup.py \
  --query-database-name exp-doi:10.1126_sciadv.aba2498.SRR9331959_algae_denovo \
  --run-dir=runs \
  proteins.faa.gz
```

### KO

You can search against KO HMM profile similarly,

```
PYTHONPATH=. python3 scripts/hmmscan-ko.py \
  --query-database-name exp-doi:10.1126_sciadv.aba2498 \
  query.faa test_result.tsv
```

But because KO HMM profiles do not use GA scores, but rather a separate
threshold file, a second script is needed to make assignments.

```
PYTHONPATH=. python3 scripts/ko-assign.py \
  test_result.tsv test_result_assigned.tsv
```

Use the `--scoring-ratio-min` option to change the min ratio of bitscore over
threshold used to filter the results. Default is 0.99. If you change to 0.7,
for example, the resulting file may include putative matches worth
investigating.


## FoldSeek Searching

Use the following script to search the SwissProt database

```
PYTHONPATH=. python3 scripts/foldseek-swissprot.py \
  --query-database-name exp-doi:10.1126_sciadv.aba2498 \
  query.faa test_result.tsv
```

The query database name should uniquely identify the source of the query
accessions in the query fasta file.


From a .cif file, you can use the Docker image directly

```
docker run --rm -v /host/db-dir:/db -v /host/cif-file-dir:/app \
  ghcr.io/steineggerlab/foldseek easy-search \
  /app/fold_2026_03_12_14_08_model_0.cif /db/pdb /app/res.tsv /tmp \
  --format-output "query,target,prob,evalue,bits,fident,qstart,qend,tstart,tend"
```


## Pre-generated Relations

Use the following script to convert UniProt to Pfam data, downloaded from
UniProt, to our detected TSV format.

The second argument should be a list of SwissProt IDs present in the AlphaFold
SwissProt database. That argument is just a file with list of accessions from
the first file to keep.

```
gzcat protein2ipr.dat.gz| awk -F'\t' '$4 ~ "PF"' - > protein-pfam.txt
python3 helpers/ipr-pfam.py protein-pfam.txt afdb-swissprot.ids.txt uniprot-pfam.tsv.gz
```
