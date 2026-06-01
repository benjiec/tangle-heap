#!/bin/bash
set -e

# Validate input arguments
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <N_parts>"
    exit 1
fi

N=$1

# Basic bounds check
if [ "$N" -lt 1 ]; then
    echo "Error: Number of parts must be 1 or greater."
    exit 1
fi

# Initialization: Clone part1 files as the base of final_db
echo "Initializing final_db with part 0..."
cp db_0 final_db; cp db_0.index final_db.index; cp db_0.dbtype final_db.dbtype; cp db_0.lookup final_db.lookup
cp db_0 final_db_h; cp db_0.index final_db_h.index; cp db_0.dbtype final_db_h.dbtype
cp db_0 final_db_ss; cp db_0.index final_db_ss.index; cp db_0.dbtype final_db_ss.dbtype

# Loop through part 1 up to part N
for (( i=1; i<N; i++ )); do
    chunk="db_$i"
    
    # Verify target chunk files exist before executing merge
    if [ ! -f "${chunk}" ] || [ ! -f "${chunk}_h" ] || [ ! -f "${chunk}_ss" ]; then
        echo "Error: Essential files for ${chunk} are missing. Aborting."
        exit 1
    fi

    echo "Merging ${chunk} into final_db (Step $i of $N)..."
 
    # 1. Merge Main Sequence Data
    docker run --platform linux/amd64 --rm -v .:/db ghcr.io/steineggerlab/foldseek concatdbs /db/final_db /db/"$chunk" /db/tmp_db --threads 1
    mv tmp_db final_db; mv tmp_db.index final_db.index; mv tmp_db.dbtype final_db.dbtype; mv tmp_db.lookup final_db.lookup
    
    # 2. Merge Header Metadata
    docker run --platform linux/amd64 --rm -v .:/db ghcr.io/steineggerlab/foldseek concatdbs /db/final_db_h /db/"${chunk}_h" /db/tmp_db_h --threads 1
    mv tmp_db_h final_db_h; mv tmp_db_h.index final_db_h.index; mv tmp_db_h.dbtype final_db_h.dbtype
    
    # 3. Merge 3Di Structure Alphabet Data
    docker run --platform linux/amd64 --rm -v .:/db ghcr.io/steineggerlab/foldseek concatdbs /db/final_db_ss /db/"${chunk}_ss" /db/tmp_db_ss --threads 1
    mv tmp_db_ss final_db_ss; mv tmp_db_ss.index final_db_ss.index; mv tmp_db_ss.dbtype final_db_ss.dbtype
done

# Step 4: Reindex the unified database globally
echo "Generating global index mappings..."
docker run --platform linux/amd64 --rm -v .:/db ghcr.io/steineggerlab/foldseek createindex /db/final_db /tmp

echo "Database assembly complete: final_db"
