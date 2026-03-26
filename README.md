# Heap

Heap: (noun) a disorderly collection of objects placed haphazardly on top of
each other, or (verb) put objects or loose substances on top of each other.

In this case: loosely organized collection of probabilistic annotations for
transcripts and proteins, to help figure out what these transcripts and
proteins do.


## Setup

FoldSeek

```
docker pull ghcr.io/steineggerlab/foldseek:latest
```

Then download databases to a host directory mounted onto the container

```
docker run -v /host/dir:/app --rm \
  ghcr.io/steineggerlab/foldseek databases \
  Alphafold/Swiss-Prot /app/afdb-swissprot /tmp

docker run -v /host/dir:/app --rm \
  ghcr.io/steineggerlab/foldseek databases \
  PDB /app/pdb /tmp

docker run -v /host/dir:/app --rm \
  ghcr.io/steineggerlab/foldseek databases \
  ProstT5 /app/prost-t5-weights /tmp
```


## FoldSeek Searching

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
