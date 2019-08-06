import sys

if sys.version_info[0] <= 2:
	from httplib2_python2 import iri2uri
	sys.modules[__name__] = sys.modules['httplib2_python2.iri2uri']
else:
	from httplib2_python3 import iri2uri
	sys.modules[__name__] = sys.modules['httplib2_python3.iri2uri']
