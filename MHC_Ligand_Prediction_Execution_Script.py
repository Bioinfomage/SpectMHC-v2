
#!/usr/bin/env python3
import argparse
import os
import subprocess
import datetime
import sys

def executemhc(path, version, list_of_files, mhc, input_lengths):
    print(f"Execution started at {datetime.datetime.now()}", file=sys.stderr)
    out_list = []

    # Process each length and each file in the input list
    for length in input_lengths:
        for filename in list_of_files:
            head, sep, tail = filename.partition('.f')
            print(f"\nExecuting file {head} for length {length}", file=sys.stderr)
            
            # Generate output and error file names based on the input filename and peptide length
            outfile = f'{head}_{length}_output.txt'
            errfile = f'{head}_{length}_error.log'
            out_list.append(outfile)  # Store the output filename in the list

            # Construct the command for running netMHC based on the version
            if version == '4.0':
                command = f"{path}/netMHC -l {length} -a {mhc} {filename} > {outfile}"
            elif version == 'pan':
                command = f"{path}/netMHCpan -l {length} -a {mhc} -f {filename} > {outfile}"
            elif version == '3.4':
                command = f"{path}/netMHC -l {length} -a {mhc} {filename} > {outfile}"
            else:
                raise ValueError("Unsupported netMHC version provided.")

            # Run the command and redirect output to the appropriate files
            with open(outfile, 'w') as out, open(errfile, 'w') as err:
                subprocess.run(command, shell=True, stdout=out, stderr=err)

    print("\nnetMHC execution completed.", file=sys.stderr)
    return out_list  # Return the list of output files

if __name__ == "__main__":
    # Argument parsing
    parser = argparse.ArgumentParser(description="Execute netMHC predictions.")
    parser.add_argument('--path', type=str, required=True, help="Path to netMHC executable")
    parser.add_argument('--ver', type=str, required=True, help="Version of netMHC (e.g., '4.0', 'pan', '3.4')")
    parser.add_argument('--ifile', type=str, nargs='+', required=True, help="List of input file(s) for netMHC")
    parser.add_argument('--mhc', type=str, required=True, help="MHC allele")
    parser.add_argument('--length', type=str, required=True, help="Peptide length(s) (e.g., '8 9 10')")

    # Parse the arguments
    args = parser.parse_args()

    # Convert the peptide lengths from string to a list of integers
    input_lengths = [int(x) for x in args.length.split()]

    # Call the executemhc function with the list of input files
    output_files = executemhc(args.path, args.ver, args.ifile, args.mhc, input_lengths)

    # Print the list of output files (so it can be captured by a shell script)
    print("\n".join(output_files))
