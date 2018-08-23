
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
 * <p>Original spec-file type: AssemblyPipelineResults</p>
 * <pre>
 * Outputs from the Assembly pipeline.
 * report_name:
 *     The name of the generated report object.
 * report_ref:
 *     The UPA for the generated report object.
 * assembly_output:
 *     The UPA for the newly made assembly object.
 * cleaned_reads_output (optional):
 *     The UPA for the finalized, cleaned reads that are assembled in the pipeline, if requested by the input.
 * alignment_output (optional):
 *     The UPA for the uploaded alignment object, if requested by the input.
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "report_name",
    "report_ref",
    "assembly_output",
    "cleaned_reads_output",
    "alignment_output"
})
public class AssemblyPipelineResults {

    @JsonProperty("report_name")
    private String reportName;
    @JsonProperty("report_ref")
    private String reportRef;
    @JsonProperty("assembly_output")
    private String assemblyOutput;
    @JsonProperty("cleaned_reads_output")
    private String cleanedReadsOutput;
    @JsonProperty("alignment_output")
    private String alignmentOutput;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("report_name")
    public String getReportName() {
        return reportName;
    }

    @JsonProperty("report_name")
    public void setReportName(String reportName) {
        this.reportName = reportName;
    }

    public AssemblyPipelineResults withReportName(String reportName) {
        this.reportName = reportName;
        return this;
    }

    @JsonProperty("report_ref")
    public String getReportRef() {
        return reportRef;
    }

    @JsonProperty("report_ref")
    public void setReportRef(String reportRef) {
        this.reportRef = reportRef;
    }

    public AssemblyPipelineResults withReportRef(String reportRef) {
        this.reportRef = reportRef;
        return this;
    }

    @JsonProperty("assembly_output")
    public String getAssemblyOutput() {
        return assemblyOutput;
    }

    @JsonProperty("assembly_output")
    public void setAssemblyOutput(String assemblyOutput) {
        this.assemblyOutput = assemblyOutput;
    }

    public AssemblyPipelineResults withAssemblyOutput(String assemblyOutput) {
        this.assemblyOutput = assemblyOutput;
        return this;
    }

    @JsonProperty("cleaned_reads_output")
    public String getCleanedReadsOutput() {
        return cleanedReadsOutput;
    }

    @JsonProperty("cleaned_reads_output")
    public void setCleanedReadsOutput(String cleanedReadsOutput) {
        this.cleanedReadsOutput = cleanedReadsOutput;
    }

    public AssemblyPipelineResults withCleanedReadsOutput(String cleanedReadsOutput) {
        this.cleanedReadsOutput = cleanedReadsOutput;
        return this;
    }

    @JsonProperty("alignment_output")
    public String getAlignmentOutput() {
        return alignmentOutput;
    }

    @JsonProperty("alignment_output")
    public void setAlignmentOutput(String alignmentOutput) {
        this.alignmentOutput = alignmentOutput;
    }

    public AssemblyPipelineResults withAlignmentOutput(String alignmentOutput) {
        this.alignmentOutput = alignmentOutput;
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
        return ((((((((((((("AssemblyPipelineResults"+" [reportName=")+ reportName)+", reportRef=")+ reportRef)+", assemblyOutput=")+ assemblyOutput)+", cleanedReadsOutput=")+ cleanedReadsOutput)+", alignmentOutput=")+ alignmentOutput)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
