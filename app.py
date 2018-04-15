#! /usr/bin/python3.5
# -*- coding:utf-8 -*-

from flask import Flask
from flask import render_template
from flask import request
from flask import g
from flask import session
from flask import redirect 
from flask import url_for
from flask import redirect
from flask import abort
from hashlib import md5

import os
import mysql.connector 

app = Flask(__name__)
app.config.from_object('config')
app.config.from_object('secret_config')

def connect_db () :
    g.mysql_connection = mysql.connector.connect(
        host = app.config['DATABASE_HOST'],
        user = app.config['DATABASE_USER'],
        password = app.config['DATABASE_PASSWORD'],
        database = app.config['DATABASE_NAME']	
    )   

    g.mysql_cursor = g.mysql_connection.cursor()
    return g.mysql_cursor

def get_db () :
    if not hasattr(g, 'db') :
        g.db = connect_db()
    return g.db

@app.teardown_appcontext
def close_db (error) :
    if hasattr(g, 'db') :
        g.db.close()


@app.route('/')
def index () :
    return redirect('monitoring')


@app.route('/monitoring/')
def monitoring () :
	db = get_db()
	db.execute('SELECT id, website FROM cards')
	cards = db.fetchall()
	return render_template('monitoring.html', cards = cards)


@app.route('/delete/<id>/', methods=['POST'])
def delete_card (id) :
	db = get_db()
	db.execute('delete from cards where id = '+id)
	g.mysql_connection.commit()
	return redirect('monitoring')

@app.route('/add/')
def add () : 
	if not session.get('logged_in'):
		return render_template('login.html')
	else:
		return render_template(ajout.html)

@app.route('/ajout/', methods=['GET', 'POST'])
def ajout_site () :
	if 'username' in session:
		unsername_session = escape(session['username']).capitalize()
		Website = request.form.get('urlsite')
		db = get_db()
		db.execute('insert into cards(website) values(%s)', (Website))
		g.mysql_connection.commit()
		return redirect ('monitoring')
	else: 
		return redirect('login')

@app.route('/gerer/')
def gerer () :
	if 'username' in session:
		username_session = escape(session['username']).capitalize()
		db = get_db()
		db.execute('SELECT id, website FROM cards')
		cards = db.fetchall()
		return render_template('gerer.html', cards = cards)
	else:
		return redirect('login')


@app.route('/login/', methods=['GET', 'POST'])
def login():
    error = None
    if 'username' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username_form  = request.form['username']
        password_form  = request.form['password']
        db = get_db()
        db.execute("SELECT COUNT(1) FROM users WHERE name = %s;", [username_form]) # CHECKS IF USERNAME EXSIST
        if db.fetchone()[0]:
            db.execute("SELECT pass FROM users WHERE name = %s;", [username_form]) # FETCH THE HASHED PASSWORD
            for row in db.fetchall():
                if md5(password_form).hexdigest() == row[0]:
                    session['username'] = request.form['username']
                    return redirect(url_for('index'))
                else:
                    error = "Invalid Credential"
        else:
            error = "Invalid Credential"
    return render_template('login.html', error=error)


@app.route('/logout/')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')