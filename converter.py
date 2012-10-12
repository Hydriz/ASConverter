#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (C) 2012 Hydriz
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# This is the converter class for all archiving scripts by Hydriz. It
# is not designed to work standalone, but rather as a supporting scripts 
# for the scripts. You can find the different archiving projects and 
# scripts at https://github.com/Hydriz

import os
import re
import urllib
from xml.dom import minidom

class ASConverter(object):
	def convertdb(self, wikidb):
		"""
		This is the main function for converting database names into proper 
		readable wiki names (i.e. enwiki -> English Wikipedia).
		
		TODO: Make this script work for special wikis.
		"""
		self.apicall(wikidb)
		for entry in self.itemlist:
			if (self.lang == entry):
				return entry.attributes['localname'].value
				break
			else:
				continue
		
	def apicall(self, wikidb):
		"""
		This is the function used by the class to do switching of the 
		database name into a human-readable site name.
		
		This function is called by self.convertdb().
		
		wikidb - The database name to work with.
		"""
		self.sanitycheck(wikidb)
		if (self.site == ""):
			self.name = wikidb # Keep it like the way it is now
		else:
			#os.system('wget "https://en.wikipedia.org/w/api.php?action=sitematrix&smtype=language&smlangprop=localname|code&format=xml" -O langlist.xml')
			xmldoc = minidom.parse('langlist.xml')
			self.itemlist = xmldoc.getElementsByTagName('language')
	
	def sanitycheck(self, wikidb):
		"""
		This function will figure out the site that the database belongs 
		to. It is guessed from the database name, although there are 
		exceptions to this for the special wikis (i.e. metawiki). These 
		special wikis will be kept in its original state (its part of 
		the file's TODO).
		
		This function is called by self.apicall().
		
		wikidb - The database name to work with.
		"""
		for suffix in self.normalsuffixes:
			if suffix in wikidb:
				self.site = suffix.title() # Capitalises the first letter
				self.lang = wikidb.replace(suffix, "")
				break
			else:
				continue

		if 'wiki' in wikidb:
			length = len(wikidb)
			if length > 7: # enwiki = 6, angwiki = 7
				if any(wikidb in s for s in self.specialcases):
					self.site = "Wikipedia"
					self.lang = wikidb.replace("wiki", "")
				else:
					# Probably special wikis, will work on them later...
					self.site = ""
			elif length < 8:
				if any(wikidb in s for s in self.badcases):
					self.site = ""
				else:
					self.site = "Wikipedia"
					self.lang = wikidb.replace("wiki", "")

	def __init__(self):
		"""
		The initialiser function for all the globals.
		"""
		self.itemlist = ""
		self.lang = ""
		self.site = ""
		self.normalsuffixes = [
			'wiktionary',
			'wikibooks',
			'wikinews',
			'wikiquote',
			'wikisource',
			'wikiversity']
		self.specialcases = [
			'bat_smgwiki',
			'be_x_oldwiki',
			'cbk_zamwiki',
			'fiu_vrowiki',
			'map_bmswiki',
			'nds_nlwiki',
			'roa_rupwiki',
			'roa_tarawiki',
			'simplewiki',
			'zh_classicalwiki',
			'zh_min_nanwiki',
			'zh_yuewiki']
		self.badcases = [
			'tenwiki']