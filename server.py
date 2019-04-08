#!/usr/bin/env python2.7

"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver

To run locally:

    python server.py

Go to http://localhost:8111 in your browser.

A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@104.196.18.7/w4111
#
# For example, if you had username biliris and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://biliris:foobar@104.196.18.7/w4111"
#
DATABASEURI = "postgresql://jk4249:junghu23@34.73.21.127/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
'''
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")
print("Success");
'''
@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """


  
  # DEBUG: this is debugging code to see what request looks like
  print request.args


  #
  # example of a database query
  #
  cursor = g.conn.execute("SELECT lid, languagename FROM language")
  cursor2 = g.conn.execute("SELECT pc_id, title FROM production_company")
  res = cursor.fetchall();
  res2 = cursor2.fetchall();
  cursor.close()
  cursor2.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html", result = [res,res2])






#
# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#
@app.route('/another')
def another():
  return render_template("another.html")

@app.route('/list', methods=['GET'])
def list():
  name = request.args.get('name', None)
  if(name != None):
    cursor = g.conn.execute('SELECT P.*, R.title FROM Production P, has_Role H, Role R WHERE H.rid=%s and H.pid=P.pid AND R.rid=H.rid', name)
  else:
    cursor = g.conn.execute('SELECT mid, title, release_date FROM movie')

  res = []
  for r in cursor:
    res.append(r)
  cursor.close()
  if(name!=None):
    return render_template('list.html', result = res)
  else:
    return render_template('list2.html', result = res)


@app.route('/search', methods=['GET'])
def search():
  name = request.args.get('name', None)
  cursor = g.conn.execute('SELECT mid, release_date FROM movie WHERE title=%s', name)
  
  res = []
  for r in cursor:
    res.append(r)  # can also be accessed using result[0]
  cursor.close()
  return render_template('results.html', result = res)

@app.route('/searchprod', methods=['GET'])
def searchprod():
  name = request.args.get('name', None)
  cursor = g.conn.execute('SELECT P.*, R.title FROM Production P, has_Role H, Role R WHERE P.name=%s and H.pid=P.pid AND R.rid=H.rid', name)
  
  res = []
  for r in cursor:
    res.append(r)  # can also be accessed using result[0]
  cursor.close()
  return render_template('resultprods.html', result = res)


@app.route('/company', methods=['GET'])
def company():
  pcid = request.args.get('name', None)
  cursor = g.conn.execute('SELECT * FROM production_company WHERE pc_id=%s', pcid)
  cursor2 = g.conn.execute('SELECT P.pid, P.name, W.since FROM Production P, works_for W, Production_company PC, has_role H WHERE PC.pc_id=W.pc_id and W.pid=P.pid AND H.pid=P.pid and H.rid = 0 and PC.pc_id=%s', pcid)
  cursor3 = g.conn.execute('SELECT P.pid, P.name, W.since FROM Production P, works_for W, Production_company PC, has_role H WHERE PC.pc_id=W.pc_id and W.pid=P.pid AND H.pid=P.pid and H.rid = 1 and PC.pc_id=%s', pcid)
  cursor4 = g.conn.execute('SELECT P.pid, P.name, W.since FROM Production P, works_for W, Production_company PC, has_role H WHERE PC.pc_id=W.pc_id and W.pid=P.pid AND H.pid=P.pid and H.rid = 2 and PC.pc_id=%s', pcid)
  cursor5 = g.conn.execute('SELECT M.mid, M.title FROM Movie M, produces P WHERE M.mid=P.mid and P.pc_id=%s', pcid)
  res = cursor.fetchall()
  res2 = cursor2.fetchall()
  res3 = cursor3.fetchall()
  res4 = cursor4.fetchall()
  res5 = cursor5.fetchall()
  cursor.close()
  cursor2.close()
  cursor3.close()
  cursor4.close()
  cursor5.close()
  return render_template('company.html', result = [res,res2,res3,res4,res5])


@app.route('/language', methods=['GET'])
def language():
  lid = request.args.get('name', None)
  cursor = g.conn.execute('SELECT languagename FROM language WHERE lid=%s', lid)
  cursor2 = g.conn.execute('SELECT P.pid, P.name FROM Production P, speaks S, has_role H WHERE S.pid=P.pid and H.pid=P.pid AND H.rid = 0 and S.lid=%s', lid)
  cursor3 = g.conn.execute('SELECT P.pid, P.name FROM Production P, speaks S, has_role H WHERE S.pid=P.pid and H.pid=P.pid AND H.rid = 1 and S.lid=%s', lid)
  cursor4 = g.conn.execute('SELECT P.pid, P.name FROM Production P, speaks S, has_role H WHERE S.pid=P.pid and H.pid=P.pid AND H.rid = 2 and S.lid=%s', lid)
  cursor5 = g.conn.execute('SELECT M.mid, M.title FROM Movie M, use_lang U WHERE M.mid=U.mid and U.lid=%s', lid)
  res = cursor.fetchall()
  res2 = cursor2.fetchall()
  res3 = cursor3.fetchall()
  res4 = cursor4.fetchall()
  res5 = cursor5.fetchall()
  cursor.close()
  cursor2.close()
  cursor3.close()
  cursor4.close()
  cursor5.close()
  return render_template('language.html', result = [res,res2,res3,res4,res5])

@app.route('/title', methods=['GET'])
def title():
  mid = request.args.get('name', None)
  cursor = g.conn.execute('SELECT * FROM movie WHERE mid=%s', mid)
  cursor2 = g.conn.execute('SELECT P.* FROM makes A, Production P, has_role H WHERE P.pid=A.pid AND H.pid=P.pid AND H.rid=0 and A.mid=%s', mid)
  cursor3 = g.conn.execute('SELECT P.* FROM makes A, Production P, has_role H WHERE P.pid=A.pid AND H.pid=P.pid AND H.rid=1 and A.mid=%s', mid)
  cursor4 = g.conn.execute('SELECT P.* FROM makes A, Production P, has_role H WHERE P.pid=A.pid AND H.pid=P.pid AND H.rid=2 and A.mid=%s', mid)
  cursor5 = g.conn.execute('SELECT L.* FROM language L, use_lang U WHERE L.lid=U.lid AND U.mid=%s',mid)
  cursor6 = g.conn.execute('SELECT PC.pc_id, PC.title FROM production_company PC, produces P WHERE PC.pc_id=P.pc_id AND P.mid=%s',mid)
  res = cursor.fetchall()
  res2 = cursor2.fetchall()
  res3 = cursor3.fetchall()
  res4 = cursor4.fetchall()
  res5 = cursor5.fetchall()
  res6 = cursor6.fetchall()
  cursor.close()
  cursor2.close()
  cursor3.close()
  cursor4.close()
  cursor5.close()
  cursor6.close()
  return render_template('title.html', result = [res,res2,res3,res4,res5,res6])

@app.route('/production', methods=['GET'])
def production():
  pid = request.args.get('name', None)
  cursor = g.conn.execute('SELECT P.*, R.title FROM Production P, has_Role H, Role R WHERE P.pid=%s and H.pid=P.pid AND R.rid=H.rid', pid)
  cursor2 = g.conn.execute('SELECT M.title, E.mid FROM Movie M, makes E, Production P WHERE P.pid=%s and E.pid=P.pid AND M.mid=E.mid', pid)
  cursor3 = g.conn.execute('SELECT L.* FROM language L, speaks S WHERE L.lid=S.lid AND S.pid=%s',pid)
  cursor4 = g.conn.execute('SELECT PC.pc_id, PC.title, P.since FROM production_company PC, works_for P WHERE PC.pc_id=P.pc_id AND P.pid=%s',pid)
  res = cursor.fetchall()
  res2 = cursor2.fetchall()
  res3 = cursor3.fetchall()
  res4 = cursor4.fetchall()
  cursor.close()
  cursor2.close()
  cursor3.close()
  cursor4.close()
  return render_template('production.html', result = [res,res2,res3,res4])


# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  g.conn.execute('INSERT INTO test(name) VALUES (%s)', name)
  return redirect('/')

@app.route('/delete', methods=['POST'])
def delete():
  name = request.form['name']
  g.conn.execute('DELETE FROM test WHERE name=%s', name)
  return redirect('/')


@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python server.py

    Show the help text using:

        python server.py --help

    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
