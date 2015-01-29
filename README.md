# GenericFormDataServer

Generic Form Data server for python 2.x
by Mike Cline

extremely simple HTTP server supporting the following queries:

**POST /post**

post form data.  Dictionary of key-value pairs from form data will be added to local data store

**GET /data**

returns the saved data as json, as a list of dictionaries of posted form data

**POST /remove**


removes any posts matching the query, e.g., if you post ID=938593 to /remove, it will remove
any items from the data store where ID=938593.  If you post multiple key-value pairs, then
it will only remove the elements which match all of the values.

also serves files from the running directory

# index.html

Sample html form for use with GenericFormDataServer.py

# dynamic.html

Sample html and javascript for single-page web app talking to GenericFormDataServer via ajax get/post requests.  Displays notes as grey bubbles.
