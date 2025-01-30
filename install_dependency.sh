#!/bin/bash
if [ -z "$1" ]; then
	echo "Usage: ./install_dependency.sh <package-name>"
	exit 1
fi

PACKAGE=$1

echo "Installing $PACKAGE to discord_bot/vendor/"
pip3 install $PACKAGE --target discord_bot/vendor/ --upgrade

echo "Updating requirements.txt"
if ! grep -q "^$PACKAGE" discord_bot/requirements.txt; then
	echo "$PACKAGE" >> discord_bot/requirements.txt
fi

echo "Done!"
