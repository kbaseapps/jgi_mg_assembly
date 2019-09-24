from jgi_mg_assembly.pipeline_steps.step import Step
import os
from jgi_mg_assembly.utils.util import mkdir


AGP_FILE_TOOL = "/kb/module/bbmap/fungalrelease.sh"
class AgpRunner(Step):
    def __init__(self, scratch_dir, output_dir):
        super(AgpRunner, self).__init__("createAGPFile", "BBTools", AGP_FILE_TOOL, scratch_dir, output_dir, False)

    def run(self, spades_scaffolds, spades_contigs):
        """
        Runs bbmap/fungalrelease.sh to build AGP files and do some mapping and cleanup.
        Returns a dictionary where values are paths to files and keys are the following:
        scaffolds - mapped scaffolds fasta file
        contigs - mapped contigs fasta file
        agp - AGP file
        legend - legend for generated scaffolds
        """
        if spades_scaffolds is None or not os.path.exists(spades_scaffolds):
            err_str = "SPAdes did not generate a scaffolds file - expected to see {}".format(in_scaffolds)
            if not os.path.exists(spades_contigs):
                err_str = err_str + "\nSPAdes also did not produce a contigs file. This means that either SPAdes finished incorrectly, or your reads were unable to be assembled. Check the Job Status tab for SPAdes details."
            else:
                err_str = err_str + "\nThis might mean that your reads were unable to be assembled properly, or were over-filtered. Check the Job Status tab for details. The log segment before running SPAdes should show details about the corrected reads used in assembly."
            err_str = err_str + "\nUnable to continue running pipeline!"
            raise RuntimeError(err_str)
        agp_dir = os.path.join(self.output_dir, "createAGPfile")
        mkdir(agp_dir)
        out_scaffolds = os.path.join(agp_dir, "assembly.scaffolds.fasta")
        out_contigs = os.path.join(agp_dir, "assembly.contigs.fasta")
        out_agp = os.path.join(agp_dir, "assembly.agp")
        out_legend = os.path.join(agp_dir, "assembly.scaffolds.legend")
        agp_cmd_params = [
            "-Xmx40g",
            "in={}".format(spades_scaffolds),
            "out={}".format(out_scaffolds),
            "outc={}".format(out_contigs),
            "agp={}".format(out_agp),
            "legend={}".format(out_legend),
            "mincontig=200",
            "minscaf=200",
            "sortscaffolds=t",
            "sortcontigs=t",
            "overwrite=t"
        ]

        (exit_code, command) = super(AgpRunner, self).run(*agp_cmd_params)
        if exit_code != 0:
            raise RuntimeError("Error while cleaning scaffolds and creating AGP file!")

        return {
            "scaffolds_file": out_scaffolds,
            "contigs_file": out_contigs,
            "agp_file": out_agp,
            "legend_file": out_legend,
            "command": command,
            "version_string": self.version_string()
        }
