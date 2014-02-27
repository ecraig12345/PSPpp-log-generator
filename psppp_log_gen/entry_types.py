# -*- coding: utf-8 -*-

"""
Classes representing various types of entries in the PSP++ log file
"""

import datetime
import os

class PspTimeEntry(object):
	"""
	Entry for the time log section of the PSP++ log file
	"""
	# Remappings to allow other commonly used field names in input
	remappings = { u'comments': u'comment', u'note': u'comment', 
			u'notes': u'comment', u'finish': u'end' }
	# Required fields for constructor
	required = (u'date', u'start', u'end', u'phase', u'comment')

	def __init__(self, date, start, end, phase, comment, team_mode=False,
			name=None, **kwargs):
		"""
		Initialize a time entry. Date format must be m/d/yyyy. Time format
		must be h:mm in 24-hour time. **kwargs are ignored (**kwargs is only 
		in the parameter list so the constructor can be called with a dict that
		might contain extra args).
		Raises ValueError if anything is wrong.
		"""
		error_gen = lambda s : ValueError('PspTimeEntry requires a %s' % s)
		if not date: raise error_gen('date')
		if not start: raise error_gen('start')
		if not end: raise error_gen('end')
		if not phase: raise error_gen('phase')
		if not comment: raise error_gen('comment')
		# Google Forms date formatting, M/D/YYYY, is different than Python's 
		# required format. There's no option for date parts without a 
		# leading 0 in strptime, so parse the date manually.
		date_parts = [int(d) for d in date.split('/')]
		self.date = datetime.date(date_parts[2], date_parts[0], date_parts[1])
		# Google Forms stores dates as h:mm:ss, using 24-hour time and not
		# padding the hour with 0s. 
		if len(start) == 7: start = '0' + start
		try: 
			self.start = datetime.datetime.strptime(start, '%H:%M:%S').time()
		except ValueError:
			self.start = datetime.datetime.strptime(start, '%H:%M').time()
		if len(end) == 7: end = '0' + end
		try:
			self.end = datetime.datetime.strptime(end, '%H:%M:%S').time()
		except ValueError:
			self.end = datetime.datetime.strptime(end, '%H:%M').time()
		self.phase = phase
		if team_mode and name: comment = u'(%s) %s' % (name, comment)
		self.comment = comment
		self.name = name
	
	def __lt__(self, other):
		return self.date < other.date and self.start < other.start \
				and self.end < other.end and self.name < other.name
		
	def __unicode__(self):
		# Using os.linesep for joining assumes that if the resulting string is
		# written to files, it will always be done using the codecs module.
		return unicode(os.linesep).join([
				u'\t- date: ' + self.date.strftime('%b %d, %Y').replace(' 0', ' '),
				u'\t  start time: ' + self.start.strftime('%I:%M%p').lstrip('0'),
				u'\t  end time: ' + self.end.strftime('%I:%M%p').lstrip('0'),
				u'\t  phase: ' + self.phase,
				u'\t  comment: ' + self.comment])
	
	def __str__(self):
		return unicode(self).encode('utf-8')

