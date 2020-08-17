from flask_script import Server
from application import app, manager
import os


import www
## web server

# Bind to a port, could solve heroku bind error
port = int(os.environ.get('PORT', 5000))
manager.add_command( "runserver", Server( host='0.0.0.0',port=port,use_debugger = True ,use_reloader = True, threaded=True) )


def main():
    manager.run()

if __name__ == '__main__':
    try:
        import sys
        sys.exit( main() )
    except Exception as e:
        import traceback
        traceback.print_exc()
