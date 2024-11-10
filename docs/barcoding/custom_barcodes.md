# Custom Barcode Arrangements

Dorado supports barcode demultiplexing using custom barcode arrangements.
These include customizations of existing kits (e.g. using only a subset of the barcodes
from a kit) or entirely new kits containing new barcode sequences and layouts.

The format to define a custom arrangement is inspired by the arrangement specification
in Guppy, with some adjustments to account for the algorithmic changes in Dorado.

Custom [barcode arrangements](#arrangement-file) are defined using a `toml` file,
and custom [barcode sequences](#sequences-file) are defined in a `FASTQ` file.

## Barcode reference diagram

A double-ended barcode with different flanks and barcode sequences for front and rear
barcodes is described here.

```text
 5' --- ADAPTER/PRIMER
... --- LEADING_FLANK_1 --- BARCODE_1 --- TRAILING_FLANK_1
... --- READ
... --- RC(TRAILING_FLANK_2) --- RC(BARCODE_2) --- RC(LEADING_FLANK_2)
... --- 3'
```

* For single-ended barcodes, there is no barcode sequence at the rear of the read.
* For double-ended barcodes which are symmetric, the flank and barcode sequences for front
* and rear windows are same.

For single-ended barcodes with the `rear_only_barcodes` flag set (see below), e.g. RNA kits,
the sequence description would look like this:

```text
 5' ---READ
... ---LEADING_FLANK_1 ---BARCODE_1 ---TRAILING_FLANK_1
... ---ADAPTER/PRIMER --- 3'
```

## Arrangement file

The following are all the options that can be defined in the arrangement file.

```toml
[arrangement]
name = "custom_barcode"
kit = "BC"

mask1_front = "ATCG"
mask1_rear = "ATCG"
mask2_front = "TTAA"
mask2_rear = "GGCC"

# Barcode sequences
barcode1_pattern = "BC%02i"
barcode2_pattern = "BC%02i"
first_index = 1
last_index = 96
rear_only_barcodes = true

## Scoring options
[scoring]
max_barcode_penalty = 11
barcode_end_proximity = 75
min_barcode_penalty_dist = 3
min_separation_only_dist = 6
flank_left_pad = 5
flank_right_pad = 10
front_barcode_window = 175
rear_barcode_window = 175
midstrand_flank_score = 0.95
```

### Arrangement options

The table below describes the arrangement options in more detail.

| Option | Required | Description |
| -- | -- | -- |
| name | **Yes** | Name of the barcode arrangement. This name will be used to report the barcode classification. |
| kit | | Which class of barcodes this arrangement belongs to (if any). |
| mask1_front | **Yes** | The leading flank for the front barcode. ^[1,2]^ |
| mask1_rear | **Yes** | The trailing flank for the front barcode. ^[1,2]^ |
| mask2_front | | The leading flank for the rear barcode. ^[1,3]^ |
| mask2_rear | | The trailing flank for the rear barcode. ^[1,3]^ |
| barcode1_pattern | **Yes** | An expression capturing the sequences to use for the front barcode. ^[4]^ |
| barcode2_pattern | | An expression capturing the sequences to use for the rear barcode. ^[4]^ |
| first_index | **Yes** | Start index for range of barcode sequences to use in the arrangement. Used in combination with the `last_index`. |
| last_index | **Yes** | End index for range of barcode sequences to use in the arrangement. Used in combination with the `first_index`. |
| rear_only_barcodes | | For single ended barcodes, the barcode is at the rear of the read rather than the front (e.g for an RNA kit). |

1. Can be empty string.
2. Applies to single and double-ended barcodes.
3. Applies to double-ended barcodes only.
4. Pattern must match sequences from pre-built kits list in Dorado or in the [custom sequences file](#sequences-file).

The pre-built barcode sequences in Dorado can be found in the [barcode_kits.cpp file]({{dorado.code}}/dorado/utils/barcode_kits.cpp)
under the `barcodes` map.

### Scoring options

Dorado maintains a default set of parameters for scoring each barcode to determine the best
classification. These parameters have been tuned based on barcoding kits from Oxford Nanopore.
However, the default parameters may not be optimal for new arrangements and kits.

The classification heuristic applied by Dorado is the following:

1. Dorado uses the flanking sequences defined in `maskX_front/rear` to find a window in the
    read where the barcode is situated.

2. For double-ended barcodes, the **best** window (either from the front or rear of the
    read) is chosen based on the alignment of the flanking mask sequences.

3. Each barcode candidate within the arrangement is aligned to the subsequence within the window.
    The alignment may optionally consider additional bases from the preceding/succeeding
    flank (as specified in the `flank_left_pad` and `flank_right_pad` parameters).

4. The edit distance of this alignment is assigned as a penalty to each barcode.

Once barcodes are sorted by barcode penalty, the top candidate is checked against the following rules:

1. Is the barcode penalty below `max_barcode_penalty` and the distance between the
    top 2 barcode penalties greater than `min_barcode_penalty_dist`?.

2. Is the barcode penalty above `max_barcode_penalty` but the distance between the
    top 2 barcodes penalties greater then `min_separation_only_dist`?

3. Is the flank score below the `min_flank_score`?

If a candidate meets (1) or (2) AND (3), and the location of the start/end of the barcode
construct is within `barcode_end_proximity` bases of the ends of the read, then it is considered a hit.

| Scoring option | Description |
| -- | -- |
| max_barcode_penalty | The maximum edit distance allowed for a classified barcode. Considered in conjunction with the `min_barcode_penalty_dist` parameter. |
| min_barcode_penalty_dist | The minimum penalty difference between top-2 barcodes required for classification. Used in conjunction with `max_barcode_penalty`. |
| min_separation_only_dist | The minimum penalty difference between the top-2 barcodes required for classification when the `max_barcode_penalty` is not met. |
| barcode_end_proximity | Proximity of the end of the barcode construct to the ends of the read required for classification. |
| flank_left_pad | Number of bases to use from preceding flank during barcode alignment. |
| flank_right_pad | Number of bases to use from succeeding flank during barcode alignment. |
| front_barcode_window | Number of bases at the front of the read within which to look for barcodes. |
| rear_barcode_window | Number of bases at the rear of the read within which to look for barcodes. |
| min_flank_score | Minimum score for the flank alignment. Score here is 1.f - (edit distance) / flank_length |
| midstrand_flank_score | Minimum score for a flank alignment that is not at read ends to be considered as a mid-strand barcode. Score here is 1.f - (edit distance) / flank_length |

For `flank_left_pad` and `flank_right_pad`, something in the range of 5-10 bases is typically good.
Note that errors from this padding region are also part of the barcode alignment penalty.
Therefore a bigger padding region may require a higher `max_barcode_penalty` for classification.

## Sequences file

In addition to specifying a custom barcode arrangement, new barcode sequences can also be specified
in a FASTQ format.

There are 2 requirements:

1. The sequence names must follow the `prefix%\d+i` format (e.g. `BC%02i` for barcodes needing 2
digit indexing, or `NB%04i` for barcodes with 4 digit indexing, etc.).
2. All barcode sequence lengths must match.

This is an example sequences file.

```text
>BC01
TTTT
>BC02
AAAA
>BC03
GGGG
>BC04
CCCC
```
