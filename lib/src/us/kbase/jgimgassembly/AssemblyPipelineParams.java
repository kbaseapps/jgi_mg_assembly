
package us.kbase.jgimgassembly;

import java.util.HashMap;
import java.util.Map;
import javax.annotation.Generated;
import com.fasterxml.jackson.annotation.JsonAnyGetter;
import com.fasterxml.jackson.annotation.JsonAnySetter;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;


/**
 * <p>Original spec-file type: AssemblyPipelineParams</p>
 * <pre>
 * Inputs for the Assembly pipeline.
 * reads_upa:
 *     UPA for the input reads object. This should be a Paired-End Illumina reads file.
 * workspace_name:
 *     name of the workspace to upload to at the end.
 * output_assembly_name:
 *     name of the output assembly file.
 * skip_rqcfilter:
 *     If 1, skip the RQCFilter step of the pipeline. If 0, run it. (default = 0)
 * cleaned_reads_name (optional):
 *     If not empty, this will cause the finalized, cleaned/filtered reads to be uploaded as a new
 *     reads object with this name. This'll be an interleaved paired-end reads object.
 * alignment_name (optional):
 *     If not empty, this will save and upload the BBMap-generated BAM file that aligns the original
 *     filtered, but uncleaned reads to the constructed assembly.
 * debug (hidden option):
 *     If 1, run in debug mode. A little more verbose, and trims some parameters from various steps
 *     so it can run locally(ish). You probably don't want to do this in production, it's meant for
 *     testing.
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "reads_upa",
    "workspace_name",
    "output_assembly_name",
    "skip_rqcfilter",
    "debug"
})
public class AssemblyPipelineParams {

    @JsonProperty("reads_upa")
    private String readsUpa;
    @JsonProperty("workspace_name")
    private String workspaceName;
    @JsonProperty("output_assembly_name")
    private String outputAssemblyName;
    @JsonProperty("skip_rqcfilter")
    private Long skipRqcfilter;
    @JsonProperty("debug")
    private Long debug;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("reads_upa")
    public String getReadsUpa() {
        return readsUpa;
    }

    @JsonProperty("reads_upa")
    public void setReadsUpa(String readsUpa) {
        this.readsUpa = readsUpa;
    }

    public AssemblyPipelineParams withReadsUpa(String readsUpa) {
        this.readsUpa = readsUpa;
        return this;
    }

    @JsonProperty("workspace_name")
    public String getWorkspaceName() {
        return workspaceName;
    }

    @JsonProperty("workspace_name")
    public void setWorkspaceName(String workspaceName) {
        this.workspaceName = workspaceName;
    }

    public AssemblyPipelineParams withWorkspaceName(String workspaceName) {
        this.workspaceName = workspaceName;
        return this;
    }

    @JsonProperty("output_assembly_name")
    public String getOutputAssemblyName() {
        return outputAssemblyName;
    }

    @JsonProperty("output_assembly_name")
    public void setOutputAssemblyName(String outputAssemblyName) {
        this.outputAssemblyName = outputAssemblyName;
    }

    public AssemblyPipelineParams withOutputAssemblyName(String outputAssemblyName) {
        this.outputAssemblyName = outputAssemblyName;
        return this;
    }

    @JsonProperty("skip_rqcfilter")
    public Long getSkipRqcfilter() {
        return skipRqcfilter;
    }

    @JsonProperty("skip_rqcfilter")
    public void setSkipRqcfilter(Long skipRqcfilter) {
        this.skipRqcfilter = skipRqcfilter;
    }

    public AssemblyPipelineParams withSkipRqcfilter(Long skipRqcfilter) {
        this.skipRqcfilter = skipRqcfilter;
        return this;
    }

    @JsonProperty("debug")
    public Long getDebug() {
        return debug;
    }

    @JsonProperty("debug")
    public void setDebug(Long debug) {
        this.debug = debug;
    }

    public AssemblyPipelineParams withDebug(Long debug) {
        this.debug = debug;
        return this;
    }

    @JsonAnyGetter
    public Map<String, Object> getAdditionalProperties() {
        return this.additionalProperties;
    }

    @JsonAnySetter
    public void setAdditionalProperties(String name, Object value) {
        this.additionalProperties.put(name, value);
    }

    @Override
    public String toString() {
        return ((((((((((((("AssemblyPipelineParams"+" [readsUpa=")+ readsUpa)+", workspaceName=")+ workspaceName)+", outputAssemblyName=")+ outputAssemblyName)+", skipRqcfilter=")+ skipRqcfilter)+", debug=")+ debug)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
