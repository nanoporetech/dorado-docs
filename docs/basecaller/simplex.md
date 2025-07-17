# Simplex Basecalling

## Quick start

To run Dorado basecalling, using the [automatically downloaded]({{find("complex")}}) `hac` model
on a directory of POD5 files or a single POD5 file use:

```dorado
dorado basecaller hac pod5s/ > calls.bam
```

To basecall a single file, simply replace the directory `pod5s/` with a path to your data.

```dorado
dorado basecaller hac /path/to/reads.pod5 > calls.bam
```

To automatically download and use the `fast` or `sup` models try the following:

```dorado
dorado basecaller fast pod5s/ > calls.bam
dorado basecaller sup  pod5s/ > calls.bam
```

If you have a model that has already been [downloaded]({{find("downloader")}}) you can specify that
**simplex** model using a path. For more information on how models are downloaded and how they
can be re-used please see the [downloader documentation]({{find("downloader")}}#downloading-models).

```dorado
dorado basecaller /path/to/simplex_model/ pod5s/ > calls.bam
```

### Adding modified bases

To add modified basecalling extend the [model complex]({{find("complex")}}) or refer to
modified basecalling [usage guide]({{find("mods")}}#usage) for more details on the other options available.

```dorado
dorado basecaller hac,5mC     pod5s/ > calls.bam
dorado basecaller sup,6mA,5mC pod5s/ > calls.bam
```

### Selecting data

To basecall all reads in a nested directory structure [recursively]({{find("basecall_overview")}}#data-ingest)
use `-r / --recursive`:

```dorado
dorado basecaller hac data/ --recursive  > calls.bam
```

To basecall only a limited number reads use the `-n / --max-reads` argument:

```dorado
dorado basecaller hac data/ --max-reads 100  > calls.bam
```

!!! tip inline end

    You can generate a list of read ids using the [`pod5 view` tool](https://pod5-file-format.readthedocs.io/en/latest/docs/tools.html#pod5-view).

To basecall a specific selection of reads use the `-l / --read-ids` argument passing in a file path
to a newline-delimited list of read ids. Only these read ids will be basecalled.

```dorado
dorado basecaller hac data/ --read-ids read_ids.txt > calls.bam
```

### Resume basecalling

If basecalling is interrupted, it is possible to resume basecalling from a BAM file.
To do so, use the `--resume-from` flag to specify the path to the incomplete BAM file.

```dorado
dorado basecaller hac pod5s/ --resume-from incomplete.bam > calls.bam
```

!!! warning
    Do not reuse the filenames for `--resume-from` and the new output.

    If they are the same then the interrupted file will be **deleted** when
    Dorado is launched and the previous work will be lost.

    ```dorado
    # WARNING: This will overwrite the existing `resume.bam` file before it is used.
    dorado basecaller hac pod5/ --resume-from resume.bam > resume.bam
    ```

## Read trimming

See [read trimming]({{find("read_trimming")}}).

---

## CLI reference

Here's a slightly re-formatted output from the Dorado `basecaller` subcommand for reference.

!!! info

    Please check the `--help` output of your own installation of Dorado as this page may be outdated
    and argument defaults have been omitted as they are platform specific.

```text hl_lines="1"
> dorado basecaller --help

Positional arguments:
  model                       Model selection {fast,hac,sup}@v{version} for automatic model selection
                                including modified bases, or path to existing model directory.
  data                        The data directory or file (POD5/FAST5 format).

Optional arguments:
  -h, --help                  shows help message and exits
  -v, --verbose               [may be repeated]
  -x, --device                Specify CPU or GPU device: 'auto', 'cpu', 'cuda:all' or 'cuda:<id>[,<id>...]'.
                                Specifying 'auto' will choose either 'cpu', 'metal' or 'cuda:all' depending
                                on the presence of a GPU device.
  --models-directory          Optional directory to search for existing models or download new models into.
  --bed-file                  Optional bed-file. If specified, overlaps between the alignments and
                                bed-file entries will be counted, and recorded in BAM output using
                                the 'bh' read tag.

Input data arguments:
  -r, --recursive             Recursively scan through directories to load FAST5 and POD5 files.
  -l, --read-ids              A file with a newline-delimited list of reads to basecall. If not provided,
                                all reads will be basecalled.
  -n, --max-reads             Limit the number of reads to be basecalled.
  --resume-from               Resume basecalling from the given HTS file. Fully written read records are
                                not processed again.
  --disable-read-splitting    Disable read splitting

Output arguments:
  --min-qscore                Discard reads with mean Q-score below this threshold.
  --emit-moves                Write the move table to the 'mv' tag.
  --emit-fastq                Output in fastq format.
  --emit-sam                  Output in SAM format.
  -o, --output-dir            Optional output folder, if specified output will be written to a calls file
                                (calls_<timestamp>.sam|.bam|.fastq) in the given folder.

Alignment arguments:
  --reference                 Path to reference for alignment.
  --mm2-opts                  Optional minimap2 options string. For multiple arguments surround with
                                double quotes.

Modified model arguments:
  --modified-bases            A space separated list of modified base codes. Choose from:
                                pseU, 5mCG_5hmCG, 5mC, 6mA, 5mCG, m6A_DRACH, m6A, 5mC_5hmC, 4mC_5mC.
  --modified-bases-models     A comma separated list of modified base model paths.
  --modified-bases-threshold  The minimum predicted methylation probability for a modified base
                                to be emitted in an all-context model, [0, 1].

Barcoding arguments:
  --kit-name                  Enable barcoding with the provided kit name. Choose from:
                                  EXP-NBD103 EXP-NBD104 EXP-NBD114 EXP-NBD114-24 EXP-NBD196 EXP-PBC001
                                  EXP-PBC096 SQK-16S024 SQK-16S114-24 SQK-LWB001 SQK-MLK111-96-XL
                                  SQK-MLK114-96-XL SQK-NBD111-24 SQK-NBD111-96 SQK-NBD114-24 SQK-NBD114-96
                                  SQK-PBK004 SQK-PCB109 SQK-PCB110 SQK-PCB111-24 SQK-PCB114-24 SQK-RAB201
                                  SQK-RAB204 SQK-RBK001 SQK-RBK004 SQK-RBK110-96 SQK-RBK111-24 SQK-RBK111-96
                                  SQK-RBK114-24 SQK-RBK114-96 SQK-RLB001 SQK-RPB004 SQK-RPB114-24
                                  TWIST-16-UDI TWIST-96A-UDI VSK-PTC001 VSK-VMK001 VSK-VMK004 VSK-VPS001.
  --sample-sheet              Path to the sample sheet to use.
  --barcode-both-ends         Require both ends of a read to be barcoded for a double ended barcode.
  --barcode-arrangement       Path to file with custom barcode arrangement.
  --barcode-sequences         Path to file with custom barcode sequences.
  --primer-sequences          Path to file with custom primer sequences.

Trimming arguments:
  --no-trim                   Skip trimming of barcodes, adapters, and primers.
                                If option is not chosen, trimming of all three is enabled.
  --trim                      Specify what to trim. Options are 'none', 'all', 'adapters', and 'primers'.
                                Default behaviour is to trim all detected adapters, primers, or barcodes.
                                Choose 'adapters' to just trim adapters.
                                The 'primers' choice will trim adapters and primers, but not barcodes.
                                The 'none' choice is equivalent to using --no-trim.
                                Note that this only applies to DNA. RNA adapters are always trimmed.

Poly(A) arguments:
  --estimate-poly-a           Estimate poly(A/T) tail lengths (beta feature).
                                Primarily meant for cDNA and dRNA use cases.
  --poly-a-config             Configuration file for poly(A) estimation to change default behaviours

Advanced arguments:
  -b, --batchsize             The number of chunks in a batch. If 0 an optimal batchsize will be selected.
  -c, --chunksize             The number of samples in a chunk.
  --overlap                   The number of samples overlapping neighbouring chunks.
```
