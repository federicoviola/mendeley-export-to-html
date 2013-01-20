#!/usr/bin/python

"""
Script to get papers from a particular folder in the Desktop version
 of Mendeley to an HTML file.
"""

#########################################################################
# HEADER DECLARATIONS							#
#########################################################################

# Import modules
import shutil
import os
import getpass
import sqlite3
import time
import urllib
import sys

#########################################################################
# TEST FOR CONFIG FILE AND FINDING THE DATABASE				#
#########################################################################

#Check for config file
try:
	from configfile import *
except:
	print "\n The configuration file is missing.\n  Rename the file configfile.py.dist to configfile.py\n  and fill the values.\n"
	sys.exit (1)

#Try to connect
linux_username=getpass.getuser()
conn = sqlite3.connect('/home/' + linux_username + '/.local/share/data/Mendeley Ltd./Mendeley Desktop/' + mendeley_user + '@www.mendeley.com.sqlite')
#TEMP DB FOR TESTING
#conn = sqlite3.connect(mendeley_user + '@www.mendeley.com.sqlite')
conn.text_factory = str

#########################################################################
# FUNCTION DECLARATIONS							#
#########################################################################

def getfolders():
	"""
	Get Mendeley folders
	"""
	cursor = conn.cursor()
	cursor.execute('SELECT id, name FROM Folders')
	allfolders=cursor.fetchall()
	for x in allfolders:
		print "ID: " + str(x[0]) + " - Folder name: " + x[1]
	cursor.close()
	
def export(folderID):
	"""
	Export papers to html folder
	"""
	if folderID == "":
		print "Error: The Folder ID: " + str(folderID) + " does not exists. \n\n Exiting...\n\n"
		sys.exit (1)
	if os.path.exists('html')==True:
		shutil.rmtree('html')
	os.makedirs('html')
	os.makedirs('html/files')
	cursor = conn.cursor()
	cursor.execute('SELECT count() FROM Documents, DocumentFolders WHERE DocumentFolders.folderID=' + str(folderID) + ' AND DocumentFolders.documentid=Documents.id AND Documents.type="JournalArticle"')
	count_files=cursor.fetchone()[0]
	cursor.execute('SELECT Documents.id, Documents.year, Documents.title, Documents.publication, Documents.pages, Documents.doi FROM Documents, DocumentFolders WHERE DocumentFolders.folderID=' + str(folderID) + ' AND DocumentFolders.documentid=Documents.id AND Documents.type="JournalArticle"')
	allfiles=cursor.fetchall()
	f = open('html/index_unordered.html', 'a')
	for x in allfiles:
		cursor2 = conn.cursor()
		cursor2.execute('SELECT count(), firstNames, lastName FROM DocumentContributors WHERE DocumentContributors.documentid=' + str(x[0]) + ' AND DocumentContributors.contribution="DocumentAuthor"')
		count_authors=cursor2.fetchone()[0]
		cursor2.execute('SELECT firstNames, lastName FROM DocumentContributors WHERE DocumentContributors.documentid=' + str(x[0]) + ' AND DocumentContributors.contribution="DocumentAuthor"')
		allauthors=cursor2.fetchall()
		a_counter=1
		for y in allauthors:
			if type(y[0])!=type(None):
				f_name = y[0]
				f_name = f_name.title()
			else:
				f_name = ""
			if type(y[1])!=type(None):
				l_name = y[1].title()
				l_names = l_name.split("-")
				for i, w in enumerate(l_names):
					l_names[i] = w.title()
				l_name.join(l_names)
			else:
				l_name = ""
			if a_counter==1:
				f.write(l_name + ", " + f_name)
			else:
				f.write(" " + f_name + " " + l_name)
			if a_counter != count_authors:
				f.write(",")
			a_counter = a_counter+1
		d_year = str(x[1])
		if type(x[2])!=type(None):
			d_title = x[2]
			d_title = d_title.title()
		else:
			d_title = ""

		if type(x[3])!=type(None):
			d_journal = x[3]
			d_journal = d_journal.capitalize()
		else:
			d_journal = ""
		if type(x[4])!=type(None):
			d_pages = x[4]
		else:
			d_pages = ""
		f.write(". " + d_year + ". " + d_title + ". " + d_journal + ": " + d_pages)
		f.write(". ")
		if type(x[5])!=type(None):
			d_doi = x[5]
			f.write(" doi: <a href=\"http://dx.doi.org/" + d_doi + "\">" + d_doi + "</a>")
		cursor2.close()
		cursor3 = conn.cursor()
		cursor3.execute('SELECT count() FROM DocumentFiles, Files WHERE DocumentFiles.documentid=' + str(x[0]) + ' AND DocumentFiles.hash=Files.hash')
		count_authors=cursor3.fetchone()[0]
		cursor3.execute('SELECT Files.localUrl FROM DocumentFiles, Files WHERE DocumentFiles.documentid=' + str(x[0]) + ' AND DocumentFiles.hash=Files.hash')
		allfiles=cursor3.fetchall()
		for z in allfiles:
			f_url = z[0]
			f_url = f_url.encode('ascii')
			f_url = f_url[7:]
			if f_url[-3:]=="pdf" or f_url[-3:]=="PDF":
				f_url = urllib.unquote(f_url)
				f_url.replace(' ', '\\ ')
				if os.path.exists(urllib.unquote(f_url))==True:
					shutil.copy(urllib.unquote(f_url), 'html/files/' + str(x[0]) + '.pdf')
					f.write(' [<a href=\"files/' + str(x[0]) + '.pdf\">PDF</a>]')
		cursor3.close()
		f.write("<br>\n")
	cursor.close()
	f.close()
	f = open('html/index_unordered.html', 'r')
	f1 = open('html/index.html', 'a')
	#From http://code.activestate.com/recipes/440612-sort-a-file/
	lines=[] # give lines variable a type of list
	for line in f:
		lines.append(line.rstrip())
	lines.sort()
	for line in lines:
		f1.write(line + "\n")
	time_now = time.strftime("%Y-%m-%d %H:%M:%S")
	f1.write('\n<br><br>Exported from Mendeley on: ' + time_now + '\n\n')
	f.close()
	f1.close()

   
#########################################################################
# EXECUTE THE SCRIPT							#
#########################################################################

print "\nFolders in Mendeley:\n"
getfolders()
folderID = raw_input('\n Type a folder ID to export: ')
export(folderID)

print "\nOK\n\n"
sys.exit(0)
