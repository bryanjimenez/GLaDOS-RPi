#!/usr/bin/python

import RPi.GPIO as GPIO  
import urllib2
import json
from xml.dom import minidom
import sys, os
from time import sleep
import ConfigParser
import re
from functions import * 
from wolfram import *


QUERY_FILE="query.flac"
RESPONSE_FILE="response.mpeg"

config = ConfigParser.ConfigParser()
config.read('default.cfg')
URL_V2T= config.get('Google', 'url_voice2text')
URL_T2V= config.get('Google', 'url_text2voice')


cmds = ConfigParser.RawConfigParser()
cmds.read('commands.cfg')

know = ConfigParser.RawConfigParser()
know.read('knowledge.cfg')


knowledge = {}
commands = {}



#-------------------------------------------------------------------------------------------------------------------------------	
def affirm(phrase):

	try:
		respond("Did you say, " + phrase + "?")
		message = record()
		
		req = urllib2.Request(url=URL_V2T, data=message, headers={"Content-type": "audio/x-flac; rate=8000"})
		u = urllib2.urlopen(req)
		data = json.load(u)

		if len(data["hypotheses"])>0:
			phrase = data["hypotheses"][0]["utterance"]
			certainty = data["hypotheses"][0]["confidence"]
			print 'You: "' + phrase +'"'
			if phrase=="yes":
				return True
	except Exception,e:
		print "affirm() failed",e

	return False

#-------------------------------------------------------------------------------------------------------------------------------	
def listen():
	try:
		message = record()

		req = urllib2.Request(url=URL_V2T, data=message, headers={"Content-type": "audio/x-flac; rate=8000"})
		u = urllib2.urlopen(req)
		data = json.load(u)


		if len(data["hypotheses"])>0:
			phrase = data["hypotheses"][0]["utterance"]
			certainty = data["hypotheses"][0]["confidence"]
			print
			print "You: " +'"' + phrase	+ '"'
			return (phrase, certainty)	
		else:
			respond ("Could you say that again?")
			return None
	except Exception,e:
		print "listen() failed: ",e
		return None

#-------------------------------------------------------------------------------------------------------------------------------	
def respond(results,lang='en'):
	try:
		
		if results:
			if lang=='en':
				print 'GLaDOS: "' + results + '"'
			else:
				print 'Translator: "' + results + '"'



			headers = { 'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.77 Safari/537.36'}

			phrase = ''
			words = results.split(' ')
			# google only accepts 100 chars for text to voice		
			for i in range(0, len(words)):
				if(len(phrase + ' ' + words[i]) <100):
					phrase += ' ' + words[i]
				else:
					URL_VOICE='http://translate.google.com/translate_tts?tl='+lang+'&q=' + urllib2.quote(phrase)
					req = urllib2.Request(URL_VOICE,None,headers)
					u = urllib2.urlopen(req)

					with open(RESPONSE_FILE, 'wb') as response:
						response.write(u.read())
					os.system('mplayer -ao alsa -really-quiet -noconsolecontrols ' + RESPONSE_FILE)

					phrase = words[i]

			
			# NOTE request string has max len of 100 chars!
			URL_VOICE='http://translate.google.com/translate_tts?tl='+lang+'&q=' + urllib2.quote(phrase)
			req = urllib2.Request(URL_VOICE,None,headers)
			u = urllib2.urlopen(req)

			with open(RESPONSE_FILE, 'wb') as response:
				response.write(u.read())

			os.system('mplayer -ao alsa -really-quiet -noconsolecontrols ' + RESPONSE_FILE)
	except Exception,e:
		print "respond() failed: ",e	

#-------------------------------------------------------------------------------------------------------------------------------	
def command(phrase):
	os.system(commands[phrase])
	return "Command '" + phrase + "' was executed"
	
