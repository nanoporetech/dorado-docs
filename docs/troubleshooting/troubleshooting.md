# Troubleshooting

This page contains Dorado troubleshooting advice to help users resolve issues which are known
to appear from time to time.

If you have an issue that cannot be resolved following the advice below please raise a new issue on the
[Dorado GitHub issues](https://github.com/nanoporetech/dorado/issues) page providing as
much information as possible and the Dorado team will aim to respond promptly.

You can also seek advice from the [Nanopore Community](https://community.nanoporetech.com/docs?from=support).

## Errors and warnings

Dorado will issue warnings and errors to `stderr` during runtime and may terminate if an
unrecoverable error occurs. Many errors stem from incorrect configuration of the
command line and the following are examples of common
[issues](https://github.com/nanoporetech/dorado/issues) reported on GitHub.

### No supported chemistry found

```text
[error] No supported chemistry found for flowcell_code: '__UNKNOWN_FLOWCELL__' sequencing_kit: '__UNKNOWN_KIT__' sample_rate: 5000
[error] This is typically seen when using prototype kits. Please download an appropriate model for your data and select it by model path
```

When using automatic [model selection complex]({{find("complex")}}) dorado must be able to
determine which model to use by inspecting the input data which must be in POD5 format.

If your data doesn't contain a recognised flow cell (e.g. `__UNKNOWN_FLOWCELL__`) or
sequencing_kit (e.g. `__UNKNOWN_KIT__`) dorado cannot find a suitable model for your data.

To basecall your data you need to first [download]({{find("downloader")}}) a basecalling model
which is appropriate for your data and specify the model using its **filepath** as
shown in the [simplex basecalling quick-start]({{find("simplex")}}) or in the example below:

```dorado
dorado download --model dna_r9.4.1_e8_hac@v3.3
dorado basecaller dna_r9.4.1_e8_hac@v3.3 reads/ > calls.bam
```

For details please check out the [models introduction]({{find("models")}}) and
the [models list]({{find("list")}}).

## Runtime issues

### CUDA Out Of Memory

Dorado supports multiple model architectures which can vary significantly in size (`fast, hac, sup`).
Multiple models are also used together when using features such as modification basecalling,
stero duplex basecalling and hemi-methylation duplex basecalling. As such there are
cases where excessive GPU memory consumption can unexpectedly terminate Dorado.

Unless specified otherwise by the user Dorado will attempt to calculate the optimal
batch size using the auto batch size protocol.
This algorithm tests multiple batch sizes for the models in use and selects the batch size which
gives the best performance.
However, many factors could result in this algorithm selecting a batch size which may
exceed the available GPU memory especially when combined with modification / stereo duplex models.

These factors include but are not limited to:

- Other processes using GPU resources (including other instances of Dorado)
- Display devices
- GPU with insufficient memory (Dorado does not support GPUs with <8GB of memory)

To resolve CUDA out-of-memory issues inspect the Dorado output from a previous run which should
report the batch size used as shown in the example below:

```text hl_lines="3"
dorado basecaller <model> <reads> ... > calls.bam
[info] > Creating basecall pipeline
[info]  - set batch size to 480
```

This example shows a batch size of `480`. We can use this as a guide for specifying the batch size
manually using the  `--batchsize` argument in `basecaller` and `duplex`. Reduce the batchsize
by a even values such as `32, 48, 64` starting with approximately 10%
of the original auto batchsize estimate `480-48=432` giving:

```dorado
dorado basecaller <model> <reads> --batchsize 432 ... > calls.bam
```

Repeat the above until Dorado completes successfully without running out of GPU memory.

### Low GPU utilization

Low GPU utilization can lead to reduced basecalling speed. This problem can be identified using
tools such as `nvidia-smi` and `nvtop`. Low GPU utilization often stems from I/O bottlenecks
in basecalling.

Here are a few steps you can take to improve the situation:

1. Use POD5 instead of .fast5:
    - POD5 has superior I/O performance and will enhance the basecall speed in I/O constrained environments.
2. Transfer data to the local disk before basecalling:
    - Frequently network disks cannot supply Dorado with adequate I/O speeds.
        To mitigate this, make sure your data is as close to your host machine as possible.
3. Choose SSD over HDD:
    - Particularly for duplex basecalling, using a local SSD can offer significant speed advantages.
        This is due to the duplex basecalling algorithm's reliance on heavy random access of data.

### Library path errors

Dorado comes equipped with the necessary libraries (such as CUDA) for its execution.
However, on some operating systems, the system libraries might be chosen over Dorado's.
This discrepancy can result in various errors, for instance, `CuBLAS error 8`.

To resolve this issue, you need to set the `LD_LIBRARY_PATH` to point to Dorado's libraries.
Use a command like the following to change path as appropriate:

=== "Linux"

    ```bash
    $ export LD_LIBRARY_PATH=<PATH_TO_DORADO>/dorado-{{dorado.version}}-linux-x64/lib:$LD_LIBRARY_PATH
    ```

=== "MacOS"

    ```bash
    $ export DYLD_LIBRARY_PATH=<PATH_TO_DORADO>/dorado-{{dorado.version}}-osx-arm64/lib:$DYLD_LIBRARY_PATH
    ```

### Windows PowerShell encoding

When running in PowerShell on Windows, care must be taken, as the default encoding for application
output is typically `UTF-16LE`.  This will cause file corruption if standard output is redirected to a file.

It is recommended to use the `--output-dir` argument to emit BAM files if PowerShell must be used.

For example, the following command will create corrupt output which cannot be read by samtools:

```dorado
PS > dorado basecaller <args> > out.bam
```

Instead, use:

```dorado
PS > dorado basecaller <args> --output-dir .
```

!!! warning inline end

    Using `out-file` with `Ascii` encoding will not produce well-formed **BAM** (binary) files.

For text-based output formats (SAM or FASTQ), it is possible to override the encoding on
output using the out-file command.

This command will produce a well formed ascii **SAM** file:

```dorado
PS > dorado basecaller <args> --emit-sam | out-file -encoding Ascii out.sam
```

Read more about PowerShell output encoding [here](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_character_encoding?view=powershell-7.4).
