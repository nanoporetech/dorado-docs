---
herro: https://github.com/lbcb-sci/herro
bgzip: https://www.htslib.org/doc/bgzip.html
---

# Dorado Correct

!!! tip inline end "Should I use `correct` or `polish`?"

    [See here]({{find("polish")}}#should-i-use-correct-or-polish)

Dorado supports single-read error correction with the integration of the [HERRO]({{herro}}) algorithm in Dorado `correct`.

## HERRO Algorithm

!!! info inline end "Citation"

    Telomere-to-telomere phased genome assembly using error-corrected Simplex nanopore reads

    Dominik Stanojević, Dehui Lin, Paola Florez de Sessions, Mile Šikić
    bioRxiv 2024.05.18.594796;

HERRO uses all-vs-all alignment followed by haplotype-aware correction using a deep learning
model to achieve higher single-read accuracies. The corrected reads are primarily useful for
generating de novo assemblies of diploid organisms.

The original paper containing implementation details
can be downloaded from [bioRxiv](https://www.biorxiv.org/content/10.1101/2024.05.18.594796v1).

## Quick start

To run Dorado `correct`, pass in a FASTQ or a [bgz]({{bgzip}}) compressed FASTQ.gz file.
Dorado will perform read correction on this dataset after automatically downloading the
required [HERRO]({{herro}}) model.

```dorado
dorado correct reads.fastq > corrected_reads.fasta
```

You may pre-download the [HERRO]({{herro}}) model if required:

```dorado
dorado download --model herro-v1
```

and select it as shown:

```dorado
dorado correct reads.fastq --model-path herro-v1 > corrected_reads.fasta
```

!!! IMPORTANT

    Currently there is only one Dorado `correct` model which is `herro-v1` for the `r10.4` run condition.

## Usage

Dorado `correct` supports FASTQ(.gz) as the input and generates a FASTA file as output.
A FASTQ file is either a FASTA or FASTQ file and either can be uncompressed
or compressed with [bgzip]({{bgzip}}).

An index file is generated for the input FASTQ file in the same folder unless
one is already present. Please ensure that the folder with the input file is writeable
by the Dorado process and has sufficient disk space (no more than 10GB should be
necessary for a whole genome dataset).

To correct reads, run:

```dorado
dorado correct reads.fastq > corrected_reads.fasta
```

All required model weights are downloaded automatically by Dorado.
However, the weights can also be pre-downloaded and passed via command line in case of offline execution. To do so, run:

```dorado
dorado download --model herro-v1
dorado correct --model-path herro-v1 reads.fq.gz > corrected_reads.fasta
```

### Split mapping and inference

Dorado `correct` can run mapping (CPU-only stage) and inference (GPU-intensive stage) individually.
This enables separation of the CPU and GPU heavy stages into individual steps which can
even be run on different nodes with appropriate compute characteristics. For example:

```dorado
dorado correct reads.fastq --to-paf > overlaps.paf
dorado correct reads.fastq --from-paf overlaps.paf > corrected_reads.fasta
```

Gzipped PAF is currently not supported for the `--from-paf` option.

### Resume

If a run was stopped or has failed, Dorado `correct` provides functionality to resume from where the previous
run stopped.

The `--resume-from` argument takes a list of previously corrected reads provided via
a `.fai` index from the outputs of the previous run. The reads that have been previously
processed are then skipped when resuming.

To generate the `.fai` file from a previous output from Dorado `correct` use:

```bash
# corrected_reads.fasta is the output from the previously interrupted run.
mv corrected_reads.fasta corrected_reads.res.fasta
samtools faidx corrected_reads.res.fasta
```

And to continue Dorado `correct` using `--resume-from` use:

```dorado
dorado correct reads.fastq --resume-from corrected_reads.res.fasta.fai > corrected_reads.fasta
```

The input file format for the `--resume-from` feature can be any plain text file where
the first whitespace-delimited column (or a full row) consists of sequence names to skip, one per row.

## Specifying resources

Dorado correct will automatically select all available compute resources to perform error correction.

To specify resources manually use:

* `-x / --device` to specify specific GPU resources (if available).
* `--threads` to set the maximum number of threads to be used during correction.
* `--infer-threads` to set the number of threads used per-device for inference.

```dorado
dorado correct reads.fastq --device cuda:0 --threads 64 --infer-threads 1 > corrected_reads.fasta
```

The error correction tool is both compute and memory intensive.

As a result, it is best run on a system with:

* multiple high performance CPU cores ( > 64 cores)
* large system memory ( > 256GB)
* a modern GPU with a large VRAM ( > 32GB)

## Troubleshooting

### Consuming too much memory

In case the process is consuming too much memory for your system, try running it with a smaller
index size. For example:

```dorado
dorado correct reads.fastq --index-size 4G > corrected_reads.fasta
```

The auto-computed inference batch size may still be too high for your system.
If you are experiencing warnings/errors regarding available GPU memory, try reducing the batch
size by selecting it manually. For example:

```dorado
dorado correct reads.fastq --batch-size <number> > corrected_reads.fasta
```

### Missing reads

In case your output FASTA file contains a very low amount of corrected reads compared to the input,
please check the following:

1. The input dataset has average read length >=10kbp.
      * Dorado Correct is designed for long reads, and it will not work on short libraries.
2. Input coverage is reasonable, preferably >=30x.
      * Check the average base qualities of the input dataset. Dorado Correct expects accurate inputs for both mapping and inference.

## CLI reference

Here's a slightly re-formatted output from the Dorado `correct` subcommand for reference.

!!! Info

    Please check the --help output of your own installation of dorado as this page may be
    outdated and argument defaults have been omitted as they are platform specific.

```bash hl_lines="1"
> dorado correct --help

Positional arguments:
  reads             Path to a file with reads to correct in FASTQ format.

Optional arguments:
  -h, --help        shows help message and exits
  -v, --verbose     [may be repeated]

Resources arguments:
  -x, --device      Specify CPU or GPU device
  -t, --threads     Number of threads for processing. Default uses all available threads.
  --infer-threads   Number of threads per device.

Input/output arguments:
  -m, --model-path  Path to correction model folder.
  -p, --from-paf    Path to a PAF file with alignments. Skips alignment computation.
  --to-paf          Generate PAF alignments and skip consensus.
  --resume-from     Resume a previously interrupted run.
                        Requires a path to a file where sequence headers are stored in the first column
                        (whitespace delimited), one per row.

Advanced arguments:
  -b, --batch-size  Batch size for inference.
  -i, --index-size  Size of index for mapping and alignment. Decrease index size to lower memory footprint.
```
