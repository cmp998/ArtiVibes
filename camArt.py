#ArtiVibes | TigerHacks 2019

import numpy as np
import cv2
from collections import deque
import numpy as np
from PIL import Image
import sys
import spotipy
import spotipy.util as util
import requests
import json
import pprint
import base64
import math

playlist = []

def getSong(valence):
    playlist = []
    scope = 'ugc-image-upload playlist-read-collaborative playlist-modify-private playlist-modify-public playlist-read-private user-modify-playback-state user-read-currently-playing user-read-playback-state user-read-private user-read-email user-library-modify user-library-read user-read-recently-played user-top-read streaming app-remote-control'
    username = "connor_pautz"

    token = util.prompt_for_user_token(username, scope,
        client_id='62e21b5370884eee90c6d332110df385',
        client_secret='71bb03bebc084c538e0f3352e244141d',
        redirect_uri='https://localhost:8080/callback')

    if token:
        newPlaylist = requests.post('https://api.spotify.com/v1/users/'+username+'/playlists',
            data="{\"name\":\""+ "ArtiVibes: " + str(valence) + "\",\"description\":\"New playlist description\",\"public\":true}",
            headers={'Authorization': 'Bearer ' + token, 'Accept': 'application/json', 'Content-Type': 'application/json'})
        response = requests.get("https://api.spotify.com/v1/recommendations?limit=5&market=US&seed_artists=4NHQUGzhtTLFvgF5SZesLK&seed_tracks=0c6xIDDpzE81m2q797ordA&target_valence=" + str(valence),
            headers={'Authorization': 'Bearer ' + token, 'Accept': 'application/json', 'Content-Type': 'application/json'})
        data = response.json()
        playID = newPlaylist.json()
        playID = playID["id"]
        for i in range(0,5):
            temp = data["tracks"][i]["uri"]
            temp = temp.replace(':','%3A')
            playlist.append(temp)
        for i in playlist:
            stuff = requests.post('https://api.spotify.com/v1/users/'+username+'/playlists/' + playID + '/tracks?uris=' + i,
                headers={'Authorization': 'Bearer ' + token, 'Accept': 'application/json', 'Content-Type': 'application/json'})
        #Set Volume and send the device to the newly created playlist
        requests.put('https://api.spotify.com/v1/me/player/volume?volume_percent=100&device_id=faeeb8fa86110a9007ae4f49fbea8a93c65258b2',
            headers={'Authorization': 'Bearer ' + token, 'Accept': 'application/json', 'Content-Type': 'application/json'})
        requests.put('https://api.spotify.com/v1/me/player/play?device_id=faeeb8fa86110a9007ae4f49fbea8a93c65258b2',
            data="{\"context_uri\":\"spotify:playlist:" + playID + "\"}",
            headers={'Authorization': 'Bearer ' + token, 'Accept': 'application/json', 'Content-Type': 'application/json'})

    else:
        print("Can't get token for", username)


#Turns png into pixel count and call getSong with valence
def play_song():
    im=np.array(Image.open("output.png"))
    blue_px_cnt = np.count_nonzero(np.all(im == [0, 0, 255], axis=2))
    green_px_cnt = np.count_nonzero(np.all(im==[0,255,0],axis=2))
    red_px_cnt = np.count_nonzero(np.all(im==[255,0,0],axis=2))
    yellow_px_cnt = np.count_nonzero(np.all(im==[255,255,0],axis=2))
    valence = round((blue_px_cnt * 0 + green_px_cnt * 0.33 + yellow_px_cnt * 0.66 + red_px_cnt * 1) / (blue_px_cnt + green_px_cnt + yellow_px_cnt + red_px_cnt), 2)
    print(valence)
    getSong(valence)

