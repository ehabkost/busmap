here="$PWD"
for d in "$here/pkgs/site-packages/"*;do
	PYTHONPATH="$d:$PYTHONPATH"
done
PYTHONPATH="$here/python:$PYTHONPATH"
export PYTHONPATH
