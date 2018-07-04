# -*- coding: utf-8 -*-

import tensorflow as tf
import numpy as np
import time
import threading

class LoadModel(threading.Thread):
	"""docstring for LoadModel"""
	def __init__(self,queue,loop):
		super(LoadModel, self).__init__()
		self.freeze = False
		self.loop = loop
		self.queue = queue
	
	def load_frozenpb(self, file_name):
		with tf.gfile.GFile(file_name, "rb") as g:
			graph_def = tf.GraphDef()
			graph_def.ParseFromString(g.read())
			_ = tf.import_graph_def(graph_def, name="")
			self.g_def = graph_def
			self.g = g

		self.sess = tf.Session()
		self.freeze = True

	def load_restore(self):
		pass

	def load_savedpb(self, file_name="./model", tag=[tf.saved_model.tag_constants.SERVING], usingGPU=False):
		new_graph = tf.Graph()
		with new_graph.as_default():
			init = tf.global_variables_initializer()
			config = tf.ConfigProto()
			config.gpu_options.allow_growth = True
			if not usingGPU:
			    config.device_count['GPU'] = 0
			self.sess = tf.Session(config=config, graph=new_graph)
			self.sess.run(init)
			tf.saved_model.loader.load(self.sess, tag, file_name)

	def print_node(self):
		for node in self.sess.graph.get_operations():
			print("op: {}, name: {}".format(node.type,node.name))

	def freeze_model(save_name="./frozen_model.pb",output_name="output"):
		if self.freeze:
			print("{} model has frozen.".format(save_name))
			return

		gd = self.sess.graph.as_graph_def()

		for node in gd.node:
			if node.op == 'RefSwitch':
			    node.op = 'Switch'
			    for index in xrange(len(node.input)):
			      if 'moving_' in node.input[index]:
			          node.input[index] = node.input[index] + '/read'

			elif node.op == 'AssignSub':
			    node.op = 'Sub'
			    if 'use_locking' in node.attr: del node.attr['use_locking']
			elif node.op == 'AssignAdd':
			    node.op = 'Add'
			    if 'use_locking' in node.attr: del node.attr['use_locking']

		output_graph_def = tf.graph_util.convert_variables_to_constants(self.sess, gd, output_node_names=[output_name])
		with tf.gfile.FastGFile( save_name, mode='wb') as f:
		    f.write(output_graph_def.SerializeToString())
		    print("save model {} success.".format(save_name))

	def save_graph(self):
		try:
			tf.summary.FileWriter("./data",self.sess.graph)
			print("save graph success.")
		except:
			print("ERROR|save graph failed.")

	def run_tensor(self, batch=1, input_name="input", output_name="output"):
		print("run_tensor begin")
		listNode = self.sess.graph.get_operations()
		input_node = listNode[0]
		output_name = listNode[-1].name
		if input_node.type == "Placeholder":
			input_name = input_node.name

		print("in_name: {}\nout_name: {}".format(input_name,output_name))

		input_node = self.sess.graph.get_tensor_by_name(input_name + ":0")
		output_node = self.sess.graph.get_tensor_by_name(output_name +":0")

		in_shape = input_node.shape.as_list()
		in_shape[0] = batch
		input_data = np.ones(shape=in_shape)
		
		start_time = time.time()
		for x in range(self.loop):
			out = self.sess.run(output_node,feed_dict={input_node:input_data})
		# print(out)
		end_time = time.time()
		esp_time =  (end_time - start_time)/float(self.loop)
		esp_ms_time = round(esp_time * 1000, 2)
		# print("[TF] time used per loop is : %s ms" % ( esp_ms_time))
		self.queue.put(esp_ms_time)

	def run(self):
		self.run_tensor()
		print("run tensor end.")
