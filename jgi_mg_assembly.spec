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
    debug (hidden option):
        If 1, run in debug mode. A little more verbose, and trims some parameters from various steps
        so it can run locally(ish). You probably don't want to do this in production, it's meant for
        testing.
    */
    typedef structure {
        reads_upa reads_upa;
        string workspace_name;
        string output_assembly_name;
        boolean skip_rqcfilter;
        boolean debug;
    } AssemblyPipelineParams;

    typedef structure {
        string report_name;
        string report_ref;
        assembly_upa assembly_output;
    } AssemblyPipelineResults;

    funcdef run_mg_assembly_pipeline(AssemblyPipelineParams params)
        returns (AssemblyPipelineResults results) authentication required;
};
