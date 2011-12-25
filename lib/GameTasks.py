from DBFunctions import GetRequestedGamesAsArray,UpdateStatus
import sys
import urllib
import urllib2
import os
import shutil
import stat
from subprocess import call
from Logger import LogEvent

class GameTasks():

    def FindGames(self, nzbmatrixusername, nzbmatrixapi,sabnzbdApi,sabnzbdHost,sabnzbdPort):
        GameTasks().CheckIfPostProcessExistsInSab(sabnzbdApi,sabnzbdHost,sabnzbdPort)
        nzbmatrixusername = nzbmatrixusername.replace('"','')
        nzbmatrixapi = nzbmatrixapi.replace('"','')
        games = GetRequestedGamesAsArray()
        for game in games:
            try:
                game_name = str(game[0])
                game_id = str(game[1])
                LogEvent("Searching for game: " + game_name)
                nzbmatrixResult = GameTasks().FindGameOnNZBMatrix(game_name,game_id,nzbmatrixusername,nzbmatrixapi,sabnzbdApi,sabnzbdHost,sabnzbdPort)
            except:
                error = sys.exc_info()[0]
                print error
                continue
        return

    def FindGameOnNZBMatrix(self,game_name,game_id,username,api,sabnzbdApi,sabnzbdHost,sabnzbdPort):
        url = "http://api.nzbmatrix.com/v1.1/search.php?search=" + game_name + "&num=1&cat=44&username=" + username + "&apikey=" + api
        opener = urllib.FancyURLopener({})
        responseObject = opener.open(url)
        response = responseObject.read()
        responseObject.close()
        responseData = response.split("\n")
        fieldData = responseData[0].split(":")
        nzbID = fieldData[1]
        nzbID = nzbID.replace(";","")

        if(nzbID <> "nothing_found"):
            LogEvent("Game found on NZB Matrix")
            GameTasks().AddNZBToSab(nzbID,game_name,sabnzbdApi,sabnzbdHost,sabnzbdPort,game_id)
            UpdateStatus(game_id,"Snatched")
        return

    def AddNZBToSab(self,nzbID,game_name,sabnzbdApi,sabnzbdHost,sabnzbdPort,game_id):
        nzbUrl = "http://api.nzbmatrix.com/v1.1/download.php?id=" + nzbID
        url = "http://" + sabnzbdHost + ":" +  sabnzbdPort + "/sabnzbd/api?mode=addurl&pp=3&apikey=" + sabnzbdApi + "&script=gamezPostProcess.py&name=" + nzbUrl + "&nzbname=[" + game_id + "] - "+ game_name
        responseObject = urllib.FancyURLopener({}).open(url)
        responseObject.read()
        responseObject.close()
        LogEvent("NZB added to Sabnzbd")
        return

    def CheckIfPostProcessExistsInSab(self,sabnzbdApi,sabnzbdHost,sabnzbdPort):
        path = os.path.abspath("postprocess")
        srcPath = os.path.join(path,"gamezPostProcess.py")
        url = "http://" + sabnzbdHost + ":" + sabnzbdPort + "/sabnzbd/api?mode=get_config&apikey=" + sabnzbdApi + "&section=misc&keyword=script_dir"
        opener = urllib.FancyURLopener({})
        responseObject = opener.open(url)
        response = responseObject.read()
        responseObject.close()
        scriptDir = response.split(":")[2].replace("'","").replace(" ","").replace("{","").replace("}","").replace("\n","")
        destPath = os.path.join(scriptDir,"gamezPostProcess.py")

        try:
            LogEvent("Copying post process script to Sabnzbd scripts folder")
            shutil.copyfile(srcPath,destPath)
        except:
            print 'Error Copying File'
        try:
            LogEvent("Setting permissions on post process script")
            cmd = "chmod +x '" + destPath + "'"
            os.system(cmd)
        except:
            print 'Error Setting Permissions'
        return