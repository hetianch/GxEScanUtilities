import gzip
import csv
import xlrd
import time

""" 
This script is used to extract the SNPs of Top100.xlsx from 22 imputated dosage files
@author Hetian Chen Mar 22 2015
"""


######################
# Target data location
######################
SNP_FILE='Top100.xlsx'

SHEET='Top100' # sheet name of top100.xlsx file

#######################
# Dosage files location 
#######################
DOSAGE_PREFIX= '/Volumes/Projects/LalesGWASData/release_2015-01-23/lales_imputation_20150114_dosage_chr'

DOSAGE_SURFIX= '.gen.gz'

##################
# Output file
##################
OUTFILE = 'results.gz' 




##################
# Define functions
##################

# Convert xlsx file to csv file
def csv_from_excel(xls_name,sheet_name,csv_name):

	wb = xlrd.open_workbook(xls_name)
	sh = wb.sheet_by_name(sheet_name)
	csv_file = open(csv_name, 'wb')
	wr = csv.writer(csv_file)

	for rownum in xrange(sh.nrows):
	    wr.writerow(sh.row_values(rownum))
	
	csv_file.close()

# Get target SNP from top 100 SNP file
def get_targetSNP(file_name):
	data = {str(k+1): [] for k in range(22)}

	with open(file_name,'rU') as target:
		for t,row in enumerate(csv.DictReader(target)):
			target_chr=str(int(float(row['CHR'])))
			target_snp=row['SNP'].rstrip()
			data[target_chr].append(target_snp)

	return data

# Get dosage data from imputed dosage file
def get_dosage(file_name):
	with gzip.open(file_name,"rb") as dosage_file:
		for t,row in enumerate(dosage_file):
			row_split = row.split()
			dosage_chr = row_split[0]
			dosage_snp = row_split[1]
			dosage_data = row
			yield t,dosage_chr,dosage_snp,dosage_data



SNP_FILE_CSV= 'Top100.csv' #intermediate csv file 
csv_from_excel(SNP_FILE,SHEET,SNP_FILE_CSV)
data= get_targetSNP(SNP_FILE_CSV)

all_start = time.time()
with gzip.open(OUTFILE,'wb') as outfile:
	for i in range(1,23): #loop through chromosome 1 to 22#
		start = time.time()
		chr_idx=str(i)
		dosage_file_name = DOSAGE_PREFIX+chr_idx+DOSAGE_SURFIX
		if not data[chr_idx]:
			print 'No target data needed in',dosage_file_name
			continue

		for t,dosage_chr,dosage_snp,dosage_data in get_dosage(dosage_file_name):
			if dosage_snp in data[dosage_chr]:
				idx = data[dosage_chr].index(dosage_snp)
				
				data[dosage_chr].pop(idx)
				print 'Found target data:',dosage_chr,dosage_snp

				outfile.write(dosage_data)

				if not data[dosage_chr]:
					print 'All target data in dosage file ' + chr_idx + ' is found. stop at line:',t
					break

		end = time.time()
		print 'Elapsed time in file ' + chr_idx + ':',end-start

all_end = time.time()
print 'Elapsed time of entire search:',all_end-all_start

	