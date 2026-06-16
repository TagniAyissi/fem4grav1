import os
import shutil

configfile: "config.yaml"

DATA_FILE = config.get("data_file", "data/Flegrei.txt")
IROW = config.get("irow", 75)
ICOL = config.get("icol", 101)
METHOD = config.get("method", "cubic")
OUTPUT_NPZ = config.get("output_npz", "results/flegrei.npz")
OUTPUT_TXT = config.get("output_txt", "results/flegrei_table.txt")
PLOT_FILE = config.get("plot_file", "images/flegrei_maps.png")


rule all:
    input:
        OUTPUT_NPZ,
        OUTPUT_TXT,
        PLOT_FILE,


rule run_fem:
    input:
        DATA_FILE
    output:
        npz=OUTPUT_NPZ,
        table=OUTPUT_TXT,
        plot=PLOT_FILE,
    params:
        irow=IROW,
        icol=ICOL,
        method=METHOD,
    shell:
        """
        python -m fem4grav {input} \
            --irow {params.irow} \
            --icol {params.icol} \
            --method {params.method} \
            --output {output.npz} \
            --table {output.table} \
            --save-plot {output.plot} \
            --no-plot
        """


rule clean:
    run:
        # Remove the entire "results" directory if it exists
        if os.path.exists("results"):
            shutil.rmtree("results")
        
        # Specifically remove the generated images
        files_to_remove = [
            "images/flegrei_maps.png",
            "images/bouguer.png", 
            "images/regional.png", 
            "images/residual.png"
        ]
        
        for f in files_to_remove:
            if os.path.exists(f):
                os.remove(f)