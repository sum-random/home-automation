#!/usr/local/bin/python

import os
import cgi

def varlist():
  "returns a list of envienronment variable names"
  for envvar in sorted(os.environ):
    yield envvar

print("Content-type: text/html; charset=iso-8859-1\n")

print('<html><head><title>Python test script</title></head>')
print('<body>')
for envvar in varlist():
  print('<div style="color:red;"><span style="color:blue;">%s</span> = <span style="color:green;">%s</span></div>' %(envvar,os.environ[envvar]))

print('<div style="color:#224466;"><span>Form variables:</span>')
form = cgi.FieldStorage()
#print(form)
formkeys = form.keys()
#print(formkeys)
print('<form method="post">')
for formvar in formkeys:
  #print(formvar)
  print('<div style="color:red;"><span style="color:blue;">%s</span> = <span style="color:green;">%s</span></div>' %(formvar,form.getvalue(formvar)))
  print('<div style="color:black;"><span><input type="text" name="%s" value="%s" onChange="submit();"></span></div>' %(formvar,form.getvalue(formvar)))

print('</form>')

print('</div>')

print('</body>')
