/*
A KBase module: jgi_mg_assembly

*/

module jgi_mg_assembly {
    typedef string assembly_upa;

    /* Should be only Paired-end reads. */
    typedef string reads_upa;

    typedef structure {
        reads_upa reads_upa;
        string workspace_name;
        string output_assembly_name;
    } AssemblyPipelineParams;

    typedef structure {
        string report_name;
        string report_ref;
        assembly_upa assembly_output;
    } AssemblyPipelineResults;

    funcdef run_mg_assembly_pipeline(AssemblyPipelineParams params)
        returns (AssemblyPipelineResults results) authentication required;
};