#Create the webpaint windows
def webPaint():
    #Define a 5x5 kernel for erosion and dilation
    kernel = np.ones((5, 5), np.uint8)

    #Create the deques for each color
    bpoints = [deque(maxlen=512)]
    gpoints = [deque(maxlen=512)]
    rpoints = [deque(maxlen=512)]
    ypoints = [deque(maxlen=512)]
    bindex = 0
    gindex = 0
    rindex = 0
    yindex = 0

    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 255, 255)]
    colorIndex = 0

    #Setup the Paint interface
    paintWindow = np.zeros((471,636,3)) + 255
    cv2.namedWindow('Paint', cv2.WINDOW_AUTOSIZE)
    cv2.moveWindow("Paint", 20,20)
    paintWindow = cv2.resize(paintWindow, (1282,720))

    #Load the video and tracking of contour
    camera = cv2.VideoCapture(0)
    while True:
        #Grab the current paintWindow
        (grabbed, frame) = camera.read()
        frame = cv2.flip(frame, 1)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        #Add the coloring options to the frame
        frame = cv2.rectangle(frame, (50,1), (150,65), (122,122,122), -1)
        frame = cv2.rectangle(frame, (160,1), (260,65), colors[0], -1)
        frame = cv2.rectangle(frame, (270,1), (370,65), colors[1], -1)
        frame = cv2.rectangle(frame, (380,1), (480,65), colors[2], -1)
        frame = cv2.rectangle(frame, (490, 1), (590, 65), colors[3], -1)
        frame = cv2.rectangle(frame, (600,1), (750,65), (122,122,122), -1)
        cv2.putText(frame, "RESET", (77, 38), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, "BLUE", (190, 38), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, "GREEN", (292, 38), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, "RED", (415, 38), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, "YELLOW", (510, 38), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
        cv2.putText(frame, "CURATE VIBES", (630, 38), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

        #End of Video Check
        if not grabbed:
            break

        #Blue Masking
        Mask = cv2.inRange(hsv, (100,60,60), (140,255,255))
        Mask = cv2.erode(Mask, kernel, iterations=2)
        Mask = cv2.morphologyEx(Mask, cv2.MORPH_OPEN, kernel)
        Mask = cv2.dilate(Mask, kernel, iterations=1)

        #Determine contours available
        (cnts, _) = cv2.findContours(Mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        center = None

        #Contour Tracking
        if len(cnts) > 0:
            #Choose largest contour
            cnt = sorted(cnts, key = cv2.contourArea, reverse = True)[0]
            ((x, y), radius) = cv2.minEnclosingCircle(cnt)
            #Put circle around 'brush'
            cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
            #Calc moments for brush
            M = cv2.moments(cnt)
            center = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))

            if center[1] <= 65:
                if 40 <= center[0] <= 140: # Clear All
                    bpoints = [deque(maxlen=512)]
                    gpoints = [deque(maxlen=512)]
                    rpoints = [deque(maxlen=512)]
                    ypoints = [deque(maxlen=512)]

                    bindex = 0
                    gindex = 0
                    rindex = 0
                    yindex = 0

                    paintWindow[67:,:,:] = 255
                elif 160 <= center[0] <= 260:
                        colorIndex = 0 # Blue
                elif 270 <= center[0] <= 370:
                        colorIndex = 1 # Green
                elif 380 <= center[0] <= 480:
                        colorIndex = 2 # Red
                elif 490 <= center[0] <= 590:
                        colorIndex = 3  # Yellow
                elif 600 <= center[0] <= 700:
                    cv2.imwrite("output.png", paintWindow)
                    play_song()
            else :
                if colorIndex == 0:
                    bpoints[bindex].appendleft(center)
                elif colorIndex == 1:
                    gpoints[gindex].appendleft(center)
                elif colorIndex == 2:
                    rpoints[rindex].appendleft(center)
                elif colorIndex == 3:
                    ypoints[yindex].appendleft(center)
        #Appened when contour is lost
        else:
            bpoints.append(deque(maxlen=512))
            bindex += 1
            gpoints.append(deque(maxlen=512))
            gindex += 1
            rpoints.append(deque(maxlen=512))
            rindex += 1
            ypoints.append(deque(maxlen=512))
            yindex += 1

        #Actual line drawing
        points = [bpoints, gpoints, rpoints, ypoints]
        for i in range(len(points)):
            for j in range(len(points[i])):
                for k in range(1, len(points[i][j])):
                    if points[i][j][k - 1] is None or points[i][j][k] is None:
                        continue
                    cv2.line(frame, points[i][j][k - 1], points[i][j][k], colors[i], 3)
                    cv2.line(paintWindow, points[i][j][k - 1], points[i][j][k], colors[i], 3)

        #Bring up both windows
        cv2.moveWindow("Tracking",20,20)
        cv2.imshow("Tracking", frame)
        cv2.imshow("Paint", paintWindow)

        #Kill on 'q' press
        if cv2.waitKey(1) & 0xFF == ord("q"):
            cv2.imwrite("output.png", paintWindow)
            cv2.imwrite("output.jpg", paintWindow)
            break

    #Cleanup time
    camera.release()
    cv2.destroyAllWindows()

#Run this stuffs
webPaint()
#getSong(.5)