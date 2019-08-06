import sys

if sys.version_info[0] <= 2:
	from httplib2_python2 import socks
	sys.modules[__name__] = sys.modules['httplib2_python2.socks']
else:
	from httplib2_python3 import socks
	sys.modules[__name__] = sys.modules['httplib2_python3.socks']
