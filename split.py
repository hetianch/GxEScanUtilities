'''
This script is used to split given .gz file by chr. 
@author Hetian Chen Mar 24 2015

Example:
python split.py -i bin2.info.gz --v 0.3

'''


import gzip
from sys import argv, stdout, stderr
import argparse
import os
import datetime
import time

##############################################################################
# class, function, generator definitions #####################################
##############################################################################

class SPLIT():

	def __init__(self,input_file,value):

		self.input_file = input_file
		self.value = value
		self.line_count = 0

	def get_data(self):
		try:
			with gzip.open(self.input_file,"rb") as reader:
				for t,row in enumerate(reader):
					if t == 0: # first row is column name
						continue
					
					data = row.split()
					chr_idx = data[0]
					rs_id = data[1]
					position = data[2]
					a0 = data[3]
					a1 = data[4]
					info = data[6]
					yield t,chr_idx, rs_id, position, a0, a1, info
		
		except Exception as ex: #catch exception if not able to read input file
			template = "An exception of type {0} occured. Arguments:\n{1!r}"
			message = template.format(type(ex).__name__, ex.args)
			stderr.write('encountered exception when reading input file...\n'+str(message))

	def write_file(self,file_name,data):
		with open(file_name,'a') as outfile:
			outfile.write('%s %s %s %s %s %s\n' % (data[0],data[1],0,data[2],data[3],data[4]))

	def split_file(self):
		
		start = time.time()
		#make results folder : results_YearMonthDayHourMinuteSecond
		script_path =  os.path.realpath(__file__)
		results_path = os.path.dirname(script_path) +'/results_' \
					+str(datetime.datetime.now().year)\
					+str(datetime.datetime.now().month)\
					+str(datetime.datetime.now().day)\
					+str(datetime.datetime.now().hour)\
					+str(datetime.datetime.now().minute)

		try: 
			if not os.path.exists(results_path):
				os.makedirs(results_path)

		except Exception as ex: #catch exception if not able to make folder
			template = "An exception of type {0} occured. Arguments:\n{1!r}"
			message = template.format(type(ex).__name__, ex.args)
			stderr.write('encountered exception when splitting files...\n'+str(message))

		
		#read input file line by line and write to result files
		for t,chr_idx, rs_id, position, a0, a1, info in self.get_data():
			
			# change position to negative if info > given cut off value 
			if float(info) > self.value:
				position = '-'+position

			file_surfix = str(self.value).replace('.','')+'.bim'
			file_name = results_path + '/chr'+chr_idx+'_'+file_surfix
			data = [chr_idx,rs_id,position,a0,a1]
			self.write_file(file_name,data)

		end = time.time()
		stderr.write('Elapsed time: %ds' % int(end-start))

##############################################################################
# start split ################################################################
##############################################################################
def myargs():
    
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description = 
""" 
Split file by chr. Output chr,rs_id, position, a0, a1. 

If info_value > value  {
	Position = - position 
} else {
	Position = Position
}

\nUsage is via:
\n
\n\t\tpython split.py -i <input file name> --v <value>
\n

""")
    parser.add_argument('-i', type = str)
    parser.add_argument('--v', default = 0.3, type = float)
  
    args = parser.parse_args()
    for v in vars(args).keys():
        stderr.write("%s => %s\n" % (v, str(vars(args)[v])))
    return args

def run():
    args = myargs()
    input_file = args.i
    cutoff = args.v
    if cutoff > 1 or cutoff<0:
    	stderr.write("--v value should be within 0 to 1\n")  
    else:
	    split = SPLIT(input_file,cutoff)
	    split.split_file()
        
if __name__ == "__main__":
	run()
