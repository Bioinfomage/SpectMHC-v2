"""
This script splits a FASTA file into a specified number of smaller parts for processing.
Splits the file into a specified number of chunks (num_chunks)
"""

import argparse
import math

def chunks(lst, num_chunks):
    """Divide a list `lst` into `num_chunks` approximately equal parts."""
    avg_chunk_size = math.ceil(len(lst) / num_chunks)
    return [lst[i:i + avg_chunk_size] for i in range(0, len(lst), avg_chunk_size)]

def new_string(x):
    """Convert a list of strings into a single string separated by '>' characters."""
    temp = ">"
    for i in x:
        temp = temp + i + ">"
    return temp[:-1]  # Remove the last '>' to avoid empty entry

def mkfile(content, i, filename):
    """Write content to a file and return the file name."""
    split_filename = f"split{i}_{filename.split('.')[0]}"
    with open(split_filename, "w") as f:
        f.write(content)
    return split_filename

def split_files(filename, number_of_chunks):
    """Split the input FASTA file into the specified number of chunks and write each chunk to a new file."""
    split_list = []

    with open(filename, "r") as f:
        splitted_file = f.read().split(">")

    # Remove any empty elements from the split
    splitted_file = list(filter(None, splitted_file))

    # Split the file contents into the specified number of chunks
    new_files = chunks(splitted_file, number_of_chunks)

    for count, i in enumerate(new_files, start=1):
        q = new_string(i)
        if count == 1:
            q = q[1:]  # Remove the leading '>' from the first chunk
        split_filename = mkfile(q, count, filename)
        split_list.append(split_filename)

    return split_list
    

if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Split a FASTA file into a specified number of chunks.")
    parser.add_argument("--fname", type=str, required=True, help="The input FASTA file.")
    parser.add_argument("--num_chunks", type=int, required=True, help="Number of chunks to split the file into.")

    # Parse the arguments
    args = parser.parse_args()

    # Call the split_files function with parsed arguments
    split_list = split_files(args.fname, args.num_chunks)

    # Print split file names (for shell script capture)
    print(" ".join(split_list))

