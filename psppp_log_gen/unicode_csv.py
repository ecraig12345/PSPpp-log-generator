# -*- coding: utf-8 -*-

from csv import reader, Sniffer

# Borrowed from the csv module source; modified to support Unicode,
# opening files, and dialect sniffing
class UnicodeFileDictReader:
	"""
	Opens a CSV file with an arbitrary encoding and reads it into a dictionary
	(with field names as keys) one line at a time.
	"""
	def __init__(self, csv_path, encoding='utf-8', fieldnames=None, 
			restkey=None, restval=None, dialect=None,
			field_remappings=None, lowercase_fieldnames=False, *args, **kwds):
 # If the fieldnames parameter is omitted, the values in the first row of the 
#  csvfile will be used as the fieldnames. If the row read has more fields than 
#  the fieldnames sequence, the remaining data is added as a sequence keyed by 
#  the value of restkey. If the row read has fewer fields than the fieldnames 
#  sequence, the remaining keys take the value of the optional restval parameter. 
#  Any other optional or keyword arguments are passed to the underlying reader 
#  instance.
 		"""
		Open a CSV file.
			csv_path		Path to file
			encoding		Encoding to read the file with (default is utf-8)
			fieldnames		Use these instead of field names from a header row
			restkey			if a row has more fields than are in fieldnames,
							use this key for the sequence of remaining cells
			restval			If a row has fewer fields than are in fieldnames,
							use this value for the remaining keys
			dialect			csv.Dialect to read the file as. If not specified,
							the program guess (defaulting to 'excel').
			field_remappings Keys are possible alternate names for expected
							fields, and values are correct names. If any of 
							these keys is found as a field name, the field will
							be renamed to the key's value.
			lowercase_fieldnames Convert all field names to lowercase?
		Any other optional or keyword arguments are passed to the underlying
		csv.reader instance.
		"""
		self.encoding = encoding
		self._fieldnames = fieldnames	# list of keys for the dict
		self.restkey = restkey			# key to catch long rows
		self.restval = restval			# default value for short rows
		self.field_remappings = field_remappings
		self.lowercase_fieldnames = lowercase_fieldnames
		
		self.csv_file = open(csv_path, 'Urb') # universal newlines, binary
		# Detect the dialect of the file if no dialect was specified
		if dialect:
			self.dialect = dialect
		else:
			self.dialect = Sniffer().sniff(self.csv_file.read(1024)) or 'excel'
			self.csv_file.seek(0)
		self.reader = reader(self.csv_file, self.dialect, *args, **kwds)
		self.line_num = 0

	# __enter__ and __exit__ allow the class to be used in with statements.
	def __enter__(self):
		return self

	def __exit__(self, type, value, traceback):
		self.csv_file.close()
	
	def __iter__(self):
		return self

	@property
	def fieldnames(self):
		if self._fieldnames is None:
			try:
				# Convert the header row to Unicode 
				names = [unicode(cell, self.encoding) for cell in self.reader.next()]
				# Also convert to lowercase if requested
				if self.lowercase_fieldnames:
					names = [name.lower() for name in names]
				# Take care of any field name remappings requested
				for i, name in enumerate(names):
					if name in self.field_remappings:
						names[i] = self.field_remappings[name]
				self._fieldnames = names
			except StopIteration:
				pass
		self.line_num = self.reader.line_num
		return self._fieldnames

	@fieldnames.setter
	def fieldnames(self, value):
		self._fieldnames = value

	def next(self):
		if self.line_num == 0:
			# Used only for its side effect.
			self.fieldnames
		row = self.reader.next()
		self.line_num = self.reader.line_num

		# unlike the basic reader, we prefer not to return blanks,
		# because we will typically wind up with a dict full of None values
		while row == []:
			row = self.reader.next()
		row = [unicode(cell, self.encoding) for cell in row]
		d = dict(zip(self.fieldnames, row))
		lf = len(self.fieldnames)
		lr = len(row)
		if lf < lr:
			d[self.restkey] = row[lf:]
		elif lf > lr:
			for key in self.fieldnames[lr:]:
				d[key] = self.restval
		return d
