from ordermenu import app
import sys, os
from flask_debugtoolbar import DebugToolbarExtension

sys.path.append(os.getcwd())

app.debug = True
toolbar = DebugToolbarExtension(app)

if __name__ == '__main__':
    app.run(debug=True)
