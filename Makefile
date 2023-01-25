SOURCES += modules/cachetools
SOURCES += modules/certifi
SOURCES += modules/chardet
SOURCES += modules/google
SOURCES += modules/googleapiclient
SOURCES += modules/google_auth_httplib2.py
SOURCES += modules/google_auth_oauthlib
SOURCES += modules/idna
SOURCES += modules/httplib2
SOURCES += modules/httplib2_python3
SOURCES += modules/httplib2_python2
SOURCES += modules/oauth2client
SOURCES += modules/oauthlib
SOURCES += modules/pyasn1
SOURCES += modules/pyasn1_modules
SOURCES += modules/requests
SOURCES += modules/requests_oauthlib
SOURCES += modules/rsa
SOURCES += modules/six.py
SOURCES += modules/uritemplate
SOURCES += modules/urllib3

SOURCES += icon.png
SOURCES += main.py
SOURCES += metadata.xml
SOURCES += settings.ui

ZIP = current.zip

all: $(ZIP)

$(ZIP): $(SOURCES)
	zip -r $@ $^