class PspObjectEntry(object):
	"""
	Entry for the new or reused objects log sections of the PSP++ log file
	"""
	remappings = { u'object type': u'obj_type', u'new/reused': u'obj_type',
			u'estimated lines': u'est_lines', 	  u'lines': u'est_lines',
			u'estimated base': u'est_base', 	  u'base': u'est_base',
			u'estimated removed': u'est_removed', u'removed': u'est_removed',
			u'estimated modified': u'est_modified', u'modified': u'est_modified',
			u'estimated added': u'est_added', 	  u'added': u'est_added',
			u'comments': u'comment', u'note': u'comment', u'notes': u'comment' }
	required = (u'name', u'type')

	def __init__(self, name, type, obj_type=None, comment=None, est_lines=None,
			est_base=None, est_removed=None, est_modified=None, est_added=None,
			**kwargs):
		"""
		Initialize an object entry. Raises ValueError if: 
			- obj_type is not one of "new", "reused", or None
			- obj_type is "new" and est_lines is not specified
			- obj_type is "reused" and est_base is not specified
			- est_lines, est_base, est_removed, est_modified, or est_added is
			  specified and is not an int
			- name or type is missing
		**kwargs are ignored (**kwargs is only in the parameter list so the 
		constructor can be called with a dict that might contain extra args).
		"""
		if not name: raise ValueError('PspObjectEntry requires a name')
		if not type: raise ValueError('PspObjectEntry requires a type')
		
		if obj_type:
			# An object type was specified. Make sure required information for
			# that object type was provided.
			self.obj_type = unicode(obj_type.lower())
			if self.obj_type == u'new':
				if est_lines == None:
					raise ValueError('must specify est_lines for obj_type "new"')
			elif self.obj_type == u'reused':
				if est_base == None:
					raise ValueError('must specify est_base for obj_type "reused"')
			else:
				raise ValueError('obj_type must be "new" or "reused"')
		else:
			# No object type was specified. Try to guess.
			if est_lines:
				self.obj_type = u'new'
			elif est_base:
				self.obj_type = u'reused'
			else:
				raise ValueError('obj_type not specified and couldn\'t be inferred')
		self.name = name
		self.type = type
		self.comment = comment
		
		int_or_0 = lambda val: int(val) if val else None
		# Don't set values that are inappropriate for this object type
		if self.obj_type == u'new':
			self.est_lines = int(est_lines)
		else:
			self.est_base = int_or_0(est_base)
			self.est_removed = int_or_0(est_removed)
			self.est_modified = int_or_0(est_modified)
			self.est_added = int_or_0(est_added)
	
	def __unicode__(self):
		val_str = lambda name, val: u'\t  %s: %s' % (name, val)
		str_lst = [u'\t- name: ' + self.name, val_str(u'type', self.type)]
		if self.obj_type == u'new':
			str_lst += [val_str(u'estimated lines', self.est_lines)]
		else:
			str_lst.extend(val_str(name, val) for name, val in 
						((u'estimated base', self.est_base),
						(u'estimated removed', self.est_removed),
						(u'estimated modified', self.est_modified),
						(u'estimated added', self.est_added))
					if val != None)
		if self.comment:
			str_lst += [val_str(u'comment', self.comment)]

		# Using os.linesep for joining assumes that if the resulting string is
		# written to files, it will always be done using the codecs module.
		return unicode(os.linesep).join(str_lst)

	def __str__(self):
		return unicode(self).encode('utf-8')

class PspDefectEntry(object):
	"""
	Entry for the defect log section of the PSP++ log file
	"""
	remappings = { u'fix time': u'fix_time' }
	required = (u'date', u'type', u'fix_time', u'comment')
	
	def __init__(self, date, type, fix_time, comment, team_mode=False,
			name=None, **kwargs):
		"""
		Initialize a defect entry. Date format must be m/d/yyyy. **kwargs are 
		ignored (**kwargs is only in the parameter list so the constructor can 
		be called with a dict that might contain extra args).
		Raises ValueError if anything is wrong.
		"""
		error_gen = lambda s : ValueError('PspDefectEntry requires a %s' % s)
		if not date: raise error_gen('date')
		if not type: raise error_gen('type')
		if fix_time == None: raise error_gen('fix time')
		if not comment: raise error_gen('comment')
		
		date_parts = [int(d) for d in date.split('/')]
		self.date = datetime.date(date_parts[2], date_parts[0], date_parts[1])
		self.type = type
		self.fix_time = int(fix_time)
		if team_mode and name: comment = u'(%s) %s' % (name, comment)
		self.comment = comment
		self.name = name

	def __lt__(self, other):
		return self.date < other.date
	
	def __unicode__(self):
		# Using os.linesep for joining assumes that if the resulting string is
		# written to files, it will always be done using the codecs module.
		return unicode(os.linesep).join([
				u'\t- date: ' + self.date.strftime('%b %d, %Y').replace(' 0', ' '),
				u'\t  type: ' + self.type,
				u'\t  fix time: %s' % self.fix_time,
				u'\t  comment: ' + self.comment])

	def __str__(self):
		return unicode(self).encode('utf-8')
