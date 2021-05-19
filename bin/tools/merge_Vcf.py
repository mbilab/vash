#!/usr/bin/env python
import argparse
import logging
import subprocess
import time


def get_args():
    """
    Get the args and/or show the help message.
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description="""Merge vcf files. Dependency: bcftools.""")
    parser.add_argument('Input', help='The file list with one sample per-line')
    parser.add_argument('-b', metavar="batch", help='Number of files to be merged at one time. ', type=int, default=16)
    parser.add_argument('-t', metavar="threads", help='Threads to use for bcftools.', type=int, default=1)
    parser.add_argument('-p', metavar='prefix',
                        help='The output prefix string of outfile, e.g. given "Sample1", the output file will be Sample1.run_number.vcf.gz',
                        type=str, default="output")
    parser.add_argument('-v', '--verbose', action='store_true', help="Display info.")

    args = parser.parse_args()
    return args


def get_files(in_files):
    vcf_list = []
    with open(in_files, 'r') as fh:
        for line in fh:
            vcf_list.append(line.rstrip())
    return vcf_list


def merge_vcf(in_list, batch_number, threads, out_prefix):
    logging.debug("Number of input files: %d, Batch size %d, Threads to use: %d",
                  len(in_list), batch_number, threads)
    current = 1
    for i in range(0, len(in_list), batch_number):
        outfile_name = str(out_prefix) + "." + str(i+1) + ".vcf.gz"
        logging.info("Stage %d, merge %d files start from line %d to %s", current, batch_number, i+1, outfile_name)

        start_time = time.time()

        # command_merge = str("bcftools merge --threads " + str(threads)  + " --merge all "
        #                     + " ".join(str(f) for f in in_list[i:i+batch_number]) + " -O z -o "
        #                     + outfile_name)

        command_merge = ["bcftools", "merge", "--threads", str(threads) , "--merge", "all"]
        command_merge.extend(in_list[i:i+batch_number])
        command_merge.extend(["-O", "z", "-o", outfile_name])

        logging.info("Command: %s", command_merge)
        #subprocess.call(command_merge, shell=True)
        subprocess.call(command_merge)

        logging.info("Indexing file: %s", outfile_name)

        command_index = str("bcftools index --tbi --thread " + str(threads) +" "+ outfile_name)
        logging.info("Command: %s", command_index)
        subprocess.call(command_index, shell=True)

        end_time = time.time()
        logging.info("Running time: %d\n", end_time - start_time)
        current += 1
    return


def main():
    args = get_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG,
                            format='[%(asctime)s][%(levelname)s]: %(message)s')
    else:
        logging.basicConfig(level=logging.WARNING,
                            format='[%(asctime)s][%(levelname)s]: %(message)s')

    list_a = get_files(args.Input)
    merge_vcf(list_a, args.b, args.t, args.p)



if __name__ == '__main__':
    main()

