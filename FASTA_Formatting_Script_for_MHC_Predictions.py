#!/usr/bin/env python3

import csv
import argparse
import math
import sys

def process_data(version, rawfiles, cut_off):
    cut_off = float(cut_off)  # Ensure cut_off is treated as a float
    if version == '4.0':
        bad_words = ['high binders', 'iCore', '----', '#']
    elif version == 'pan':
        bad_words = ['Pos', 'HLA', 'Peptide', 'Core', 'Icore', 'Identity', 'Score', '%Rank', 'BindLevel', '#', 'training data', 'ICore', 'high binders', '------', 'Command', 'NetMHCpan', 'Rank', '---']
    elif version == '3.4':
        bad_words = ['binder threshold', 'Artificial Neural', 'affinity(nM)', '--------', 
                     'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    rawfile_list = []
    for rawfile in rawfiles:
        rawfile_list.extend(rawfile.replace('\n', ' ').split())
    
    #print(rawfile_list) 
    formatted_files = []  # List to store output file names
    
    for filename in rawfile_list:
        newname = filename.replace("output", "data")
        print(f"Processing file: {filename}", file=sys.stderr)
        formatted_files.append(newname)  # Add the new file name to the list

        with open(filename) as oldfile, open(newname, 'w') as newfile:
            for line in oldfile:
                if not any(bad_word in line for bad_word in bad_words):
                    if line.strip():
                        newline = line.split()
                        try:
                            if version == '3.4':
                                if float(newline[3]) < cut_off:
                                    if cut_off < 500:
                                        newfile.write(f">>{newline[5]}_{newline[3]}_{newline[6]}\n{newline[1]}\n")
                                    else:
                                        newfile.write(f">>{newline[4]}_{newline[3]}_{newline[5]}\n{newline[1]}\n")
                            else:
                                if len(newline) > 11 and float(newline[11]) < cut_off:
                                    newfile.write(f">>{newline[10]}|Score:{newline[11]}|Allele:{newline[1]}\n{newline[2]}\n")
                                else:
                                    print(f"Skipping line due to insufficient data: {newline}", file=sys.stderr)
                        except ValueError as e:
                            print(f"Error processing line due to value conversion issue: {e}", file=sys.stderr)
    
    print("\nnetMHC to fasta conversion complete", file=sys.stderr)
    print(" ".join(formatted_files))
    return formatted_files  # Return the list of formatted files

if __name__ == "__main__":
    # Argument parser
    parser = argparse.ArgumentParser(description='Process netMHC data.')
    parser.add_argument('--version', type=str, help='netMHC version (e.g., 3.4, 4.0, pan)')
    parser.add_argument('--rawfiles', nargs='+', help='List of input files to process')
    parser.add_argument('--cutoff', type=float, help='Affinity cutoff for processing')
    
    args = parser.parse_args()

    # Call the processing function with arguments
    formatted_files = process_data(args.version, args.rawfiles, args.cutoff)
