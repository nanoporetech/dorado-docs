# Sample Sheet

`dorado` can make use of a MinKNOW-compatible sample sheet containing data used to
identify a particular classification of read.

To apply a sample sheet, provide the path to the appropriate CSV file using the `--sample-sheet` argument:

```bash
dorado basecaller dna_r10.4.1_e8.2_400bps_hac@v4.2.0 reads/ \
    --kit-name SQK-16S114-24 \
    --sample-sheet <path_to_sample_sheet_csv> \
    > calls.bam
```

A sample sheet can also be applied to the `demux` command in the same way:

```bash
dorado demux calls.bam \
    --output-dir classified_reads \
    --kit-name SQK-16S114-24 \
    --sample-sheet <path_to_sample_sheet_csv>
```

`dorado` currently uses the sample sheet only for barcode filtering and aliasing,
so a `--kit-name` argument is **required**.

In the case of `demux`, the sample sheet must contain a 1-to-1 mapping of `barcode` identifiers
to `flow_cell_id`/`position_id` - i.e. all entries in the `barcode` column must be unique.

## Specification

### Sample Sheet Column headers

A sample sheet may only contain the column names below:

| Purpose   | Column Name              | Notes                             |
| --------- | ------------------------ | --------------------------------- |
| Standard  | `experiment_id`^[1]^     | Required^[3]^                     |
|           | `kit`                    | Required                          |
|           | `flow_cell_id`^[2]^      | Optional if `position_id` is set  |
|           | `position_id`^[2]^       | Optional if `flow_cell_id` is set |
|           | `protocol_run_id`        | Optional                          |
|           | `sample_id`              | Optional^[3]^                     |
|           | `flow_cell_product_code` | Optional                          |
| Barcoding | `alias`^[4]^             | Optional^[3]^                     |
|           | `type`                   | Optional                          |
|           | `barcode`^[5]^           | Optional                          |

1. All rows in a sample sheet must contain the same `experiment_id`.
2. At a minimum a sample sheet must contain `kit`, `experiment_id` and one of `position_id`
or `flow_cell_id`.
3. These fields must be a **maximum of 40 characters**, which must be either alphanumeric (`A-Z`, `a-z`, `0-9`), `_` or `-`.
4. See [Barcode aliasing](#barcode-aliasing)
5. See [Barcode filtering](#barcode-filtering)

For a full description of the format of the sample sheet, see
[the MinKNOW Sample Sheet documentation](https://community.nanoporetech.com/docs/prepare/library_prep_protocols/experiment-companion-minknow/v/mke_1013_v1_revcy_11apr2016/sample-sheet-upload).

!!! note

    `dorado` does not currently support dual barcodes.

## Barcode aliasing

If a sample sheet contains an `alias` column, this will be used to replace the `barcode`
identifier for reads matching the `flow_cell_id`/`position_id` and `experiment_id`.
This will be reflected in the read group ID `@RG ID` in the file header, and in the
`BC` and `RG` tags of the classified reads.

!!! note

    If both `flow_cell_id` and `position_id` are present, both must match the read data for an alias to be applied.
!!! warning

    Values in the `alias` column must not be valid barcode identifiers (e.g. `barcode##` or `unclassified`).

## Barcode filtering

If a sample sheet is present and barcoding is requested, `dorado` will only attempt to
find matches to the barcode identifiers listed in the `barcode` column (if present).
