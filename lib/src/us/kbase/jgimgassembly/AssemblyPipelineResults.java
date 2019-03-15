
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
 * assembly_upa:
 *     The UPA for the newly made assembly object.
 * cleaned_reads_upa (optional):
 *     The UPA for the finalized, cleaned reads that are assembled in the pipeline, if requested by the input.
 * filtered_reads_upa (optional):
 *     The UPA for the RQCFiltered reads, if requested by the input, AND skip_rqcfilter is not true.
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "report_name",
    "report_ref",
    "assembly_upa",
    "cleaned_reads_upa",
    "filtered_reads_upa"
})
public class AssemblyPipelineResults {

    @JsonProperty("report_name")
    private String reportName;
    @JsonProperty("report_ref")
    private String reportRef;
    @JsonProperty("assembly_upa")
    private String assemblyUpa;
    @JsonProperty("cleaned_reads_upa")
    private String cleanedReadsUpa;
    @JsonProperty("filtered_reads_upa")
    private String filteredReadsUpa;
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

    @JsonProperty("assembly_upa")
    public String getAssemblyUpa() {
        return assemblyUpa;
    }

    @JsonProperty("assembly_upa")
    public void setAssemblyUpa(String assemblyUpa) {
        this.assemblyUpa = assemblyUpa;
    }

    public AssemblyPipelineResults withAssemblyUpa(String assemblyUpa) {
        this.assemblyUpa = assemblyUpa;
        return this;
    }

    @JsonProperty("cleaned_reads_upa")
    public String getCleanedReadsUpa() {
        return cleanedReadsUpa;
    }

    @JsonProperty("cleaned_reads_upa")
    public void setCleanedReadsUpa(String cleanedReadsUpa) {
        this.cleanedReadsUpa = cleanedReadsUpa;
    }

    public AssemblyPipelineResults withCleanedReadsUpa(String cleanedReadsUpa) {
        this.cleanedReadsUpa = cleanedReadsUpa;
        return this;
    }

    @JsonProperty("filtered_reads_upa")
    public String getFilteredReadsUpa() {
        return filteredReadsUpa;
    }

    @JsonProperty("filtered_reads_upa")
    public void setFilteredReadsUpa(String filteredReadsUpa) {
        this.filteredReadsUpa = filteredReadsUpa;
    }

    public AssemblyPipelineResults withFilteredReadsUpa(String filteredReadsUpa) {
        this.filteredReadsUpa = filteredReadsUpa;
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
        return ((((((((((((("AssemblyPipelineResults"+" [reportName=")+ reportName)+", reportRef=")+ reportRef)+", assemblyUpa=")+ assemblyUpa)+", cleanedReadsUpa=")+ cleanedReadsUpa)+", filteredReadsUpa=")+ filteredReadsUpa)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
