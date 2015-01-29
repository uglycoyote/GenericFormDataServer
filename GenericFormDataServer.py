#!/usr/bin/python

#
# Generic Form Data server for python 2.x
# by Mike Cline
#
# extremely simple HTTP server supporting the following queries:
#
# POST /post 
#    post form data.  Dictionary of key-value pairs from form data will be added to local data store
#
# GET /data   
#    returns the saved data as json, as a list of dictionaries of posted form data
#
# POST /remove
#     removes any posts matching the query, e.g., if you post ID=938593 to /remove, it will remove
#     any items from the data store where ID=938593.  If you post multiple key-value pairs, then
#     it will only remove the elements which match all of the values.
#
#
#  also serves files from the running directory
#


from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import os
import cgi
import json
import pickle

PORT_NUMBER = 8080

mimetypes = {}
mimetypes[".html"] = "text/html"
mimetypes[".jpg"] = "image/jpg"
mimetypes[".gif"] = "text/gif"
mimetypes[".js"] = "application/javascript"
mimetypes[".css"] = "text/css"

# All form data will be stored in here.
storedData = []

stateFile = "state.pickle"

def saveState():
	global storedData
	f = open(stateFile, "w")
	pickle.dump(storedData,f)
	f.close()

def loadState():
	global storedData
	if os.path.exists(stateFile):
		f = open(stateFile, "r")
		storedData = pickle.load(f)
		f.close()
		print ( "loaded " + str(storedData) )

loadState()

class myHandler(BaseHTTPRequestHandler):
	

	def setStoredData(self, data):
		global storedData
		print ( "setting data:  " + str(data) )
		storedData = data
		saveState()

	def getStoredData(self):
		global storedData
		return storedData

	def do_GET(self):
		if ( self.path == "/data" ):
			self.sendStoredDataAsJson()
			return

		self.serveFile()

	def sendStoredDataAsJson(self):
			self.send_response(200)
			self.send_header('Content-type','application/json')
			self.end_headers()
			jsonOutput = json.dumps(self.getStoredData(), indent=4)
			#print( jsonOutput )
			self.wfile.write(jsonOutput)

	def do_POST(self):
		form = cgi.FieldStorage(
			fp=self.rfile, 
			headers=self.headers,
			environ={'REQUEST_METHOD':'POST',
	                 'CONTENT_TYPE':self.headers['Content-Type'],
		})

		if self.path=="/post":

			formData = { key : form[key].value for key in form }
			data = self.getStoredData()
			data.append(formData)
			self.setStoredData(data)

			self.sendStoredDataAsJson()

			return			

		if self.path=="/remove":

			formData = { key : form[key].value for key in form }

			# We should remove a data element if it matches all of the key-value pairs
			#  in the formData
			def shouldRemove( storedFormData ):
				return all ( (key in storedFormData and storedFormData[key]==formData[key]) for key in formData ) 			

			oldData = self.getStoredData()
			newData = filter( lambda x: not shouldRemove(x), oldData )

			self.setStoredData(list(newData))

			self.sendStoredDataAsJson()
			return			

	# File-serving subroutine called under do_GET
	def serveFile(self):
		if self.path=="/":
			self.path="/index.html"

		try:
			sendReply = False

			# if the requested path has one of the known file extensions, set the mime type 
			#   of the response.
			matchingExtensions = [ x for x in mimetypes if self.path.endswith(x) ]
			if matchingExtensions:
				extension = matchingExtensions[0]
				mimetype = mimetypes[extension]
				sendReply = True

			if sendReply == True:
				#Open the static file requested and send it
				f = open(os.curdir + os.sep + self.path) 
				self.send_response(200)
				self.send_header('Content-type',mimetype)
				self.end_headers()
				self.wfile.write(f.read())
				f.close()
			return

		except IOError:
			self.send_error(404,'File Not Found: %s' % self.path)
			
try:
	#Create a web server and define the handler to manage the
	#incoming request
	server = HTTPServer(('', PORT_NUMBER), myHandler)
	print ('Started httpserver on port ' , PORT_NUMBER)
	
	#Wait forever for incoming htto requests
	server.serve_forever()

except KeyboardInterrupt:
	print ('^C received, shutting down the web server')
	server.socket.close()
	
