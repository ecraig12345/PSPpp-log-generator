#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Generates a PSP++ log text file from a series of CSV files. 
More information about PSP++ can be found at:
	http://www.cs.ou.edu/~rlpage/setools/Tools/PSP++readme.html
"""

import argparse
import codecs
import datetime
import itertools
import os
import sys

from entry_types import *
from unicode_csv import UnicodeFileDictReader

def _get_args():
	"""
	Parse the command line arguments and ask the user for any required values
	that are missing. Returns an argparse.Namespace.
	"""
	parser = argparse.ArgumentParser()
	parser.set_defaults(team_mode=None)
	
	# All positional arguments are optional so that the program can be run in
	# interactive mode from a standalone executable.
	parser.add_argument('time_file', nargs='?', help='path to time entry CSV file')
	parser.add_argument('defect_file', nargs='?', help='path to defect entry CSV file')
	parser.add_argument('object_file', nargs='?', help=('path to object ' +
						'entry CSV file (must have column specifying new/reused)'))
	parser.add_argument('out_file', nargs='?', help='path to output text file')
	parser.add_argument('--new-file', help='path to new object CSV file')
	parser.add_argument('--reused-file', help='path to reused object CSV file')
	parser.add_argument('--encoding', default='utf-8',
						help=('encoding to use for reading the CSV files ' +
						'(default is utf-8, and output is always written in utf-8)'))
	parser.add_argument('--header', help='path to text file with header info')

	# team mode options
	parser.add_argument('-n', '--name', 
						help='your name (only useful when not in team mode)')
	tgroup = parser.add_mutually_exclusive_group()
	tgroup.add_argument('-t', '--team', action='store_true', dest='team_mode',
						help='use team mode (default)')
	tgroup.add_argument('-i', '--individual', action='store_false', dest='team_mode',
						help='use individual mode')

	args = parser.parse_args()

	# Get values for any required things not specified.
	if not (args.time_file and args.out_file):
		print 'Note: your working directory is', os.getcwd()
		# If args.time_file is missing, assume we need to fill everything in.
		# (In the other cases, don't ask for most missing values, because 
		# the user might have left things blank intentionally.)
		if not args.time_file:
			args.time_file = raw_input('Path to time entry CSV file: ')
			args.defect_file = raw_input('Path to defect CSV file: ')
			args.object_file = raw_input('Path to combined object CSV file (optional): ')
			args.new_file = raw_input('Path to new object CSV file (optional): ')
			args.reused_file = raw_input('Path to reused object CSV file (optional): ')
		# Always ask for the output file if it's not specified (and force
		# the user to enter something).
		while not args.out_file:
			args.out_file = raw_input('Path to output text file: ')

	# Get information about team mode if it wasn't specified
	if args.team_mode == None:
		args.team_mode = raw_input('Use team mode? ')
		args.team_mode = (args.team_mode[:1].lower() == 'y')
	print ('U' if args.team_mode else 'Not u') + 'sing team mode.'
	if not args.team_mode and not args.name:
		args.name = raw_input('Your name (for filtering): ')
	if args.name: args.name = unicode(args.name)
	
	return args

def csv_to_entries(cls, csv_path, encoding, **kwargs):
	"""
	Parse a CSV file into a list of PSP entries for the given class type.
		cls: type to construct (must have "remappings" and "required" attributes)
		csv_path: path to CSV file
		kwargs: keyword arguments for the class constructor
	"""		
	entries = []
	with UnicodeFileDictReader(csv_path, encoding, lowercase_fieldnames=True,
			field_remappings=cls.remappings) as reader:
		fieldnames = set(reader.fieldnames)
		required_fields = set(cls.required)
		diff = required_fields - fieldnames
		if len(diff) != 0:
			print 'Error: some fields missing.'
			print 'Found: [%s]' % u', '.join(reader.fieldnames)
			print 'Missing: [%s]' % u', '.join(diff)
			sys.exit(1)
		
		for line_dict in reader:
			try:
				line_dict.update(kwargs)
				entries.append(cls(**line_dict))
			except Exception, e:
				print 'Invalid line: {%s}' % u', '.join(
						u'%s: %s' % kv for kv in line_dict.iteritems())
				print e
				continue
	entries.sort()
	return entries

def writelns(f, iterable, seps=1):
	"""
	Writes a line of text followed by the platform-specific line separator,
	because the codecs module doesn't convert \n...
	"""
	for line in iterable:
		f.write(line)
		f.write(os.linesep * seps)

def main():
	args = _get_args()
	time_entries, defect_entries, new_objects, reused_objects = [], [], [], []

	# Process time entry file
	if args.time_file:
		time_entries = csv_to_entries(PspTimeEntry, args.time_file, 
				args.encoding, team_mode=args.team_mode)
		# filter entries if requested
		if not args.team_mode:
			time_entries = [t for t in time_entries if t.name in (args.name, None)]
		time_entries.sort()

	# Process defect entry file
	if args.defect_file:
		defect_entries = csv_to_entries(PspDefectEntry, args.defect_file,
				args.encoding, team_mode=args.team_mode)
		# filter entries if requested
		if not args.team_mode:
			defect_entries = [d for d in defect_entries if d.name in (args.name, None)]
		defect_entries.sort()

	# Process object entry file(s). Really the user should only specify
	# object_file or [new_objects and/or reused_objects], but allow them to
	# do both here.
	if args.object_file:
		objects = csv_to_entries(PspObjectEntry, args.object_file, args.encoding)
		new_objects = [o for o in objects if o.obj_type == u'new']
		reused_objects = [o for o in objects if o.obj_type == u'reused']
	if args.new_file:
		new_objects.extend(csv_to_entries(PspObjectEntry, args.new_file,
				args.encoding, obj_type=u'new'))
	if args.reused_file:
		reused_objects.extend(csv_to_entries(PspObjectEntry, args.reused_file,
				args.encoding, obj_type=u'reused'))
	
	with codecs.open(args.out_file, 'w+', encoding='utf-8') as f:
		# Write the header
		if args.header: # use an existing file if requested
			with codecs.open(args.header, encoding=args.encoding) as h:
				f.writelines(h.readlines())
		else: # or use the info specified
			writelns(f, [u'name: _', 
					u'date: %s' % datetime.date.today().strftime(
							'%B %d, %Y').replace(' 0', ' '),
					u'program: _', u'language: _', u'instructor: _',
					u'actual added lines: 0', u'actual base lines: 0',
					u'actual modified lines: 0', u'actual removed lines: 0'])
		
		# Write any categories of entries used
		def write_entries(name, entries):
			if entries:
				writelns(f, [u'', name, u''])
				writelns(f, (unicode(e) for e in entries), seps=2)
		write_entries(u'time log:', time_entries)
		write_entries(u'new objects:', new_objects)
		write_entries(u'reused objects:', reused_objects)
		write_entries(u'defect log:', defect_entries)
	
		print 'Successfully wrote', args.out_file
		raw_input('Press enter/return to quit...')

if __name__ == '__main__':
	try:
		main()
	except Exception, e:
		print e
		raw_input('Press enter/return to quit...')
