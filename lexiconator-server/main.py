import simplejson as json

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from wordnik import Wordnik
from pprint import pprint

class LexiQuery():
	def __init__(self):
		pass
	
	def queryWordInfo(self,word):
		"""Queries the wordnik database for the definition and usage of specified
		word and returns the result as a tuple pf the form: (definition, usage).
		
		Keyword Parameters:
		word -- word to query the wordnik database for
		"""
		word = word.rstrip()
		word = word.lstrip()
		w = Wordnik(api_key="<ENTER WORDNIK API KEY>")
		query_result = w.word_get_definitions(word,sourceDictionaries='wiktionary')
		
		definition = ""
		usage = ""		
		
		usage_counter = 1
		definition_counter = 1
		
		#Wiktionary API has a strange way of returning multiple results with the same content
		#So, we index each obtained result to make sure that there are no repetitions.
		prev_parsed_definitions = []
		prev_parsed_usage = []
		
		for each_entry in query_result:			
			if "text" in each_entry.keys():
				curr_definition = each_entry["text"]
				if curr_definition not in prev_parsed_definitions:				
					prev_parsed_definitions.append(curr_definition)
					definition = definition + str(definition_counter) + "." + curr_definition + "\n"
					definition_counter = definition_counter + 1			
			
			#For Usage examples from Websters
#			if "citations" in each_entry.keys():
#				usage_list = each_entry["citations"]					
#				for each_entry in usage_list:
#					if "cite" in each_entry.keys() and "source" in each_entry.keys():
#						usage = usage + each_entry["cite"] + "\n\t\t\t--" + each_entry["source"] + "\n"

			#Usage examples from Wiktionary	
			if "exampleUses" in each_entry.keys():
				usage_list = each_entry["exampleUses"]					
				for each_entry in usage_list:
					if "text" in each_entry.keys():
						curr_usage = each_entry["text"]
						if curr_usage not in prev_parsed_usage:
							prev_parsed_usage.append(curr_usage)
							usage = usage + str(usage_counter) + "." + curr_usage + "\n"
							usage_counter = usage_counter + 1
		
		return json.dumps((definition,usage),indent=4)


class MainPage(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        req_word = self.request.get('word')
        query_result = LexiQuery().queryWordInfo(req_word)
        self.response.out.write(query_result)

application = webapp.WSGIApplication(
                                     [('/', MainPage)],
                                     debug=True)
def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
