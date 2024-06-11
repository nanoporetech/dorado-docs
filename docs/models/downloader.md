---
model_desc: "../models/models.md"
model_list: "../models/list.md"
model_complex: "../models/complex.md"
---
# Downloader

Dorado can download [models]({{model_desc}}) from the Oxford Nanopore's Content Delivery Network (CDN) using the `dorado download`
command.

```text hl_lines="1"
❯ dorado download --help

Usage: dorado [--help]
    [--model (<model_name>|"all")]
    [--models-directory PATH]
    [--list] [--list-yaml] [--list-structured]
    [--data VAR] [--recursive] [--overwrite] [--verbose]...

Optional arguments:
  -h, --help          shows help message and exits
  --model             the model to download [nargs=0..1] [default: "all"]
  --models-directory  the directory to download the models into [nargs=0..1] [default: "."]
  --list              list the available models for download
  --list-yaml         list the available models for download, as yaml, to stdout
  --list-structured   list the available models in a structured format, as yaml, to stdout
  --data              path to POD5 data used to automatically select models [nargs=0..1] [default: ""]
  -r, --recursive     recursively scan through directories to load POD5 files
  --overwrite         overwrite existing models if they already exist
  -v, --verbose       [may be repeated]
```

## Downloading Models

### Download all models

To download all models use:

```dorado
dorado download --model all
```

### Download models for a specific condition

To download models for a specific sequencing condition and model speed, provide a
[model complex]({{model_complex}}) to the `--model` argument
and set the `--data` argument to path to your pod5 input data (.fast5 is not supported).

Dorado will then download the simplex and modbase models matching the condition and model complex selection.

```dorado
dorado download --model sup --data pod5s/
```

### Download specific models

To find and download a specific model use the following command to view a list of all available models.
These are also noted in the [Models List]({{model_list}}) below.

```dorado
dorado download --list
```

which shows an output like this where model names are printed for each model type

```text
> simplex models
 - dna_r10.4.1_e8.2_400bps_hac@v5.0.0
 - dna_r10.4.1_e8.2_400bps_sup@v5.0.0
 ...
> modification models
 - dna_r10.4.1_e8.2_400bps_sup@v5.0.0_6mA@v1
 ...
```

The models can then be downloaded using their model name as shown below

```dorado
dorado download --model <model_name>
```

### Download models into a specific directory

By default `dorado download` will download models into the current working directory.
Use the `--models-directory` argument to specify a directory to save downloaded models into.

```dorado
dorado download --model <model_name> --models-directory /path/to/models_directory
```

!!! tip

    The `--models-directory` argument is available on many dorado commands (e.g. `dorado basecaller`)
    to specify a directory to search for existing models.
    This can be used to avoid repeatedly downloading models.

## Model Search Directory and Temporary Downloads

Dorado tools can automatically download models when provided with a [model complex]({{model_complex}})
and POD5 data.

Once the automatic model selection process has found the appropriate model name matching the selection and data,
dorado will search for existing models to avoid downloading models unnecessarily.

The behaviour of this search can be controlled as listed below and are in order of decreasing priority:

1. Setting the `--models-directory` CLI argument.
2. Setting the `DORADO_MODELS_DIRECTORY` environment variable.
3. If neither `--models-directory` or `DORADO_MODELS_DIRECORY` are set then the **current working directory is searched**.

If `--models-directory` or `DORADO_MODELS_DIRECTORY` is set, automatically downloaded models will persist,
otherwise models will be downloaded into a local temporary directory and deleted after dorado has finished
using the model.

### Examples

The example below shows that without using `--models-directory` automatic model selection will download and
clean up models on every use of dorado.

```dorado
# Model is downloaded into temporary directory and cleaned when dorado is finished
dorado basecaller sup pod5s/ > calls.bam

ls *sup*
# No results

# Model is re-downloaded and cleaned up again
dorado basecaller sup pod5s/ > calls.bam
```

The example below shows that when using `--models-directory`, automatic model selection will
download models that are missing and reuse previously existing models.

```dorado
# Model is downloaded into models/
dorado basecaller sup pod5s/ --models-directory models/ > calls.bam

ls models/
    dna_r10.4.1_e8.2_400bps_sup@v5.0.0

# Model is re-used
dorado basecaller sup pod5s/ --models-directory models/ > calls.bam
```

Models can be re-used as shown above but by using the `DORADO_MODELS_DIRECTORY`
environment variable. This can be set once in a user configuration file and re-used without
needing to set the `--models-directory` argument on the command line.

```bash
export DORADO_MODELS_DIRECTORY="/path/to/models/"
```

The environment variable can also be set inline with dorado but this is just shown for completeness.

```dorado
DORADO_MODELS_DIRECTORY=/path/to/models/ dorado basecaller sup pod5s/ > calls.bam
```
