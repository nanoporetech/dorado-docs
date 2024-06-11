# Read Trimming

Dorado can trim adapters and/or primer sequences from the beginning and end of DNA and
RNA reads during basecalling

For DNA basecalls only, trimming can be done as a separate step after basecalling
using the `dorado trim` subcommand.

!!! info "RNA Trimming"

    RNA trimming is always done in-line with basecalling and cannot be done afterwards
    using `dorado trim`.

!!! warning "Demultiplexing trimmed data"

    Trimming adapters and primers may result in parts of the barcode flanking
    regions being removed, which could [interfere with demultiplexing](#effect-on-demultiplexing).

## Trimming While Basecalling

`dorado basecaller` will attempt to detect any adapter or primer sequences at
the beginning and end of reads, and remove them from the output sequence.

This functionality can be controlled using either the `--trim` or `--no-trim` options
with `dorado basecaller`.

The `--trim` option takes as its argument one of the following values:

| Option    | Adapters | Primers | Barcodes | Description |
| ------:    | :--------:|:-------: | :--------: | ----------- |
| `all` | :material-content-cut: | :material-content-cut: | :material-content-cut: | Detected adapters or primers will be trimmed.<br />If barcoding is enabled, detected barcodes will be trimmed.<br />This is the default option |
| `primers` | :material-content-cut: | :material-content-cut: | | Detected adapters or primers will be trimmed.<br />If barcoding is enabled, detected barcodes will **not** be trimmed. |
| `adapters`| :material-content-cut: | | | Detected adapters will be being trimmed, but primers will **not** be trimmed.<br />If barcoding is enabled, detected barcodes will **not** be trimmed. |
| `none`    | | | | Nothing will be trimmed. Equivalent to `--no-trim`     |

## Trimming Existing Datasets

The `dorado trim` subcommand can be used to trim adapters and/or primer sequences in
existing basecalled datasets. To do this, run:

```dorado
dorado trim <calls> > trimmed.bam
```

`<calls>` can either be an HTS format file (e.g. FASTQ, BAM, etc.) or a stream of an
HTS format (e.g. the output of Dorado basecalling).

```dorado
dorado basecaller <model> <reads> ... | dorado trim > trimmed.bam
```

The `--no-trim-primers` option can be used to prevent the trimming of primer sequences.
In this case only adapter sequences will be trimmed.

If it is also your intention to demultiplex the data, then it is recommended that you
demultiplex before trimming any adapters and primers, as trimming adapters and primers
first may interfere with correct barcode classification.

The output of `dorado trim` will always be unaligned records, regardless of whether the
input is aligned/sorted or not.

### Dorado Trim CLI Reference

```bash
Positional arguments:
  reads               Path to a file with reads to trim. Can be in any HTS format. [nargs: 0 or more]

Optional arguments:
  -h, --help          shows help message and exits
  -v, --verbose       [may be repeated]
  -t, --threads       Combined number of threads for adapter/primer detection and output generation.
                        Default uses all available threads.
Input arguments:
  -n, --max-reads     Maximum number of reads to process.
  -l, --read-ids      A file with a newline-delimited list of reads to trim.

Output arguments:
  --emit-fastq        Output in fastq format. Default is BAM.

Main arguments:
  --no-trim-primers   Skip primer detection and trimming. Only adapters will be detected and trimmed.
  --primer-sequences  Path to file with custom primer sequences.

```

## Custom Primer Trimming

!!! note inline end

    Using the `--primer-sequences` argument will remove the Oxford Nanopore kits from the
    trimming search.

Dorado searches for primer sequences used in Oxford Nanopore kits. However, you can specify
an alternative set of primer sequences to search for when trimming either in-line with basecalling,
or when using `dorado trim` directly.

In both cases this is accomplished using the `--primer-sequences` argument, followed by the
path to a `FASTA` file containing the primer sequences you want
to search for. The record names of the sequences do not matter.

## Effect on Demultiplexing

If adapter/primer trimming is done while basecalling in combination with demultiplexing,
then dorado will ensure that the trimming of adapters and primers does
not interfere with the demultiplexing process.

For example, trimming will not effect demultiplexing on `kit-name` in the following command:

```dorado
dorado basecaller <model> reads/ --kit-name <kit-name> --trim all
```

However, if you intend to do demultiplexing as a separate step, it is recommended that
trimming is disabled when basecalling with the `--no-trim` option, to ensure that barcode sequences
remain intact in the calls.

```dorado
dorado basecaller <model> <reads> --no-trim ... > calls.bam
dorado demux calls.bam --kit-name <kit-name> --output-dir <output-dir> ...
```
