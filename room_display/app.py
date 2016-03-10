from flask import Flask
from flask import render_template
from flask.ext.heroku import Heroku
from flask.ext.script import Manager
from flask.ext.script import Server


##################################################
#                    Setup
##################################################

app = Flask(__name__)
app.debug = True
heroku = Heroku(app)


@app.route('/')
def hello_world():
    return render_template('index.html')


##################################################
#                    Main
##################################################

manager = Manager(app)
# Bind the dev server to 0.0.0.0 so it works through Docker
manager.add_command('runserver', Server(host='0.0.0.0'))

@manager.command
def production():
    """
    Run the server in production mode
    """
    # Turn off debug on live...
    app.debug = False

    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    manager.run()
