import sys

if sys.version_info[0] <= 2:
	import httplib2_python2
	sys.modules[__name__] = sys.modules['httplib2_python2']
else:
	import httplib2_python3
	sys.modules[__name__] = sys.modules['httplib2_python3']
