SOURCES += modules/google
SOURCES += modules/googleapiclient
SOURCES += modules/google_auth_httplib2.py
SOURCES += modules/httplib2
SOURCES += modules/httplib2_python3
SOURCES += modules/httplib2_python2
SOURCES += modules/oauth2client
SOURCES += modules/six.py
SOURCES += modules/uritemplate

SOURCES += icon.png
SOURCES += main.py
SOURCES += metadata.xml
SOURCES += settings.ui

ZIP = current.zip

all: $(ZIP)

$(ZIP): $(SOURCES)
	zip -r $@ $^