#-------------------------------------------------------------------------------------------------------------------------------
def record():
	try:
		os.system("rm "+QUERY_FILE +" 2>/dev/null")
		
		os.system("aplay sounds/begin.wav 2>/dev/null")	

		if (os.system("arecord -Dplughw:`arecord -l | grep -o ': [a-zA-Z0-9]* \[' | grep -o '[a-zA-Z0-9]*'` -f cd -d 5 -c 1 -r 8000 -t wav - 2>/dev/null | flac -0 - --sample-rate=8000 --channels=1 -o " + QUERY_FILE + " 2>/dev/null") !=0):
			raise Exception("Cannot record, check microphone")

		os.system("aplay sounds/end.wav 2>/dev/null")	

		f = open(QUERY_FILE)
		message = f.read()
		f.close()

	except Exception,e:
		print "record() failed", e

	return message
#-------------------------------------------------------------------------------------------------------------------------------
def load_knowledge():
	knowledge.clear()
	k=know.items('Questions')
	for line in k:
		(q, a) = line
		knowledge[q] = a

def load_commands():
	commands.clear()
	c=cmds.items('Commands')
	for cmd in c:
		(q, a) = cmd
		commands[q] = a

#-------------------------------------------------------------------------------------------------------------------------------
def dialogue():
	try:
		(phrase, certainty) = listen()
	except Exception,e:
		print 'try again...'
		return None
		
	results=''

	for pattern in functions:
		if re.match(r'%s' % pattern,phrase):
			results = functions[pattern](phrase)
			respond(results)
			return results

	for pattern in commands:
		if re.match(r'%s.*' % pattern,phrase):
#		if phrase in commands:
			results = command(pattern)
#			results = command(phrase)
			respond(results)
			return results		
		
	if certainty >= .70:
		if phrase in knowledge:
			results = remember(phrase)
		else:
			results = wolfram(phrase)
	else:
		if affirm(phrase)==True:
			if phrase in knowledge:
				results = remember(phrase)
			else:
				results = wolfram(phrase)
		
	respond(results)
	return results
#-------------------------------------------------------------------------------------------------------------------------------
# function retrieves from knowledge the response to the memorized phrase
# removes the newline at the end of the line
def remember(phrase):
	return knowledge[phrase].replace("\n","");


#
# FUNCTIONS
#-------------------------------------------------------------------------------------------------------------------------------
def memorize(phrase):

	try:
		if re.match(r'(memorize .*)',phrase):
			question = ' '.join(phrase.split(' ')[1:])
		else:
			respond("What question would you like me to remember?")
			(question, certainty) = listen()

		if (question != 'nevermind' and question !='forget it'):
			respond("How would you like me to respond to " + question)
			(answer, certainty) = listen()

			know.set('Questions',question,answer)
	
			with open('knowledge.cfg', 'wb') as configfile:
				know.write(configfile)
	
			load_knowledge()
	except Exception,e:
		print "memorize() failed",e
		
	return "Got it"
#-------------------------------------------------------------------------------------------------------------------------------
def reminder(phrase):
	print "not implemented"
	

#-------------------------------------------------------------------------------------------------------------------------------
def jokes(phrase):
	try:
		respond("Who's there?")
		(knocker, certainty) = listen()
	
		respond(knocker + " Who?")
		(answer, certainty) = listen()
	except Exception,e:
		print "jokes() failed",e

	return "HA HA HA! That was a good joke!"

#-------------------------------------------------------------------------------------------------------------------------------	
def terminate(phrase):
	respond("See you soon!")
	os.system("aplay sounds/powerdown.wav 2>/dev/null")
	GPIO.cleanup()	
	sys.exit(0)


