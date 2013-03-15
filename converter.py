#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (C) 2012-2013 Hydriz
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
import time
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
		self.special = False
		self.sitename = ""
		self.normalsuffixes = [
			'wiktionary',
			'wikibooks',
			'wikinews',
			'wikiquote',
			'wikisource',
			'wikiversity',
			'wikivoyage']
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
		self.specialnames = {
			"donatewiki": "Donate Wiki",
			"foundationwiki": "Wikimedia Foundation wiki",
			"mediawikiwiki": "MediaWiki.org",
			"metawiki": "Meta-Wiki",
			"nostalgiawiki": "Nostalgia Wikipedia",
			"outreachwiki": "Outreach Wiki",
			"sourceswiki": "Wikisource",
			"specieswiki": "Wikispecies",
			"strategywiki": "Wikimedia Strategic Planning",
			"testwiki": "Test Wikipedia",
			"test2wiki": "test2.Wikipedia",
			"usabilitywiki": "Wikimedia Usability Initiative",
			"wikidatawiki": "Wikidata"
		}

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
		# Shouldn't have any wikis that fall in this category, but leaving it here for forward compatibility
		if (self.site == "" and self.special == ""):
			self.sitename = wikidb # Keep it like the way it is now
		else:
			if not (os.path.exists('langlist.xml')):
				os.system('wget "https://en.wikipedia.org/w/api.php?action=sitematrix&smtype=language&smlangprop=localname|code&format=xml" -O langlist.xml -q')
			else:
				# Auto-update langlist.xml file after seven days
				lastchange = os.path.getctime('langlist.xml')
				now = time.time()
				weekago = now - 60*60*24*7
				if (lastchange < weekago):
					os.system('wget "https://en.wikipedia.org/w/api.php?action=sitematrix&smtype=language&smlangprop=localname|code&format=xml" -O langlist.xml -q')
				else:
					# Don't do anything (hackish way of making the script continue)
					blah = ""
			tree = ET.parse('langlist.xml')
			root = tree.getroot()
			if (self.special):
				if wikidb.endswith("wiki"):
					if (wikidb == "donatewiki"):
						self.sitename = "Donate Wiki"
					elif (wikidb == "foundationwiki"):
						self.sitename = "Wikimedia Foundation wiki"
					elif (wikidb == "mediawikiwiki"):
						self.sitename = "MediaWiki.org"
					elif (wikidb == "metawiki"):
						self.sitename = "Meta-Wiki"
					elif (wikidb == "nostalgiawiki"):
						self.sitename = "Nostalgia Wikipedia"
					elif (wikidb == "outreachwiki"):
						self.sitename = "Outreach Wiki"
					elif (wikidb == "sourceswiki"):
						self.sitename = "Wikisource"
					elif (wikidb == "specieswiki"):
						self.sitename = "Wikispecies"
					elif (wikidb == "strategywiki"):
						self.sitename = "Wikimedia Strategic Planning"
					elif (wikidb == "testwiki"):
						self.sitename = "Test Wikipedia"
					elif (wikidb == "test2wiki"):
						self.sitename = "test2.Wikipedia"
					elif (wikidb == "usabilitywiki"):
						self.sitename = "Wikimedia Usability Initiative"
					elif (wikidb == "wikidatawiki"):
						self.sitename = "Wikidata"
					elif (wikidb.startswith("wikimania")):
						tempname = wikidb.replace("wikimania","")
						wmyear = tempname.replace("wiki","")
						self.sitename = "Wikimania %s" % (wmyear)
					else:
						self.sitename = wikidb # Keep it like the way it is now
				else:
					if (wikidb == "betawikiversity"):
						self.sitename = "Wikiversity Beta"
					else:
						self.sitename = wikidb # Keep it like the way it is now
			else:
				for language in root.iter('language'):
					if (self.lang == language.get('code')):
						self.langname = language.get('localname')
						self.encodingcheck()
						self.sitename = "%s %s" % (self.langname, self.site)
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
		if wikidb.endswith("wiki"):
			length = len(wikidb)
			if length > 7: # enwiki = 6, angwiki = 7
				if any(wikidb in s for s in self.specialcases):
					self.site = "Wikipedia"
					intlang = wikidb.replace("wiki", "")
					self.lang = intlang.replace("_", "-")
				else:
					# Probably special wikis, will work on them later...
					self.special = True
					self.site = ""
			elif length < 8:
				if (wikidb == "tenwiki"):
					self.sitename = "Wikipedia 10"
				elif (wikidb == "fdcwiki"):
					self.sitename = "Wikimedia FDC"
				else:
					self.site = "Wikipedia"
					self.lang = wikidb.replace("wiki", "")
		elif wikidb.endswith("wikimedia"):
			code = wikidb.replace("wikimedia","")
			self.convertcountrycode(code)
			if (self.sitename == ""):
				self.sitename = wikidb # Keep it like the way it is now
		else:
			for suffix in self.normalsuffixes:
				if suffix in wikidb:
					if (wikidb == "betawikiversity"):
						self.special = True
						self.site = ""
					else:
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
		
		This function returns a date in %B %d, %Y format.
		"""
		d = datetime.strptime(date, '%Y%m%d')
		self.date = d.strftime('%B %d, %Y')
		return self.date

	def convertcountrycode(self, code):
		"""
		This function converts the country code into a readable name of the 
		country in question, used for chapter wikis.

		Note: This does not contain all countries, and may contain codes 
		that aren't really pointing to a country. In short, this is 
		Wikimedia-specific.
		"""
		if (code == 'ar'):
			self.sitename = 'Wikimedia Argentina'
		elif (code == 'bd'):
			self.sitename = 'Wikimedia Bangladesh'
		elif (code == 'be'):
			self.sitename = 'Wikimedia Belgium'
		elif (code == 'br'):
			self.sitename = 'Wikimedia Brazil'
		elif (code == 'co'):
			self.sitename = 'Wikimedia Colombia'
		elif (code == 'dk'):
			self.sitename = 'Wikimedia Denmark'
		elif (code == 'et'):
			self.sitename = 'Wikimedia Estonia'
		elif (code == 'fi'):
			self.sitename = 'Wikimedia Finland'
		elif (code == 'il'):
			self.sitename = 'Wikimedia Israel'
		elif (code == 'mk'):
			self.sitename = 'Wikimedia Macedonia'
		elif (code == 'mx'):
			self.sitename = 'Wikimedia Mexico'
		elif (code == 'nl'):
			self.sitename = 'Wikimedia Netherlands'
		elif (code == 'no'):
			self.sitename = 'Wikimedia Norway'
		elif (code == 'nyc'):
			self.sitename = 'Wikimedia New York City' # Unofficial
		elif (code == 'nz'):
			self.sitename = 'Wikimedia New Zealand'
		elif (code == 'pa_us'):
			self.sitename = 'Wikimedia Pennsylvania' # Unofficial
		elif (code == 'pl'):
			self.sitename = 'Wikimedia Poland'
		elif (code == 'rs'):
			self.sitename = 'Wikimedia Serbia'
		elif (code == 'ru'):
			self.sitename = 'Wikimedia Russia'
		elif (code == 'se'):
			self.sitename = 'Wikimedia Sweden'
		elif (code == 'tr'):
			self.sitename = 'Wikimedia Turkey'
		elif (code == 'ua'):
			self.sitename = 'Wikimedia Ukraine'
		elif (code == 'uk'):
			self.sitename = 'Wikimedia UK'
		elif (code == 've'):
			self.sitename = 'Wikimedia Venezuela'

if __name__ == "__main__":
	import sys
	error = "Opps, this script is meant to be called using another python script and not directly. Please study the documentation on how to use this from another script."
	print error
	sys.exit(1)
