# Getting Started

## Installation

### From The Web

Dorado can be installed from pre-built binaries for multiple platforms using the following links {{ dorado.version }} :

* [dorado-{{ dorado.version }}-linux-x64](https://cdn.oxfordnanoportal.com/software/analysis/dorado-{{ dorado.version }}-linux-x64.tar.gz)
* [dorado-{{ dorado.version }}-linux-arm64](https://cdn.oxfordnanoportal.com/software/analysis/dorado-{{ dorado.version }}-linux-arm64.tar.gz)
* [dorado-{{ dorado.version }}-osx-arm64](https://cdn.oxfordnanoportal.com/software/analysis/dorado-{{ dorado.version }}-osx-arm64.zip)
* [dorado-{{ dorado.version }}-win64](https://cdn.oxfordnanoportal.com/software/analysis/dorado-{{ dorado.version }}-win64.zip)

Once the relevant `.tar.gz` or `.zip` archive has been downloaded, extract the archive to your desired location.

### From Command Line

=== "Linux x86"

    Navigate to the desired install path and run:

    ```bash
    curl "https://cdn.oxfordnanoportal.com/software/analysis/dorado-{{ dorado.version }}-linux-x64.tar.gz" -o dorado-{{ dorado.version }}-linux-x64.tar.gz
    tar -xzf dorado-{{ dorado.version }}-linux-x64.tar.gz
    dorado-{{ dorado.version }}-linux-x64/bin/dorado --version
    ```

=== "Linux arm64"

    Navigate to the desired install path and run:

    ```bash
    curl "https://cdn.oxfordnanoportal.com/software/analysis/dorado-{{ dorado.version }}-linux-arm64.tar.gz" -o dorado-{{ dorado.version }}-linux-arm64.tar.gz
    tar -xzf dorado-{{ dorado.version }}-linux-arm64.tar.gz
    dorado-{{ dorado.version }}-linux-arm64/bin/dorado --version
    ```

=== "MacOS"

    Navigate to the desired install path and run:

    ```bash
    curl "https://cdn.oxfordnanoportal.com/software/analysis/dorado-{{ dorado.version }}-osx-arm64.zip" -o dorado-{{ dorado.version }}-osx-arm64.zip
    unzip dorado-{{ dorado.version }}-osx-arm64.zip
    dorado-{{ dorado.version }}-osx-arm64/bin/dorado --version
    ```

### Supported Platforms

Dorado has been tested extensively and supported on the following systems:

| Platform | GPU/CPU | Minimum Software Requirements |
| -------- |---------|-------------------------------|
| Linux x86_64  | (G)V100, A100  | CUDA Driver ≥450.80.02 |
|               | H100           | CUDA Driver ≥520 |
| Linux arm64   | Jetson Orin    | Linux for Tegra ≥34.1.1 |
| Windows x86_64 | (G)V100, A100 | CUDA Driver ≥452.39 |
|               | H100           | CUDA Driver ≥520 |
| Apple         | Apple Silicon (M1/M2/M3) | |

Linux or Windows systems not listed above but which have Nvidia GPUs with ≥8 GB VRAM and architecture
from Pascal onwards (except P100/GP100) have not been widely tested but are expected to work.
When basecalling with Apple devices, we recommend systems with ≥16 GB of unified memory.

If you encounter problems with running on your system, please [report an issue](https://github.com/nanoporetech/dorado/issues).

---

## Dorado Command Line Interface (CLI) Basics

Dorado is a command line tool and `dorado` is the name of the binary executable. If [installed]({{find("index")}}#installation) correctly
dorado will be on your `PATH` or in installed into some known directory.

If dorado is installed into the `PATH` you should be able to view the top-level help as shown below.

```dorado
dorado --help
```

Alternatively, if dorado is in a known path or in the current working directory try:

```dorado
./dorado --help
/path/to/dorado --help
```

## Dorado Subcommands

Dorado has multiple subcommands which are used to launch specific tools such as the `basecaller`. To view all
available subcommands inspect the top-level help:

```dorado hl_lines="1"
> dorado --help
Usage: dorado [options] subcommand

Positional arguments:
aligner
basecaller
correct
demux
download
duplex
summary
trim

Optional arguments:
-h --help               shows help message and exits
-v --version            prints version information and exits
-vv                     prints verbose version information and exits
```

To launch a dorado subcommand use the following structure:

```dorado
dorado <subcommand> --help > calls.bam
```

For example, to launch the `basecaller` use:

```dorado
dorado basecaller --help
```

## Redirecting Output

There are many resources (see [gnu.org](https://www.gnu.org/software/bash/manual/html_node/Redirections.html))
which explain the details of output re-direction but below are some examples uses of re-direction
in dorado.

Some dorado subcommands write it's business logic output to `stdout` and other runtime information to `stderr`.
Examples of business logic output may be basecalls in a `.bam` file generated during basecalling. To write
these outputs to a file we must redirect the `stdout` output to a file.

Below is an example of writing the `stdout` output from `dorado basecaller` (which by default is a `.bam` file)
using the `>` redirection operator. The `stderr` (runtime information) will be written to the terminal as normal.

```dorado
dorado basecaller ... > calls.bam
```

!!! tip inline end

    To view the `my.log` info in real-time while it's being written by dorado try:

    ```bash
    tail -f dorado.log
    ```

To write the `stderr` runtime information to a log file use the `&>` `stderr` redirection operator.

```dorado
dorado basecaller ... > calls.bam &> dorado.log
```

Some dorado subcommands can be "chained" together where the output of one is the input to the other.
For example, `dorado basecaller` can generate a `.bam` file which is an input to `dorado demux` which
can split this `.bam` file into files by barcode. This can be done with the `|` pipe operator.

```dorado
dorado basecaller ... | dorado demux --output demuxed
```

## Command Line Arguments

Dorado subcommands are controlled from the command line using arguments.
The available arguments for a specific subcommand can be seen by using the
`--help` argument as shown above.

Arguments are either **positional** or **optional**.

### Positional Arguments

Positional arguments are arguments which must be specified in a specific position relative to others.
The order of positional arguments matters. The dorado subcommand is an example of a positional
argument as shown in the above examples.

Using `dorado basecaller` as another example we can see following part of the `--help` output:

```text
Positional arguments:
  model    model selection {fast,hac,sup}@v{version} ...
  data     the data directory or file (POD5/FAST5 format).
```

!!! tip inline end

    We recommend always placing positional arguments **before** optional arguments.

This information is stating that we must place the `model` and `data` arguments in that order as shown:

```dorado
dorado basecaller sup reads/ > calls.bam
```

### Optional Arguments

!!! note inline end

    Optional arguments may be **required** by the dorado subcommand.

Optional arguments are arguments which **may or may not be required**, and may themselved require zero or more
values as inputs. Optional arguments requiring no additional values are also know as
"flags", "toggles" or "switches".

All optional arguments are prefixed by a double hyphen `--argument`.

Some optional arguments may have a
one character abbreviation prefixed by a single hyphen such as `-a`.
Throughout this documentation when describing optional arguments they will be
shown as `-a / --argument` if an abbreviation exists.

Using `dorado basecaller` again we can see following part of the `--help` output listing the optional arguments:

```text
Optional arguments:
  -h, --help         shows help message and exits
  -v, --verbose      [may be repeated]
  -x, --device       device string in format ...
  -l, --read-ids     A file with a newline-delimited list of reads ...
  ...
```

Here is a complete command with both positional and optional arguments:

```dorado
dorado basecaller sup reads/ --device cuda:0 --min-qscore 10 --reference reference.fasta --no-trim > calls.bam
```

!!! warning

    Optional arguments which take **multiple values** cause issues with positional arguments.

    As such they **must be placed after all positional arguments**.

    ```dorado
    # Invalid - sup is consumed by --modified-bases
    dorado basecaller --modified-bases 5mC 6mA sup --device cuda:0 reads/
    ```
    ```dorado
    # Valid
    dorado basecaller sup reads --modified-bases 5mC 6mA --device cuda:0
    ```

## Runtime Information and Verbose Output

Dorado and its subcommands will generate some runtime information (logging) which is
written to `stderr`. All subcommands have the `-v / --verbose` argument which can be used to increase
the amount of information shown in these messages by adding `[debug]` messages to the output.
The verbose output can be specified multiple times (e.g. `-vv`) to additionally include `[trace]` messages.

These messages are typically in the format shown below which contains a timestamp,
message severity and the message.

```text
[2024-01-01 00:00:00.000] [trace] <detailed debug message - not useful in normal use - may affect performance>
[2024-01-01 00:00:00.000] [debug] <debug message - likely not useful in normal use>
[2024-01-01 00:00:00.000] [info] <useful information message>
[2024-01-01 00:00:00.000] [warning] <warning message - there may be an issue>
[2024-01-01 00:00:00.000] [error] <error message - there is significant issue>
```

It's **not recommended** to set any additional level of logging output (e.g. `-v` or `-vv`) in normal use
as it can affect performance. However, if you experience an issue please first include
a single `-v` while attempting to investigate the issue as it might yield insightful
information which may otherwise be hidden.

If you create a ticket on our [GitHub issues]({{ github.issues }})
page please add debugging output if possible.

## Specifying Hardware Resources

Many of dorado's subcommands may be able to make use of modern GPU (Graphical Processing Unit) hardware (e.g. NVidia CUDA GPUs). Dorado subcommands which support GPU acceleration will provide the `-x / --device` command line
argument.

The valid values for the `-x / --device` argument are `cpu`, `metal` and `cuda:*`.

The `*` in `cuda:*` can be used to select which specific CUDA devices are used.

Valid examples are:

* `cuda:0` select the first (best) device - Devices are zero-indexed.
* `cuda:1,2,3` select the second, third, and fourth device.
* `cuda:all` and `cuda:auto` select **all** devices

The default chosen for `-x / --device` is reported in the `--help` for each command.

=== "Linux & Windows"

    ```text hl_lines="7"
    ❯ dorado basecaller --help
    [info] Running: "basecaller" "--help"
    ...
    Optional arguments:
      -h, --help                  shows help message and exits
      -v, --verbose               [may be repeated]
      -x, --device                device string in format ... [default: "cuda:all"]
    ...
    ```

=== "MacOS"

    ```text hl_lines="7"
    ❯ dorado basecaller --help
    [info] Running: "basecaller" "--help"
    ...
    Optional arguments:
      -h, --help                  shows help message and exits
      -v, --verbose               [may be repeated]
      -x, --device                device string in format ... [default: "metal"]
    ...
    ```