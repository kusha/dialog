#!/bin/sh

command -v link-parser >/dev/null 2>&1 || { sudo apt-get install link-parser; echo "installing link-parser"; }

if [ -d .git ]; then
  echo "we are already inside git repo";
else
  git clone https://github.com/kusha/dialog.git;
fi;


while true; 

	LOCAL=$(git rev-parse @{0})
	REMOTE=$(git rev-parse @{u})
	BASE=$(git merge-base @ @{u})

	if [ $LOCAL = $REMOTE ]; then
	    echo "Up-to-date"
	elif [ $LOCAL = $BASE ]; then
		git pull origin
		echo "restarting server"
	    killall python;
	    python3 server.py &
	fi;

	sleep 1h; 
done;