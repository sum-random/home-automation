#!/usr/bin/env python3

from flask import Flask, request, render_template
import sqlite3

app = Flask(__name__)


@app.route('/runsql/<whatpet>')
def runSql(whatpet='Cat',methods=['GET','POST']):
  retval = ""
  try:
    con = sqlite3.connect('/usr/local/www/apache24/cgi-data/test.db')
    cur = con.cursor()
    cur.executescript("DROP TABLE IF EXISTS Pets; CREATE TABLE Pets(Id INT, Name TEXT, Price INT);INSERT INTO Pets VALUES(1,'Cat', 400);INSERT INTO Pets VALUES(2,'Dog', 600);INSERT INTO Pets VALUES(3,'Iguana', 1200);")

    newpets = ((4, 'Bird',60),
                (5,'Goat',500))


    cur.executemany("INSERT INTO Pets VALUES(?,?,?)",newpets)

    con.commit()

    if whatpet:
      cur.execute("SELECT * FROM Pets where Name = '{}'".format(whatpet))
    else:
      cur.execute("SELECT * FROM Pets")

    for therow in cur.fetchall():
      for thefield in therow:
        retval = retval + "thefield: {}\n".format(thefield)
  
  except:
    if con:
      con.rollback()
  finally:
    if con:
      con.close
  retval = retval + " Method used: {}".format(request.method)
  return retval


@app.route('/')
def index():
  return render_template("petlist.html",guts = runSql(None))

if __name__ == "__main__":
  app.run(debug=True)
