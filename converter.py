#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (C) 2012-2015 Hydriz Scholz
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

from datetime import datetime
import os
import re
import time
import urllib
import xml.etree.ElementTree as ET

class IncorrectUsage(Exception):
	pass

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
			'wikivoyage'
		]
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
			'zh_yuewiki'
		]
		self.badcases = [
			'tenwiki'
		]

		self.specialnames = {
			"advisorywiki": "Advisory Board wiki",
			"commonswiki": "Wikimedia Commons",
			"donatewiki": "Donate Wiki",
			"fdcwiki": "Wikimedia FDC",
			"foundationwiki": "Wikimedia Foundation wiki",
			"incubatorwiki": "Wikimedia Incubator",
			"loginwiki": "Wikimedia Login wiki",
			"mediawikiwiki": "MediaWiki.org",
			"metawiki": "Meta-Wiki",
			"nostalgiawiki": "Nostalgia Wikipedia",
			"outreachwiki": "Outreach Wiki",
			"qualitywiki": "Wikimedia Quality",
			"sourceswiki": "Wikisource",
			"specieswiki": "Wikispecies",
			"strategywiki": "Wikimedia Strategic Planning",
			"tenwiki": "Wikipedia 10",
			"testwikidatawiki": "Wikidata Test Wiki",
			"testwiki": "Test Wikipedia",
			"test2wiki": "test2.Wikipedia",
			"usabilitywiki": "Wikimedia Usability Initiative",
			"votewiki": "Wikimedia Vote Wiki",
			"wikidatawiki": "Wikidata"
		}

		# 25 wikis
		self.countrycode = {
			"am": "Wikimedia Armenia",
			"ar": "Wikimedia Argentina",
			"bd": "Wikimedia Bangladesh",
			"be": "Wikimedia Belgium",
			"br": "Wikimedia Brazil",
			"ca": "Wikimedia Canada",
			"cn": "Wikimedia China",
			"co": "Wikimedia Colombia",
			"dk": "Wikimedia Denmark",
			"et": "Wikimedia Estonia",
			"fi": "Wikimedia Finland",
			"il": "Wikimedia Israel",
			"mai": "Maithili Wikimedians",
			"mk": "Wikimedia Macedonia",
			"mx": "Wikimedia Mexico",
			"nl": "Wikimedia Netherlands",
			"no": "Wikimedia Norway",
			"nyc": "Wikimedia New York City", # Unofficial
			"nz": "Wikimedia New Zealand",
			"pa_us": "Wikimedia Pennsylvania", # Unofficial
			"pl": "Wikimedia Poland",
			"pt": "Wikimedia Portugal",
			"rs": "Wikimedia Serbia",
			"ru": "Wikimedia Russia",
			"se": "Wikimedia Sweden",
			"tr": "Wikimedia Turkey",
			"ua": "Wikimedia Ukraine",
			"uk": "Wikimedia UK",
			"ve": "Wikimedia Venezuela",
			"wb": "Wikimedia West Bengal"
		}

		# Globals for conversion of dates to human-readable format.
		self.date = ""

	def convertdb(self, wikidb):
		"""
		This is the main function for converting database names into proper 
		readable wiki names (i.e. enwiki -> English Wikipedia).

		wikidb - The database name to work on.
		"""
		self.sanitycheck(wikidb)
		# Shouldn't have any wikis that fall in this category, but leaving it here for forward compatibility
		if (self.site == "" and self.special == ""):
			self.sitename = wikidb # Keep it like the way it is now
		else:
			if not (os.path.exists('langlist.xml')):
				urllib.urlretrieve( "https://en.wikipedia.org/w/api.php?action=sitematrix&smtype=language&smlangprop=localname|code&format=xml", "langlist.xml")
			else:
				# Auto-update langlist.xml file everyday
				lastchange = os.path.getctime('langlist.xml')
				now = time.time()
				weekago = now - 60*60*24*1
				if (lastchange < weekago):
					urllib.urlretrieve( "https://en.wikipedia.org/w/api.php?action=sitematrix&smtype=language&smlangprop=localname|code&format=xml", "langlist.xml")
				else:
					pass
			tree = ET.parse('langlist.xml')
			root = tree.getroot()
			if (self.special):
				if wikidb.endswith("wiki"):
					if wikidb in self.specialnames:
						self.sitename = self.specialnames[wikidb]
					elif (wikidb.startswith("wikimania")):
						tempname = wikidb.replace("wikimania","")
						wmyear = tempname.replace("wiki","")
						self.sitename = "Wikimania %s" % (wmyear)
					else:
						self.sitename = wikidb # Keep it like the way it is now
				elif (wikidb.endswith("wikimedia")):
					code = wikidb.replace("wikimedia","")
					self.convertcountrycode(code)
					if (self.sitename == ""):
						self.sitename = wikidb # Keep it like the way it is now
				else:
					if (wikidb == "betawikiversity"):
						self.sitename = "Wikiversity Beta"
					else:
						self.sitename = wikidb # Keep it like the way it is now
			else:
				for language in root.iter('language'):
					if (self.lang == language.get('code')):
						self.langname = language.get('localname').encode('utf8')
						self.sitename = "%s %s" % (self.langname, self.site)
						break
					else:
						continue
		if ( self.sitename == wikidb ):
			f = open( "problem", "a" )
			f.write( "%s\n" % ( wikidb ) )
			f.close()
	
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
					self.special = True
				elif (wikidb == "fdcwiki"):
					self.special = True
				else:
					self.site = "Wikipedia"
					self.lang = wikidb.replace("wiki", "")
		elif wikidb.endswith("wikimedia"):
			self.special = True
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
		if code in self.countrycode:
			self.sitename = self.countrycode[code]

if __name__ == "__main__":
	raise IncorrectUsage("Script cannot be called directly")