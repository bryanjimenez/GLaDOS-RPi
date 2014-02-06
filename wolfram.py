#!/usr/bin/python

from xml.dom import minidom
import urllib2
import ConfigParser

config = ConfigParser.ConfigParser()
config.read('default.cfg')

URL_WOLF= config.get('Wolfram', 'url')

non_ascii_chars = {
'\n':' ',
u'\xb0F': "degrees Fahrenheit",
u'\xd7': "*",
'  ':' ',
'+':'plus',
'|':'',
'(':'',
')':'',
"'":''
}

def multipleReplace(text, wordDict):
    for key in wordDict:
        text = text.replace(key, wordDict[key])
    return text

#-------------------------------------------------------------------------------------------------------------------------------
# Sends query to wolfram alpha for response. Response is cleaned up 
# (some special characters replaced) and returned
#
def wolfram(query):
	try:
		u = urllib2.urlopen(URL_WOLF + urllib2.quote(query))

		xmldoc = minidom.parse(u)

		itemlist = xmldoc.getElementsByTagName('plaintext') 
		podlist = xmldoc.getElementsByTagName('pod') 


	# if only one pod return its result
		if(len(podlist)==1):
			response = itemlist[0].firstChild.data
	# if more than one then ..
		elif(len(podlist)>=2):
			# check if the first one contains 'input' in the title.. skip
			if "Input" not in podlist[0].getAttribute('title'):
				response = itemlist[0].firstChild.data
			else:
				response = itemlist[1].firstChild.data
		# if no pods then say not sure
		else:
			response = "I am not sure"
	except Exception,e:
		print "wolfram() failed",e

	return multipleReplace(response,non_ascii_chars)
