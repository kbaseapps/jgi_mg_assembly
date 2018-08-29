/*
A KBase module: jgi_mg_assembly

*/

module jgi_mg_assembly {
    /*
    A boolean - 0 for false, 1 for true.
        @range (0, 1)
    */
    typedef int boolean;
    typedef string assembly_upa;

    /* Should be only Paired-end reads. */
    typedef string reads_upa;

    /* Used for the alignment output. */
    typedef string alignment_upa;

    /*
    Inputs for the Assembly pipeline.
    reads_upa:
        UPA for the input reads object. This should be a Paired-End Illumina reads file.
    workspace_name:
        name of the workspace to upload to at the end.
    output_assembly_name:
        name of the output assembly file.
    skip_rqcfilter:
        If 1, skip the RQCFilter step of the pipeline. If 0, run it. (default = 0)
    cleaned_reads_name (optional):
        If not empty, this will cause the finalized, cleaned/filtered reads to be uploaded as a new
        reads object with this name. This'll be an interleaved paired-end reads object.
    filtered_reads_name (optional, unless alignment_name is present):
        If not empty, this will cause the RQCFiltered reads to be uploaded as a new reads object. These
        are the reads aligned to the final assembly, so these are needed to associate with the
        final alignment if that alignment is to be kept.
    alignment_name (optional):
        If not empty, this will save and upload the BBMap-generated BAM file that aligns the original
        filtered, but uncleaned reads to the constructed assembly.
    debug (hidden option):
        If 1, run in debug mode. A little more verbose, and trims some parameters from various steps
        so it can run locally(ish). You probably don't want to do this in production, it's meant for
        testing.
    */
    typedef structure {
        reads_upa reads_upa;
        string workspace_name;
        string output_assembly_name;
        string cleaned_reads_name;
        string filtered_reads_name;
        string alignment_name;
        boolean skip_rqcfilter;
        boolean debug;
    } AssemblyPipelineParams;

    /*
    Outputs from the Assembly pipeline.
    report_name:
        The name of the generated report object.
    report_ref:
        The UPA for the generated report object.
    assembly_upa:
        The UPA for the newly made assembly object.
    cleaned_reads_upa (optional):
        The UPA for the finalized, cleaned reads that are assembled in the pipeline, if requested by the input.
    filtered_reads_upa (optional):
        The UPA for the RQCFiltered reads, if requested by the input, AND skip_rqcfilter is not true.
    alignment_upa (optional):
        The UPA for the uploaded alignment object, if requested by the input.
    */
    typedef structure {
        string report_name;
        string report_ref;
        assembly_upa assembly_upa;
        reads_upa cleaned_reads_upa;
        reads_upa filtered_reads_upa;
        alignment_upa alignment_upa;
    } AssemblyPipelineResults;

    funcdef run_mg_assembly_pipeline(AssemblyPipelineParams params)
        returns (AssemblyPipelineResults results) authentication required;
};
