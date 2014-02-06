#!/usr/bin/python
from GLaDOS.py import respond

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

patterns = {
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