#-------------------------------------------------------------------------------------------------------------------------------	
def translate(command):
        try:
		
		if re.match(r'(how do you say)',command):
			phrase = ' '.join(command.split(' ')[4:-2])
		else:	
			phrase = ' '.join(command.split(' ')[1:-2])
		
		language = command.split(' ')[-1]				

		languages = {
			'Afrikaans' : 'af',
			'Albanian' : 'sq',
			'Arabic' : 'ar',
			'Azerbaijani' : 'az',
			'Basque' : 'eu',
			'Bengali' : 'bn',
			'Belarusian' : 'be',
			'Bulgarian' : 'bg',
			'Catalan' : 'ca',
			'Chinese' : 'zh-CN',
			'Chinese Simplified' : 'zh-CN',
			'Chinese Traditional' : 'zh-TW',
			'Croatian' : 'hr',
			'Czech' : 'cs',
			'Danish' : 'da',
			'Dutch' : 'nl',
			'English' : 'en',
			'Esperanto' : 'eo',
			'Estonian' : 'et',
			'Filipino' : 'tl',
			'Finnish' : 'fi',
			'French' : 'fr',
			'Galician' : 'gl',
			'Georgian' : 'ka',
			'German' : 'de',
			'Greek' : 'el',
			'Gujarati' : 'gu',
			'Haitian' : 'ht',
			'Creole' : 'ht',
			'Hebrew' : 'iw',
			'Hindi' : 'hi',
			'Hungarian' : 'hu',
			'Icelandic' : 'is',
			'Indonesian' : 'id',
			'Irish' : 'ga',
			'Italian' : 'it',
			'Japanese' : 'ja',
			'Kannada' : 'kn',
			'Korean' : 'ko',
			'Latin' : 'la',
			'Latvian' : 'lv',
			'Lithuanian' : 'lt',
			'Macedonian' : 'mk',
			'Malay' : 'ms',
			'Maltese' : 'mt',
			'Norwegian' : 'no',
			'Persian' : 'fa',
			'Polish' : 'pl',
			'Portuguese' : 'pt',
			'Romanian' : 'ro',
			'Russian' : 'ru',
			'Serbian' : 'sr',
			'Slovak' : 'sk',
			'Slovenian' : 'sl',
			'Spanish' : 'es',
			'Swahili' : 'sw',
			'Swedish' : 'sv',
			'Tamil' : 'ta',
			'Telugu' : 'te',
			'Thai' : 'th',
			'Turkish' : 'tr',
			'Ukrainian' : 'uk',
			'Urdu' : 'ur',
			'Vietnamese' : 'vi',
			'Welsh' : 'cy',
			'Yiddish' : 'yi'
		}


		fromLang="en"
		toLang= languages[language]


		URL_TRANS = "http://translate.google.com/translate_a/t?client=t&hl="+fromLang+"&tl="+toLang+"&text=" + urllib2.quote(phrase)


		headers = { 'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.77 Safari/537.36'}
		req = urllib2.Request(URL_TRANS,None,headers)
		u = urllib2.urlopen(req)

		result= u.read().split(',')[0][4:-1]
		respond(result,toLang)

	except Exception,e:
		print "translate() failed", e

#-------------------------------------------------------------------------------------------------------------------------------	
def sayAgain(phrase):
	os.system('mplayer -ao alsa -really-quiet -noconsolecontrols '+ RESPONSE_FILE)

#-------------------------------------------------------------------------------------------------------------------------------	
def countdown(phrase):
	respond("9, 8, 7, 6, 5, 4, 3, 2, 1, Blast off!")

functions = {
'(memorize)': memorize,
'(memorize .*)': memorize,
'(remember)': memorize,

# Not implemented
#'(remind me)':reminder,

'(knock knock)': jokes,

'(goodbye)': terminate,
'(shut down)': terminate,
'(quit)': terminate,

'(translate)': translate,
'(say .* in .*)': translate,
'(how do you say .* in .*)': translate,

'(repeat)': sayAgain,
'(say again)': sayAgain,
'(could you say that again)': sayAgain,

'(countdown)': countdown

}


	
#print "!"+ sys.argv[1]+"!"

print ''	
os.system("aplay sounds/powerup.wav 2>/dev/null")
  
GPIO.setmode(GPIO.BOARD)
GPIO.setup(3,GPIO.IN)

load_knowledge()
load_commands()

sleep(1)

while True:
	if not GPIO.input(3):  
		dialogue()
