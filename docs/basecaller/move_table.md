# Move Table

The move table is a record of the model's base emissions in strided signal space and
gives a coarse sequence-to-signal mapping.

It can be added to SAM/BAM outputs by setting the `--emit-moves` flag.

## Move Table Metadata Format

The format of the move table metadata SAM/BAM tag is as follows:

```text
mv:B:c,[block_stride],[signal_block_move_list]
```

`block_stride`: An `int8_t` containing the number of source signal samples which each
element in the `signal_block_move_list` corresponds to.
This will be set to the input **stride** of the model.

`signal_block_move_list`: A comma separated list of `int8_t` samples, each one containing a single move
table element (unless overflow has occurred, see implementation details below).
Each element corresponds to `block_stride` samples of the raw source signal.

The move table entries will be stored in order in successive `int8_t`s of the `signal_block_move_list`.

For example:

```text
Stride     : 5
Move Table : 0,0,1,0,1
SAM Tag    : mv:B:c,5,0,0,1,0,1
```

??? Info "Implementation Details"

    As the meta data is signed, each individual element supports values in the range -128 to 127.
    In order to be able to store values outside this range, if a single element in the
    metadata has the value -128 or 127, then the next entry in the metadata should be
    added to the current one, in order to reconstruct the original value.

    For example:

    ```text
    Stride     : 5
    Move Table : -400,200
    SAM Tag    : mv:B:c,5,0,-128,-128,-128,-16,127,73
    ```

    Note that the exact value -128 or 127 (or multiples thereof) requires a trailing zero
    for the format to be encoded correctly.

    For example:

    ```text
    Stride     :5
    Move Table : -128,127,-256,254
    SAM Tag    : mv:B:c,5,0,-128,0,127,0,-128,-128,0,127,127,0
    ```

### Example

Given the above example move table: `mv:B:c,5,0,0,1,0,1`

The block stride is `5` (the first value) and the remaining values `0,0,1,0,1` state that
the emitted bases occurred in the 3rd and 5th strided blocks.

Converting strided blocks into signal space (`[0-4,5-9,10-14,15-19,20-24]`) we can state that these bases were emitted
from the 10th-14th and 20th-24th signal samples respectively.
