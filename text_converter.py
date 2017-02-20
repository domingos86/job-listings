#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, re

chars_filename = 'chars'
words = set()
notwords = set()
if os.path.exists(chars_filename):
	with open(chars_filename, 'rb') as f:
		line = f.readline().replace('\n', '')
		for c in line:
			words.add(c)
		line = f.readline().replace('\n', '')
		for c in line:
			notwords.add(c)

def _save_chars():
	with open(chars_filename, 'wb') as f:
		for c in words:
			f.write(c)
		f.write('\n')
		for c in notwords:
			f.write(c)
		f.write('\n')

def convert(text):
	text = re.sub(r'[\s\d]+', ' ', text).strip()
	changed = False
	if re.search(r'[^\w\s]', text):
		text_list = list(text)
		for i in xrange(len(text_list)):
			if re.search(r'[\s\d]', text_list[i]) or text_list[i] in notwords:
				text_list[i] = ' '
				continue
			if re.search(r'\w', text_list[i]) is None and text_list[i] not in words:
				response = ''
				changed = True
				while len(response) == 0 or response.lower()[0] not in ['y', 'n']:
					response = raw_input('Character "%s": is it a word character or not? [y/n]:' % text_list[i])
				if response.lower()[0] == 'y':
					words.add(text_list[i])
				else:
					notwords.add(text_list[i])
					text_list[i] = ' '
		text = re.sub(r'\s+', ' ', ''.join(text_list)).strip()
	if changed:
		_save_chars()
	return text
