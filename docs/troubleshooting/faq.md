
# Frequently Asked Questions

Below are some of our most frequently asked technical and support questions.
Please check back regularly if you have an issue as this will be updated often.

If you have a question that is not answered below please raise a new issue on the
[Dorado GitHub issues](https://github.com/nanoporetech/dorado/issues) page providing as
much information as possible and the Dorado team will aim to respond promptly.

## Basecaller

### Models

#### Which model should I use?

Since Dorado 0.5.0 the [automatic model selection]({{find("complex")}})
algorithm should be able to select the appropriate model for the input data (POD5 only)
given a model speed (e.g. `fast, hac, sup`). Dorado will automatically download missing models.

In general, the **latest** basecalling models will be the most performant and most accurate as
there are continuous advances in model architecture and training.

For more details see [Models Introduction]({{find("models")}}) and the [Models List]({{find("list")}})

##### I have R10.4 data

Dorado doesn't support basecalling models for the R10.4 condition. Please use the legacy Guppy basecaller.

---

#### Where are the new models?

New Dorado releases incrementally support new models which are generally not backwards compatible
with previous versions.
If you can see a model in the [Models List]({{find("list")}}) but you cannot download it
please ensure you have the **latest release of dorado** which you can find instruction on
how to download and install it [here]({{find("index")}}#installation)

---

### Outputs

#### Why do I have more records than reads?

Dorado reports the number of reads *basecalled* from your input data, but this number may differ
from the number of records in your output because of read splitting. This can happen because a
single read recorded to the POD5 file contains more than one molecule and this was not detected
and split into separate records during sequencing by MinKnow.

Dorado annotates split reads by adding the `parent_read_id` which is stored in the bam `pi` tag.
The `parent_read_id` is the read id of the original unsplit read. Only reads which are children of
unsplit reads have this `pi` tag.

We can count all bam records which are split reads using this command:

```bash
samtools view <BAM> --expr '[pi] && [dx]!=1' | wc -l
```

!!! NOTE inline end

    Unsplit reads may contain an arbitrary number of reads not just 2 as shown in this example.

Here, we also include `[dx]!=1` for completeness in case the data was duplex basecalled.
For more information on the `dx` tag please see the [duplex documentation]({{find("duplex")}}#duplex-sequence-metadata).

If your output had 1 additional record, the above command would report 2 as an unsplit read
will be written as 2 new records with unique `read_id`s and sharing the same `parent_read_id`.

---
