#!/bin/sh
# Find actual path form which this script is launched
MY_PATH="`dirname \"$0\"`"
cd "$MY_PATH"

py3=$( which python3 )

if [ "$py3" != "" ] ; then
	# Temporary force python3
	#shopt -s expand_aliases
	alias python=$py3
fi

# Rewrite args
givenargs=""
for ARG in $*
do
        givenargs=${givenargs}" "$ARG
done

# Launch pyDarts with args
python ./pydarts.py $givenargs
