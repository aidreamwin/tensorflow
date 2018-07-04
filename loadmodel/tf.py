# -*- coding: utf-8 -*-

import argparse
import Queue
import csv
import os
from basic.tfinfo import LoadModel
from basic.pidinfo import PidInfo

def record2file(tm, mem,name="record",info="TF"):
	have = False
	if os.path.exists("./data/record.csv"):
		rw = open("./data/record.csv","r")
		try:
			csv_file = csv.reader(rw)
			for tmp in csv_file:
				if "Time(ms)" in tmp and "MEM(MB)" in tmp:
					have = True
				break
			rw.close()
		except Exception as e:
			print("wr",e)
			rw.close()
			
	ra = open("./data/record.csv","a")
	ct = [info,"%.2f"%tm,"%.2f"%mem]
	try:
		csv_write = csv.writer(ra,dialect='excel')
		if have:
			csv_write.writerow(ct)
		else:
			csv_write.writerow(["Condition","Time(ms)","MEM(MB)"])
			csv_write.writerow(ct)

		ra.close()
	except Exception as e:
		print("wa",e)
		ra.close()
		return

def prase_name(name):
	return name

def run_frozenmodel(input_model, loop, batch):
	queue = Queue.Queue()
	thread_model = LoadModel(queue,loop)
	thread_model.load_frozenpb(input_model)
	thread_pid = PidInfo(queue)
	thread_pid.start()
	thread_model.start()
	thread_model.join()
	thread_pid.join()

	tm = queue.get()
	mem = queue.get()
	print("time = %.2f ms, mem = %.2f MB" % (tm,mem))
	info = "TF:loop=%d/batch=%d" % (loop,batch)
	record2file(tm,mem,info)

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("-n","--input_model", default="./data/go_chess.pb",type=str, help="Frozen model file to read")
	parser.add_argument("-l","--loop", default=1,type=int, help="run loop")
	parser.add_argument("-b","--batch", default=1,type=int, help="batch size")
	args = parser.parse_args()
	run_frozenmodel(args.input_model,args.loop,args.batch)
	

if __name__ == '__main__':
	main()
