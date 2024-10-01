#!/bin/bash

# Script for predicting MHC ligands and generating a FASTA file for downstream mass spectrometry-based searches.
# Usage: ./script_name.sh [-r] [-s] <netMHC_folder> <MHC_version> <input_fasta> <binding_rank_cutoff> <allele> <length_of_peptides> <number_of_split_files>

# Options:
# -r  Save raw netMHC output
# -s  Split input file
# -h  Show help

# Initialize variables
save_raw_output=0
split_input_file=0

# Parse options using getopts
while getopts ":rsh" opt; do
    case "$opt" in
        r) save_raw_output=1 ;;  # Set flag to save raw output
        s) split_input_file=1 ;;  # Set flag to split input file
        h)
            echo ""
            echo "This script predicts MHC ligands and outputs a FASTA file for downstream mass spectrometry-based searches."
            echo "Please cite: MHC-I Ligand Discovery Using Targeted Database Searches of Mass Spectrometry Data: Implications for T-Cell Immunotherapies."
            echo "Usage: ./$(basename "$0") [-r] [-s] <netMHC_folder> <MHC_version> <input_fasta> <binding_rank_cutoff> <allele> <number_of_split_files>"
            echo ""
            echo "Options:"
            echo "  -r  Save raw netMHC output"
            echo "  -s  Split input file"
            echo "  -h  Show help"
            echo ""
            echo "Arguments:"
            echo "  netMHC_folder       Path to the NetMHC folder (e.g., /path/to/netMHC)"
            echo "  MHC_version         Version of netMHC (e.g., 3.4, 4.0, pan)"
            echo "  input_fasta         Input protein data in FASTA format (.fa/.fasta)"
            echo "  binding_rank_cutoff Cutoff to be used (e.g., 2)"
            echo "  allele              Allele to predict (e.g., H2-Kb)"
            echo "  peptide_lengths     Peptide length for prediction"
            echo "  number_of_split_files Number of split files (used with -s; determines the number of sequences per split file)"
            echo ""
            exit 0
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            exit 1
            ;;
    esac
done

shift $((OPTIND-1))  # Shift the arguments to parse positional ones

# Validate the number of parameters
if [ "$#" -lt 6 ] || [ "$#" -gt 7 ]; then
    echo "Usage: ./$(basename "$0") [-r] [-s] <netMHC_folder> <MHC_version> <input_fasta> <binding_rank_cutoff> <allele> <peptide_lengths> <number_of_split_files>"
    exit 1
fi

# Assign positional parameters to variables
netmhc_path=$1
mhc_version=$2
input_fasta=$3
binding_rank_cutoff=$4
mhc_allele=$5
peptide_lengths=$6
number_of_splits=${7:-1}  # Default to 1 if not provided

# Validate MHC version
echo -e "\nValidating MHC_version\n"
case "$mhc_version" in
    3.4|4.0|pan)
        echo "Using NetMHC version $mhc_version"
        ;;
    *)
        echo "Error: Unrecognized version. NetMHC version must be 3.4, 4.0, or pan."
        exit 1
        ;;
esac

# Split files if the option is selected
echo -e "\nSplitting option received and progressing\n"
if [ "$split_input_file" -eq 1 ]; then
    split_file_list=$(python split_file1.py \
    --fname "$input_fasta" \
    --num "$number_of_splits" )
    echo "Files in split_file_list: $split_file_list"
    if [ -z "$split_file_list" ]; then
        echo "Error: No files generated from split_file1.py"
        exit 1
    fi
else
    echo "Skipping file splitting"
    split_file_list="$input_fasta"
fi
# Execute netMHC using argparse in executemhc1.py
raw_output_files=$(python executemhc1.py \
    --path "$netmhc_path" \
    --ver "$mhc_version" \
    --ifile $split_file_list \
    --mhc "$mhc_allele" \
    --length "$peptide_lengths")
echo -e "\nFiles in raw_output_files: $raw_output_files"
if [ -z "$raw_output_files" ]; then
    echo "Error: No files generated from executemhc1.py"
    exit 1
fi

# Generate output in FASTA format using tofasta1.py
echo -e "\nFormatting FASTA in progress\n"
Formatted_files=$(python tofasta1.py \
    --version "$mhc_version" \
    --rawfiles "$raw_output_files" \
    --cutoff "$binding_rank_cutoff")
echo "Files in Formatted_files: $Formatted_files"
#if [ -z "$Formatted_files" ]; then
  # echo "Error: No files generated from tofasta1.py"
 #  exit 1
#fi
# Handle raw netMHC output
echo -e "\noutput handling in progress\n"
if [ "$save_raw_output" -eq 0 ]; then

    if [ -n "$split_file_list" ]; then
        python remove_raw_file1.py --rmfile $split_file_list
    else
        echo "No files to delete for split_file_list"
    fi

    if [ -n "$raw_output_files" ]; then
        python remove_raw_file1.py --rmfile $raw_output_files
    else
        echo "No files to delete for raw_output_files"
    fi
else
    if [ -n "$split_file_list" ]; then
        python remove_raw_file1.py --rmfile $split_file_list
    else
        echo "No files to delete for split_file_list"
    fi
fi

# Done
echo -e "\nExecution complete. The FASTA file is now available.\n"
