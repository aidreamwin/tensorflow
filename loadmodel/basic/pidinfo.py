# -*- coding: utf-8 -*-

import threading
import os
import time

class PidInfo(threading.Thread):
	"""docstring for PidInfo"""
	import os
	def __init__(self,queue):
		super(PidInfo, self).__init__()
		self.pid = os.getpid()
		self.queue = queue

	def get_mem(self):
		totalList = []
		if self.pid > 0:
			while self.queue.empty():
				cmd = "grep VmRSS /proc/%d/status" % self.pid
				result = os.popen(cmd).read()
				if result=='':
					print("cmd %s error."%cmd)
					return
				result.replace(' ','')
				#print(result)
				left = result.find("VmRSS:")
				right = result.find("kB")
				if left<0 or right<0:
					print("find VmRSS failed.",left,right)
					return

				mem = result[left+6:right]
				totalList.append(float(mem)) # kb
				print("%.2f MB"%(float(mem)/1024))
				time.sleep(1)
		totalList.sort()
		total = 0
		avg = 0
		if len(totalList)>2:
			totalList = totalList[1:-1]
			for x in totalList:
				total+=x
			avg = total/len(totalList)
		elif len(totalList)==2:
			total = totalList[1]
			avg = total/2
		else:
			pass
		# print("%.2f MB"%(avg/1024))
		self.queue.put(avg/1024)


	def run(self):
		self.get_mem()
		print("get mem end.")
