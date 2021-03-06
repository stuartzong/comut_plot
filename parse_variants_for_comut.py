#! /usr/bin/env python

import os, stat, os.path, time, datetime, subprocess
import re, sys, glob, argparse, csv, shutil, fileinput
from collections import defaultdict
from pprint import pprint
from itertools import islice
import ConfigParser

def __main__():
    print "script starts at: %s\n" % datetime.datetime.now()     
    parser = argparse.ArgumentParser(description='Reformat filtered summary for comut plot!')
    parser.add_argument('-i','--input_file', help='specify input file', required=True)
    args = vars(parser.parse_args())
    variant_summary = args['input_file']

    gene_list = "ordered_genes.txt"
    patient_list = "HIV_Cervical_patients.txt"
    # variant_input_file = "bam_vcf_cnv_path.txt" 
    comut_summary = ".".join([variant_summary, "comut" ])

    genes = make_list(gene_list)
    patients = make_list(patient_list)

    format_variants(variant_summary, comut_summary, genes, patients)


def make_list(infile):
    print "infile is: ", infile
    items = []
    with open(infile, 'r') as fh:
        for line in fh:
            item = line.split()[0]
            items.append(item)
        #items = list(set(items))
        print items
    return items

def format_variants(variant_summary, comut_summary, genes, patients):

    """ d = gene_variant_patients dictionary """
    d = dict()
    with open (comut_summary,  'wb') as fh:
            headers = ['gene', 'sample', 'mutations']
            writer = csv.writer( fh, delimiter='\t' )
            writer.writerow(headers)
            print "The variant summary file is: %s.\n" % variant_summary
            with open (variant_summary, 'r') as handle:
                 records = csv.DictReader(handle,  delimiter='\t')
                 headers = records.fieldnames
                 for line in records:
                     gene = line['gene']
                     chr = line["chromosome"]
                     pos = line["position"]
                     ref = line["ref_base"]
                     alt = line["alt_base"]
                     patient = line["patient_ID"].split('_')[0]
                     # fix:some snpeff noted as lowercase, which gives trouble for comut plot
                     mutation= re.split('\(|', line["snpeff_details"])[0].upper()
                     # be aware that there are annotations as 
                     # MISSENSE_VARIANT+SPLICE_REGION_VARIANT
                     # SPLICE_ACCEPTOR_VARIANT+INTRON_VARIANT
                     if "+" in mutation:
                         print "xxxxxxxx", mutation


                     try:
                         d[gene][patient].append(mutation)
                     except KeyError:
                         if gene not in d:
                             d[gene] = {}
                         if patient not in d[gene]:
                             d[gene][patient] = [mutation]
            #for gene in d:
            #    if (gene in genes):
            for gene in genes:
                if gene in d: 
                    if (len(d[gene]) > 0):
                        for patient in patients:
                            #for patient in d[gene]:
                            if (patient in d[gene]):
                                mut = list(set(d[gene][patient]))
                                if (int(len(mut)) > 1):
                                    mutation = "Multiple"
                                else:
                                    mutation = mut[0]
                            else:
                                mutation = "NA"
                                mut = ["NA"]
                            print gene, "\t",patient, "\t", mutation,"\t", len(mut)
                            writer.writerow([gene, patient, mutation])

if __name__ == '__main__':
    __main__()

