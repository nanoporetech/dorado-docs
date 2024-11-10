# Duplex Basecalling

Duplex basecalling is an extension to the simplex basecalling process where Dorado continues by
pairing template and complement strands, combines all the information for both strands
including the basecalls, Q-scores and, signal and passes this through a stereo duplex
model. The stereo duplex model considers this combined information to improve the basecalling accuracy.

Please watch this video on [YouTube](https://www.youtube.com/embed/8DVMG7FEBys?si=XUHn3DwZCKOPI1k8) for an introduction to Duplex basecalling.

## Quick start

To run Dorado duplex basecalling, using an automatically [downloaded]({{find("downloader")}})
`hac` model on a directory of POD5 files or a single POD5 file
(.fast5 files are supported, but will not be as performant).

```dorado
dorado duplex hac  pod5s/ > calls.duplex.bam
```

!!! warning inline end

    The `fast` model is not recommended for duplex basecalling

To basecall a single file, simply replace the directory `pod5s/` with a path to your data.

```dorado
dorado duplex hac  /path/to/reads.pod5 > calls.duplex.bam
```

To automatically download and use the `sup` (super-accurate) models try the following:

```dorado
dorado duplex sup  pod5s/ > calls.duplex.bam
```

If you have a model that has already been [downloaded]({{find("downloader")}}) that you want
to reuse you can use the model path directly.

```dorado
dorado duplex /path/to/model/ pod5s/ > calls.duplex.bam
```

Dorado will automatically download the required stereo duplex model if it wasn't found following the
[model search procedure]({{find("downloader")}}#model-search-directory-and-temporary-downloads).

## Duplex Sequence Metadata

When using the duplex command, two types of DNA sequence results will be produced: 'simplex' and 'duplex'.
Any specific position in the DNA which is in a duplex read is also seen in two simplex strands
(the template and complement). So, each DNA position which is duplex sequenced will be covered
by a minimum of three separate readings in the output.

Dorado records the this information in the `dx` BAM tag on all reads basecalled using `dorado duplex`.
The `dx` tag can be used to distinguish between simplex and duplex reads as follows:

| `dx`  | Read Description |
| ----- | ----------- |
| `1`   | A duplex read.|
| `0`   | A simplex read which has no duplex offspring. |
| `-1`  | A simplex read which has duplex offspring. |

Dorado will report the duplex rate as the number of nucleotides in the duplex basecalls
multiplied by two and divided by the total number of nucleotides in the simplex basecalls.
This value is a close approximation for the proportion of nucleotides which participated in a duplex basecall.

## Hemi-methylation duplex basecalling

Duplex basecalling can be performed with modified base detection, producing hemi-methylation calls for duplex reads.

```dorado
dorado duplex hac,5mCG_5hmCG pod5s/ > duplex.bam
```

More information on how hemi-methylation calls are represented can be found the
SAM [specification](https://samtools.github.io/hts-specs/SAMtags.pdf) and
Modkit [documentation](https://nanoporetech.github.io/modkit/intro_pileup_hemi.html).

## Duplex basecalling performance

Duplex basecalling is an IO-intensive process and can perform poorly if using networked storage or HDD.
This can generally be improved by splitting up POD5 files appropriately.
Firstly install the POD5 python tools ([documentation](https://pod5-file-format.readthedocs.io/en/latest/docs/tools.html)):

```bash
pip install pod5
```

Then run `pod5 view` to generate a table containing information to split on specifically,
the "channel" information.

```bash
pod5 view /path/to/your/dataset/ --include "read_id, channel" --output summary.tsv
```

This will create `summary.tsv` file which should look like:

```text
read_id channel
0000173c-bf67-44e7-9a9c-1ad0bc728e74    109
002fde30-9e23-4125-9eae-d112c18a81a7    463
...
```

Now run `pod5 subset` to copy records from your source data into a new output file per-channel.
This might take some time depending on the size of your dataset

```bash
pod5 subset /path/to/your/dataset/ --summary summary.tsv --columns channel --output split_by_channel
```

The command above will create the output directory `split_by_channel` and write into it
one POD5 file per unique channel. Duplex basecalling these split reads should now be much faster.

### Distributed duplex basecalling

If running duplex basecalling in a distributed fashion (e.g. on a SLURM or Kubernetes cluster)
it is important to split POD5 files as described above.
The reason is that duplex basecalling requires aggregation of reads from across a whole
sequencing run, which will be distributed over multiple POD5 files.

The splitting strategy described above ensures that all reads which need to be aggregated
are in the same POD5 file.
Once the split is performed one can execute multiple jobs against smaller subsets of POD5
(e.g one job per 100 channels). This will allow basecalling to be distributed across nodes on a cluster.

This will generate multiple BAMs which can be merged. This approach also offers some resilience
as if any job fails it can be restarted without having to re-run basecalling against the entire dataset.

## CLI reference

Here's a slightly re-formatted output from the `dorado duplex` subcommand for reference.

!!! info

    Please check the `--help` output of your own installation of dorado as this page may be outdated
    and argument defaults have been omitted as they are platform specific.

```text hl_lines="1"
❯ dorado duplex --help

Positional arguments:
  model                       Model selection {fast,hac,sup}@v{version} for automatic model selection
                                including modbases, or path to existing model directory.
  reads                       Reads in POD5 format or BAM/SAM format for basespace.

Optional arguments:
  -h, --help                  shows help message and exits
  -v, --verbose               [may be repeated]
  -x, --device                Specify CPU or GPU device: 'auto', 'cpu', 'cuda:all' or 'cuda:<id>[,<id>...]'.
                                Specifying 'auto' will choose either 'cpu', 'metal' or 'cuda:all'
                                depending on the presence of a GPU device.
  --models-directory          Optional directory to search for existing models or download new models into.

Input data arguments:
  -r, --recursive             Recursively scan through directories to load FAST5 and POD5 files.
  -l, --read-ids              A file with a newline-delimited list of reads to basecall.
                                If not provided, all reads will be basecalled.
  --pairs                     Space-delimited csv containing read ID pairs. If not provided, pairing
                                will be performed automatically.

Output arguments:
  --min-qscore                Discard reads with mean Q-score below this threshold.
  --emit-fastq                Output in fastq format.
  --emit-sam                  Output in SAM format.
  -o, --output-dir            Optional output folder, if specified output will be written to a calls
                                file (calls_<timestamp>.sam|.bam|.fastq) in the given folder.

Alignment arguments:
  --reference                 Path to reference for alignment.
  --mm2-opts                  Optional minimap2 options string. For multiple arguments surround
                                with double quotes.
  --bed-file                  Optional bed-file. If specified, overlaps between the alignments and
                                bed-file entries will be counted, and recorded in BAM output using
                                the 'bh' read tag.

Modified model arguments:
  --modified-bases            A space separated list of modified base codes. Choose from:
                                pseU, 5mCG_5hmCG, 5mC, 6mA, 5mCG, m6A_DRACH, m6A, 5mC_5hmC, 4mC_5mC.
  --modified-bases-models     A comma separated list of modified base models.
  --modified-bases-threshold  The minimum predicted methylation probability for a modified base to
                                be emitted in an all-context model, [0, 1].

Advanced arguments:
  -t, --threads
  -b, --batchsize             The number of chunks in a batch. If 0 an optimal batchsize will be selected.
  -c, --chunksize             The number of samples in a chunk.
  -o, --overlap               The number of samples overlapping neighbouring chunks.
```
