import os
import sys

from subprocess import Popen, PIPE
from time import sleep
import webbrowser

HELP = """
Run webserver in directory "site"

Usage:

python3 serve.py
"""

os.chdir("site")


command = sys.argv[1] if len(sys.argv) > 1 else "start"

if command == "start":
    server = Popen(["python3", "-m", "http.server"], stdout=PIPE, bufsize=1, encoding="utf-8")
    sleep(1)
    webbrowser.open("http://localhost:8000", new=2, autoraise=True)
    stopped = server.poll()
    if not stopped:
        try:
            sys.stdout.write("Press <Ctrl+C> to stop the TF browser\n")
            if server:
                for line in server.stdout:
                    sys.stdout.write(line)
        except KeyboardInterrupt:
            sys.stdout.write("\n")
            if server:
                server.terminate()
                sys.stdout.write("Http server has stopped\n")

elif command == "stop":
    pass
else:
    print(HELP)
