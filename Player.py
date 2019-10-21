import vlc
import sys, os

class Player():

    self.mypath = "/home/vxrich/Documenti/CarPy-Multimedia-System/src/songs/"

    def __init__(self):

        self.player_status = 0
        self.random_status = 0
        self.player = vlc.MediaPlayer()

    def play(self, song):

        self.player.stop()
        self.player = vlc.MediaPlayer(self.mypath + song + ".mp3")
        self.player.play()

    def stop(self):

        self.player.stop()

        
        
