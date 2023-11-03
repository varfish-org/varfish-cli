.. _main-cases_import:

===========
Case Import
===========

-------------------------
Phenopacket Bootstrapping
-------------------------

.. note::
    Currently, only PED and VCF files are supported for bootstrapping phenopackets.`a`

You must have loaded the project configuration via ``projects project-retrieve`` so the client knows the location/server and credentials of the raw data.

The ``cases-import bootstrap-phenopackets`` will then go over each file, incorporate it into the phenopackets file, and write out the phenopackets YAML.

The other files are handled as follows.
All absolute paths are assumed to be on the local file system whereas relative paths are assumed to be relative to the project import data store.
Note that these absolute paths are also written to the phenopackets YAML file and this will not work in the import.

``*.ped``
    PED/Pedigree file, used to derive sample information from.
    You can specify at most one PED file and it will overwrite existing pedigree information.

``*.bam``, ``*.bam.bai``
    The header of sequence alignment files will be read and the sample name is used to match it to the pedigree.
    Note that the samples in the BAM file and the PED file must match.
    BAM files must be indexed.

``*.vcf.gz``, ``*.vcf.gz.tbi``
    The header of variant call files will be read as well as the first ten records.
    This will be used to differentiate between sequence and structural variant files.
    You can currently only give at most one sequence variant file but any number of structural variant files.
    VCF files must be indexed.

``$FILE.md5``
    Assumed to be the MD5 checksum file of ``$FILE`` and stored as checksum attribute for it.

``*.csv``, ``*.txt``, ...
    Information related to quality control from pipelines.
    The command will try to detect the file types and register them into the phenopackets YAML file appropriately.

The ``--target-region`` argument can be given multiple time and specify the target regions of the used sequencing kit.
Supported target regions must be configured on the server.
They are given as pseudo S3 URLs in the internal storage where the server administrator must configure them.

The following target regions are available by default (for ``$RELEASE`` being one of ``GRCh37`` or ``GRCh38``) on a VarFish server installation.

whole genome
    ``s3://varfish-server/seqmeta/target-regions/$RELEASE/whole-genome.bed.gz``

Agilent SureSelect Human All Exon V4
    ``s3://varfish-server/seqmeta/target-regions/$RELEASE/agilent-all-exon-v4.bed.gz``

Agilent SureSelect Human All Exon V5
    ``s3://varfish-server/seqmeta/target-regions/$RELEASE/agilent-all-exon-v5.bed.gz``

Agilent SureSelect Human All Exon V6
    ``s3://varfish-server/seqmeta/target-regions/$RELEASE/agilent-all-exon-v6.bed.gz``

Agilent SureSelect Human All Exon V7
    ``s3://varfish-server/seqmeta/target-regions/$RELEASE/agilent-all-exon-v7.bed.gz``

Agilent SureSelect Human All Exon V8
    ``s3://varfish-server/seqmeta/target-regions/$RELEASE/agilent-all-exon-v8.bed.gz``

IDT xGen Exome Research Panel v1
    ``s3://varfish-server/seqmeta/target-regions/$RELEASE/idt-xgen-exome-research-panel-v1.bed.gz``

IDT xGen Exome Research Panel v2
    ``s3://varfish-server/seqmeta/target-regions/$RELEASE/idt-xgen-exome-research-panel-v2.bed.gz``

Twist Comprehensive Exome
    ``s3://varfish-server/seqmeta/target-regions/$RELEASE/twist-comprehensive-exome.bed.gz``

Twist Core Exome
    ``s3://varfish-server/seqmeta/target-regions/$RELEASE/twist-core-exome.bed.gz``

Twist Exome V2.0
    ``s3://varfish-server/seqmeta/target-regions/$RELEASE/twist-exome-v2_0.bed.gz``

Twist RefSeq Exome
    ``s3://varfish-server/seqmeta/target-regions/$RELEASE/twist-refseq-exome.bed.gz``
