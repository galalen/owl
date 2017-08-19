import os
import time
import datetime
import argparse

try:
	from colorama import init, Fore
except:
	print("colorama dependency it's not installed")
	print("pip install colorama\n")


__VERSION__ = '1.0'

__AUTHOR__ = 'Mohammed Galalen'


class EventType(object):
	"""
		Represent the events that can be occurred
	"""

	CREATED = "created"
	MODIFIED = "modified"
	DELETED = "deleted"
	ACCESSED = "accessed"
	NOT_FOUND = "not found"


class Log(object):
	"""
		Nicely logging events
	"""

	def __init__(self):
		try:
			init()
		except:
			pass

	
	def __get_type_color(self, event_type):
		""" 
			Return color to log 
			Params:
				event_type = used to get the color to certain event
		"""

		if event_type == EventType.CREATED:
			return Fore.GREEN
		elif event_type == EventType.DELETED:
			return Fore.RED	
		elif event_type == EventType.ACCESSED:
			return Fore.BLUE
		elif event_type == EventType.MODIFIED:
			return Fore.YELLOW
		elif event_type == EventType.NOT_FOUND:
			return Fore.LIGHTRED_EX
		else:
			return Fore.WHITE


	def log(self, filename, event_type, etime):
		""" 
			Log event info to console 
			Params:

		"""

		info = str(etime)+ ': ' + filename + ' has been ' + event_type
		try:
			color = self.__get_type_color(event_type)
			print(color + info)
		except:
			print(info)


class File(object):
	""" File and helper function to manipluate data """

	def __init__(self, filepath):
		self.filepath = filepath
		self.file_stat = os.stat(filepath)


	def get_created(self, formated=False):
		""" 
			Time file or dir creation 
			Params:
				formated: used to return datetime in readable format 
		"""
		
		ctime = self.file_stat.st_ctime
		if formated:
			return self.__format(ctime)
		return ctime


	def get_accessed(self, formated=False):
		""" Last time file has been accessed """

		atime = self.file_stat.st_atime
		if formated:
			return self.__format(atime)
		return atime


	def get_modified(self, formated=False):
		""" Last time file has been modified """

		mtime = self.file_stat.st_mtime
		if formated:
			return self.__format(mtime)
		return mtime


	def __format(self, ttime):
		""" Return time in readable format """

		return datetime \
				.datetime \
				.fromtimestamp(ttime) \
				.strftime('%a %d/%b/%Y - %H:%M:%S.%f')


	def __str__(self):
		return self.filepath


	def __repr__(self):
		return self.filepath


class Owel(object):
	"""
		Watch for event that happend to files or dirs
	""" 

	def __init__(self):
		self.files = {}
		self.log = Log()
		self.running = False


	def register(self, *args):
		""" 
			Register files or dirs to be watched
		"""

		# Adding files to be watched
		for arg in args:
			if os.path.exists(arg):
				if os.path.isfile(arg):
					# handle file operation
					self.__add_file(File(arg))	
					
				elif os.path.isdir(arg):
					# handle dir operation
					self.dirs[arg] = File(arg).get_created()
					cur_files = self.__process_dir(arg)
					for ff in cur_files:
						self.__add_file(File(ff))

			else:
				# Path not found
				log_msg = '%s: %s not found' % (datetime.datetime.now(), arg)
				try:
					print(Fore.LIGHTRED_EX + log_msg)
				except:
					print(log_msg)



	def __add_file(self, fdata):
		""" Helper function for adding files to dict """

		if not str(fdata) in self.files.keys():
			self.files[str(fdata)] = fdata.get_created()

				
	def start_watching(self):
		""" Check event on files """
		
		for f in self.files.keys():
			if os.path.exists(f):
				fdata = File(f)
				if self.files[f] < fdata.get_modified():
					self.files[f] = fdata.get_modified()
					self.log.log(f, EventType.MODIFIED, fdata.get_modified(formated=True))
			else:
				# File not found on disk
				self.log.log(f, EventType.DELETED, datetime.datetime.now())
				del self.files[f]

		
				
		# Check for addition
		for fdir in self.dirs.keys():
			cur_files = self.__process_dir(fdir)
			for ff in cur_files:
				if ff not in self.files.keys():
					cur_f = File(ff)
					self.__add_file(cur_f)
					self.log.log(ff, EventType.CREATED, cur_f.get_created(formated=True))


	def __process_dir(self, dpath):
		""" Helper function to get files in the dir """

		cur_files = [(dpath+'/'+ff) for ff in os.listdir(dpath)]
		#else:
		#	cur_files = [ff for ff in os.listdir(dpath) \
		#				if not ff.startswith('.')]

		return cur_files


	def run(self):
		""" Start monitoring files or dirs"""
		
		print('Watching: %d files' % len(self.files))
		print(self.files.keys())
		self.running = True
		while self.running:
			self.start_watching()



	def stop(self, clear=False):
		""" Cancel watching process """

		self.running = False
		if clear:
			self.files.clear()
			del self.files




parser = argparse.ArgumentParser()
parser.add_argument("-f", "--files", help="print something", nargs='+', action="append", required=True)
args = parser.parse_args()

if args.files:
	owel = Owel()
	for f in args.files[0]:
		owel.register(f)
	owel.run()
