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
# 
# Usage:
# self.site	-	This is the site that the wiki database should belong to.
#				E.g. if the database ends with "wiktionary", self.site 
#				will output "Wiktionary".
# self.langname - 	This is the language name of the wiki database. E.g. 
#					"en" will become "English".
# self.date	-	This is the output date (20121010 to October 10, 2012).
#
# TODO:
# * The script does not work for special wikis (i.e. incubatorwiki).
# * The language code hacks should be fixed upstream at CLDR, though it 
#   isn't of the highest priority right now.

from datetime import datetime
import os
import re
import urllib
import xml.etree.ElementTree as ET

class ASConverter:
	def __init__(self):
		"""
		The initialiser function for all the globals.
		"""
		# Globals for conversion of wiki databases to site names
		self.itemlist = ""
		self.lang = ""
		self.langname = ""
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

		# Globals for conversion of dates to human-readable format.
		self.date = ""

	def convertdb(self, wikidb):
		"""
		This is the main function for converting database names into proper 
		readable wiki names (i.e. enwiki -> English Wikipedia).
		
		TODO: Make this script work for special wikis.
		
		wikidb - The database name to work on.
		"""
		self.sanitycheck(wikidb)
		if (self.site == ""):
			self.name = wikidb # Keep it like the way it is now
		else:
			if not (os.path.exists('langlist.xml')):
				os.system('wget "https://en.wikipedia.org/w/api.php?action=sitematrix&smtype=language&smlangprop=localname|code&format=xml" -O langlist.xml -q')
			else:
				# Don't do anything (hackish way of making the script continue)
				blah = ""
			tree = ET.parse('langlist.xml')
			root = tree.getroot()
			for language in root.iter('language'):
				if (self.lang == language.get('code')):
					self.langname = language.get('localname')
					self.encodingcheck()
					break
				elif (self.lang == 'beta'):
					self.langname = 'Beta' # Support for Beta Wikiversity
					break
				else:
					continue
	
	def sanitycheck(self, wikidb):
		"""
		This function will figure out the site that the database belongs 
		to. It is guessed from the database name, although there are 
		exceptions to this for the special wikis (i.e. metawiki). These 
		special wikis will be kept in its original state (its part of 
		the file's TODO).
		
		This function is called by self.convertdb().
		
		wikidb - The database name to work with.
		"""
		if "wiki" in wikidb:
			length = len(wikidb)
			if length > 7: # enwiki = 6, angwiki = 7
				if any(wikidb in s for s in self.specialcases):
					self.site = "Wikipedia"
					intlang = wikidb.replace("wiki", "")
					self.lang = intlang.replace("_", "-")
				else:
					# Probably special wikis, will work on them later...
					self.site = ""
			elif length < 8:
				if (wikidb == "tenwiki"):
					self.site = ""
				else:
					self.site = "Wikipedia"
					self.lang = wikidb.replace("wiki", "")

		for suffix in self.normalsuffixes:
			if suffix in wikidb:
				self.site = suffix.title() # Capitalises the first letter
				templang = wikidb.replace(suffix, "")
				self.lang = templang.replace("_", "-")
				break
			else:
				continue

	def encodingcheck(self):
		"""
		This function checks if the wiki database name matches a set marked 
		out as having issues with encoding, which can cause scripts to go 
		crazy and exit altogether.
		
		This function is called by self.convertdb()
		
		TODO: Fix the language codes upstream so that we don't have to do 
		this hackish method of making the languages really English.
		"""
		if (self.lang == "be-x-old"):
			self.langname = "Belarusian Classical"
		elif (self.lang == "bxr"):
			self.langname = "Russia Buriat"
		elif (self.lang == "fiu-vro"):
			self.langname = "Voro"
		elif (self.lang == "frp"):
			self.langname = "Arpitan"
		elif (self.lang == "lbe"):
			self.langname = "Lak"
		elif (self.lang == "nb"):
			self.langname = "Norwegian Bokmal"
		elif (self.lang == "no"):
			self.langname = "Norwegian"
		elif (self.lang == "pfl"):
			self.langname = "Palatinate German"
		elif (self.lang == "roa-tara"):
			self.langname = "Tarantino"
		elif (self.lang == "vec"):
			self.langname = "Venetian"
		elif (self.lang == "vo"):
			self.langname = "Volapuk"

	def convertdate(self, date):
		"""
		This is the main function for converting the date into a more human-
		readable format. In this case, we are changing things like:
		20121010 -> October 10, 2012
		
		This function is supposed to be directly called by the archive scripts.
		
		Parameters:
		* date - The date format to work on (should be %Y%m%d format)
		
		This function returns a date in %B %d, %Y format. Please use the 
		self.date variable in the script.
		"""
		d = datetime.strptime(date, '%Y%m%d')
		self.date = day_string = d.strftime('%B %d, %Y')
