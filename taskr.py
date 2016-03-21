import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from contextlib import closing

DATABASE = '/tmp/taskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
  return sqlite3.connect(app.config['DATABASE'])

def init_db():
  with closing(connect_db()) as db:
    with app.open_resource('schema.sql', mode='r') as f:
      db.cursor().executescript(f.read())
    db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route('/')
def show_list():
  cur = g.db.execute('select description, complete, id from tasks order by id asc')
  tasks = [{"description" : row[0], "complete" : row[1], "id" : row[2]} for row in cur.fetchall()]
  return render_template('show_list.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add_task():
  if not session.get('logged_in'):
    abort(401)
  g.db.execute('insert into tasks (description, complete) values (?, ?)', [request.form['description'], False])
  g.db.commit()
  flash('New task was successfully added')
  return redirect(url_for('show_list'))

@app.route('/delete/<taskID>', methods=['POST'])
def delete_task(taskID):
  if not session.get('logged_in'):
    abort(401)
  g.db.execute('delete from tasks where id = ?', taskID)
  g.db.commit()
  flash('Task was successfully deleted')
  return redirect(url_for('show_list'))

@app.route('/complete/<taskID>', methods=['POST'])
def complete_task(taskID):
  if not session.get('logged_in'):
    abort(401)
  g.db.execute('update tasks set complete= 1 where id = ?', taskID)
  g.db.commit()
  flash('Task completed! Great job!')
  return redirect(url_for('show_list'))

@app.route('/edit/<taskID>', methods=['POST'])
def edit_task(taskID):
  if not session.get('logged_in'):
    abort(401)
  find_task = g.db.execute('select description, complete, id from tasks where id = ?', taskID)
  for row in find_task:
    task = {"description" : row[0], "complete" : row[1], "id" : row[2]}
  return render_template('edit.html', task=task)

@app.route('/update/<taskID>', methods=['POST'])
def update_task(taskID):
  print request.form['new_description']
  g.db.execute('update tasks set description= ? where id = ?', [request.form['new_description'], taskID])
  g.db.commit()
  flash('You have successfully updated that task!')
  return redirect(url_for('show_list'))

@app.route('/login', methods=['GET', 'POST'])
def login():
  error = None
  if request.method == 'POST':
    if request.form['username'] != app.config['USERNAME']:
      error = 'Invalid username'
    elif request.form['password'] != app.config['PASSWORD']:
      error = 'Invalid password'
    else:
      session['logged_in'] = True
      flash('You were logged in')
      return redirect(url_for('show_list'))
  return render_template('login.html', error=error)

@app.route('/logout')
def logout():
  session.pop('logged_in', None)
  flash('You were logged out')
  return redirect(url_for('show_list'))

if __name__ == '__main__':
  init_db()
  app.run()

# @app.route('/tasks/<int:id>/edit', methods=['GET'])
# def edit_description(id):
#   if not session.get('logged_in'):
#     abort(401)
#   g.db.execute('update tasks (description) values (?) where id=id', [request.form['description']])
#   g.db.commit()
#   flash('Task description was successfully updated')
#   return redirect(url_for('show_list'))