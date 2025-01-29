# Custom Adapter and Primer Sequences

Dorado will automatically detect and trim any adapter or primer sequences it finds.
The specific sequences it searches for depends on the specified sequencing kit.
Dorado `basecaller`, can get this information from read metadata in the input pod5.
Dorado `trim` however, requires that the sequencing kit is specified using the command-line option.

In some cases, it may be necessary to find and remove adapter and/or primer sequences that would
not normally be associated with the sequencing kit that was used, or you may be working with
older data for which the sequencing kit and/or primers being used are no longer directly
supported by Dorado (for example, anything prior to kit14). In such cases, you can specify a
custom adapter/primer file, using the command-line option `--primer-sequences`. If this option
is used, then the sequences encoded in the specified `--primer-sequences` file
will be used instead of the default sequences.

## Custom adapter/primer file format

The custom adapter/primer file uses the FASTA file format, where the desired adapter/primer sequences
are specified with additional metadata to define how each sequence should be used.

The following is an example adapter sequence:

```text
>LSK109_front type=adapter kits=SQK-PSK004,SQK-LSK109
AATGTACTTCGTTCAGTTACGTATTGCT
```

The syntax rules are as follows:

Record Name

:   The record name must be of the form `[id]_front` or `[id]_rear`.

    The `id` must be unique other than for the `_front` and `_rear` pair.

Type

:   Immediately following the record name must be a space, followed by either `type=adapter` or `type=primer`.

Kits (Optional)

:   Following the `type` designator, you can have an additional space, followed by `kits=[kit1],[kit2],[kit3],...`.

### How Dorado searches for adapters/primers

The `_front` and `_rear` record name suffixes and the `type` designator defines how Dorado will
search for the sequence.

For **adapters**:

:   Dorado will search for `front` sequence near the beginning of the read, and
for `rear` sequence near the end of the read.

For **primers**:

:   Dorado will search for the `front` sequence near the beginning of the read, and the reverse-complement of the
`rear` sequence near the end of the read. Dorado will also search for the `rear` sequence near the beginning of
the read, and for the reverse-complement of the `front` sequence near the end of the read.

The `kits` designator is optional. If provided, the sequence will only be searched for if
the sequencing-kit information in the read matches any of the kit names in the custom file.
If the `kits` designator is not provided, then the sequence will be searched for in all reads,
regardless of the kit that was used. If the `kit` is not present the sequence will be searched for
regardless of the read metadata in Dorado `basecaller` or sequencing kit selection in Dorado `trim`.

#### Example custom adapter/primer file

The following could be used to detect the `PCR_PSK_rev1` and `PCR_PSK_rev2` primers, along with
the `LSK109` adapters, for older data.

```text
>LSK109_front type=adapter
AATGTACTTCGTTCAGTTACGTATTGCT

>LSK109_rear type=adapter
AGCAATACGTAACTGAACGAAGT

>PCR_PSK_front type=primer
ACTTGCCTGTCGCTCTATCTTCGGCGTCTGCTTGGGTGTTTAACC

>PCR_PSK_rear type=primer
AGGTTAAACACCCAAGCAGACGCCGCAATATCAGCACCAACAGAAA
```

In this case, the above adapters and primers would be searched for in all reads, regardless of the
sequencing-kit information encoded in the read file, or in the case of dorado trim, regardless of the
sequencing-kit specified on the command-line.

To restrict the search to only primers in reads where `SQK-PSK004` specified as the kit name,
and adapters if reads were from either `SQK-PSK004` or `SQK-LSK109`, then the following could be used.

```text
>LSK109_front type=adapter kits=SQK-PSK004,SQK-LSK109
AATGTACTTCGTTCAGTTACGTATTGCT

>LSK109_rear type=adapter kits=SQK-PSK004,SQK-LSK109
AGCAATACGTAACTGAACGAAGT

>PCR_PSK_front type=primer kits=SQK-PSK004
ACTTGCCTGTCGCTCTATCTTCGGCGTCTGCTTGGGTGTTTAACC

>PCR_PSK_rear type=primer kits=SQK-PSK004
AGGTTAAACACCCAAGCAGACGCCGCAATATCAGCACCAACAGAAA
```
