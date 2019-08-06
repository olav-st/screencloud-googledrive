###############################
## Workaround for sys.argv errors ##
import sys
if not hasattr(sys, 'argv'):
    sys.argv  = ['']
###############################

import ScreenCloud
from PythonQt.QtCore import QFile, QSettings, QUrl, QByteArray, QBuffer, QIODevice
from PythonQt.QtGui import QDesktopServices
from PythonQt.QtUiTools import QUiLoader
import time, string, sys
from httplib2 import Http
from oauth2client import client, tools
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload
if sys.version_info[0] >= 3:
    import io
    BytesIO = io.BytesIO
else:
    import StringIO
    BytesIO = StringIO.StringIO


SCOPES = 'https://www.googleapis.com/auth/drive.file'

class GoogleDriveUploader():
    def __init__(self):
        self.uil = QUiLoader()
        self.loadSettings()
        if self.accessToken:
            credentials = client.AccessTokenCredentials(self.accessToken, 'my-user-agent/1.0')
            self.driveService = build('drive', 'v3', http=credentials.authorize(Http()))

    def showSettingsUI(self, parentWidget):
        self.parentWidget = parentWidget
        self.settingsDialog = self.uil.load(QFile(workingDir + "/settings.ui"), parentWidget)
        self.settingsDialog.group_account.widget_authorize.button_authenticate.connect("clicked()", self.startAuthenticationProcess)
        self.settingsDialog.group_account.widget_loggedIn.button_logout.connect("clicked()", self.logout)
        self.settingsDialog.group_name.input_nameFormat.connect("textChanged(QString)", self.nameFormatEdited)
        self.settingsDialog.connect("accepted()", self.saveSettings)
        self.loadSettings()
        self.updateUi()
        self.settingsDialog.open()

    def updateUi(self):
        self.loadSettings()
        if not self.accessToken:
            self.settingsDialog.group_account.widget_loggedIn.setVisible(False)
            self.settingsDialog.group_account.widget_authorize.setVisible(True)
            self.settingsDialog.group_account.widget_authorize.button_authenticate.setEnabled(True)
            self.settingsDialog.group_name.setEnabled(False)
            self.settingsDialog.group_folder.setEnabled(False)
            self.settingsDialog.group_clipboard.setEnabled(False)
        else:
            self.settingsDialog.group_account.widget_loggedIn.setVisible(True)
            self.settingsDialog.group_account.widget_authorize.setVisible(False)
            self.settingsDialog.group_account.widget_loggedIn.label_user.setText(self.displayName)
            self.settingsDialog.group_name.setEnabled(True)
            self.settingsDialog.group_folder.setEnabled(True)
            self.settingsDialog.group_clipboard.setEnabled(True)

        self.settingsDialog.group_clipboard.radio_publiclink.setChecked(self.copyLink)
        self.settingsDialog.group_clipboard.radio_dontcopy.setChecked(not self.copyLink)
        self.settingsDialog.group_name.input_nameFormat.setText(self.nameFormat)
        self.settingsDialog.adjustSize()


    def loadSettings(self):
        settings = QSettings()
        settings.beginGroup("uploaders")
        settings.beginGroup("googledrive")
        self.accessToken = settings.value("access-token", "")
        self.clientID = settings.value("clientID", "")
        self.clientSecret = settings.value("clientSecret", "")
        self.displayName = settings.value("display-name", "")
        self.copyLink = settings.value("copy-link", "true") in ['true', True]
        self.nameFormat = settings.value("name-format", "Screenshot at %H-%M-%S")
        self.folderName = settings.value("folder-name", "ScreenCloud")
        settings.endGroup()
        settings.endGroup()

    def saveSettings(self):
        settings = QSettings()
        settings.beginGroup("uploaders")
        settings.beginGroup("googledrive")
        settings.setValue("access-token", self.accessToken)
        settings.setValue("display-name", self.displayName)
        settings.setValue("copy-link", self.settingsDialog.group_clipboard.radio_publiclink.checked)
        settings.setValue("name-format", self.settingsDialog.group_name.input_nameFormat.text)
        settings.setValue("folder-name", self.settingsDialog.group_folder.input_folderName.text)
        settings.endGroup()
        settings.endGroup()

    def isConfigured(self):
        self.loadSettings()
        if not self.accessToken:
            return False
        return True

    def getFilename(self):
        self.loadSettings()
        return ScreenCloud.formatFilename(self.nameFormat)

    def upload(self, screenshot, name):
        self.loadSettings()
        #Save to memory buffer
        ba = QByteArray()
        buf = QBuffer(ba)
        buf.open(QIODevice.ReadWrite)
        screenshot.save(buf, ScreenCloud.getScreenshotFormat())
        #Create folder if not exists
        folders = self.driveService.files().list(
            q="name='%s' and mimeType='application/vnd.google-apps.folder' and trashed=false" % (self.folderName)
        ).execute()["files"]
        exists = len(folders) > 0
        if not exists:
            folderMetadata = {
                'name': self.folderName,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            folder = self.driveService.files().create(body=folderMetadata, fields='id').execute()
        else:
            folder = folders[0]
        #Upload
        fileMetadata = {
            'name': name,
            'parents': [folder["id"]]
        }
        media = MediaInMemoryUpload(ba.data(), mimetype='image/' + ScreenCloud.getScreenshotFormat())
        file = self.driveService.files().create(body=fileMetadata,
                                            media_body=media,
                                            fields='webViewLink, id').execute()
        if self.copyLink:
            webViewLink = file.get('webViewLink')
            ScreenCloud.setUrl(webViewLink)

        return True

    def startAuthenticationProcess(self):
        self.settingsDialog.group_account.widget_authorize.button_authenticate.setEnabled(False)
        self.flow = client.OAuth2WebServerFlow(client_id = '417133363442-dtm48svvid8ntj6locavdvdt3e982n6k.apps.googleusercontent.com',
                           client_secret = 'UmzBQInps-09e6VNbnsRT0BG',
                           scope = SCOPES,
                           redirect_uri = "urn:ietf:wg:oauth:2.0:oob")
        authorize_url = QUrl(self.flow.step1_get_authorize_url())
        QDesktopServices.openUrl(authorize_url)
        try:
            code = raw_input("Enter the authorization code from the Google Drive website:")
        except NameError:
            code = input("Enter the authorization code from the Google Drive website:")
        if code:
            try:
                oauth2_result = self.flow.step2_exchange(code)
                self.accessToken = oauth2_result.access_token
                self.driveService = build('drive', 'v3', http=oauth2_result.authorize(Http()))
                account = self.driveService.about().get(fields="user").execute()
                self.displayName = account["user"]["displayName"]
            except client.Error:
                if "win" in sys.platform: #Workaround for crash on windows
                    self.parentWidget.hide()
                    self.settingsDialog.hide()
                QMessageBox.critical(self.settingsDialog, "Failed to authenticate", "Failed to authenticate with Google Drive. Wrong code?")
                if "win" in sys.platform:
                    self.settingsDialog.show()
                    self.parentWidget.show()
        self.saveSettings()
        self.updateUi()

    def logout(self):
        settings = QSettings()
        settings.beginGroup("uploaders")
        settings.beginGroup("googledrive")
        settings.remove("access-token")
        settings.remove("user-id")
        settings.remove("display-name")
        settings.endGroup()
        settings.endGroup()
        self.loadSettings()
        self.updateUi()

    def nameFormatEdited(self, nameFormat):
        self.settingsDialog.group_name.label_example.setText(ScreenCloud.formatFilename(nameFormat))
