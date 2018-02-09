
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
 * 
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "reads_ref",
    "workspace_name",
    "assembly_name"
})
public class AssemblyPipelineParams {

    @JsonProperty("reads_ref")
    private String readsRef;
    @JsonProperty("workspace_name")
    private String workspaceName;
    @JsonProperty("assembly_name")
    private String assemblyName;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("reads_ref")
    public String getReadsRef() {
        return readsRef;
    }

    @JsonProperty("reads_ref")
    public void setReadsRef(String readsRef) {
        this.readsRef = readsRef;
    }

    public AssemblyPipelineParams withReadsRef(String readsRef) {
        this.readsRef = readsRef;
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

    @JsonProperty("assembly_name")
    public String getAssemblyName() {
        return assemblyName;
    }

    @JsonProperty("assembly_name")
    public void setAssemblyName(String assemblyName) {
        this.assemblyName = assemblyName;
    }

    public AssemblyPipelineParams withAssemblyName(String assemblyName) {
        this.assemblyName = assemblyName;
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
        return ((((((((("AssemblyPipelineParams"+" [readsRef=")+ readsRef)+", workspaceName=")+ workspaceName)+", assemblyName=")+ assemblyName)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
