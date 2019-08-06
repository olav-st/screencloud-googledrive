import sys

if sys.version_info[0] <= 2:
	from httplib2_python2 import certs
	sys.modules[__name__] = sys.modules['httplib2_python2.certs']
else:
	from httplib2_python3 import certs
	sys.modules[__name__] = sys.modules['httplib2_python3.certs']
