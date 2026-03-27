# Heap

Heap: (noun) a disorderly collection of objects placed haphazardly on top of
each other, or (verb) put objects or loose substances on top of each other.

In this case: loosely organized collection of probabilistic annotations for
transcripts and proteins, to help figure out what these transcripts and
proteins do.


## Setup

Install hmmer3 package: e.g. on MacOS run `brew install hmmer`

FoldSeek

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
FOLDSEEK_DB_DIR=/host/db_dir
```


## FoldSeek Searching

Use the following script to search the SwissProt database

```
PYTHONPATH=. python3 scripts/foldseek-swissprot.py \
  --query-database-name exp-doi:10.1126_sciadv.aba2498 \
  query.faa test.tsv
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

Or directly from a FASTA

```
docker run --rm -v /host/db-dir:/db -v /host/fasta-dir:/app \
  ghcr.io/steineggerlab/foldseek easy-search \
  /app/query.faa /db/afdb-swissprot /app/res-faa.tsv /tmp \
  --format-output "query,target,evalue,bits,fident,qstart,qend,tstart,tend" \
  --prostt5-model /db/prost-t5-weights
```
