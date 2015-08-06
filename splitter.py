import csv
import data
import random

train_data = []
test_data = []
test_indices = []
def split(data_file):
	d = data.Data(data_file)
	for i in range(len(d.raw_data)):
		if i%3 == 0:
			# k = i-random.randint(0,2)
			# test_indices.append(k)
			# test_data.append(d.raw_data[k])
			test_data.append(d.raw_data[i])

		else:
			train_data.append(d.raw_data[i])
	# for i in range(len(d.raw_data)):
	# 	if i not in test_indices:
	# 		train_data.append(d.raw_data[i])
	print len(train_data), "train data"
	print len(test_data), "test_data"
	print len(d.raw_data), "total_data"		
	write("spambase_train_data.csv", train_data, d.raw_headers, d.raw_types)	
	write("spambase_test_data.csv",test_data, d.raw_headers, d.raw_types)



def write(filename, data_as_list, headers, types):	


	with open(filename,"w") as csvfile:
		dwriter = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
		dwriter.writerow(headers)
		dwriter.writerow(types)
		for data in data_as_list:
			dwriter.writerow(data)

split("spambase_original.csv")




       