#!/usr/bin/env python
# coding: utf-8
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from pytube import YouTube
import os
from urllib.parse import quote_plus as urlencode
import requests
from bs4 import BeautifulSoup
import re
import ipaddress
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
def playlist_to_names(playlist_link, sp):
    """Given a spotify playlist link and a spotify client, extracts the song names and artist names"""
    playlist_URI = playlist_link.split("/")[-1].split("?")[0]
    return [x["track"]["name"] + " " + x["track"]["artists"][0]["name"] for x in sp.playlist_tracks(playlist_URI)["items"]]
def name_to_link(s):
    """
    searches youtube '{song name} {artist name} audio' and gives back a link to the first result
    probably somewhat fragile
    """
    #okay maybe we scape instead of using API
    url = f"http://www.youtube.com/results?search_query={urlencode(s + ' audio')}"
    contents = requests.get(url).content
    soup = BeautifulSoup(contents, features='lxml')
    video_id = re.search(r'"url":"\/watch\?v=(...........)',str(soup)).group(1)
    return "http://www.youtube.com/watch?v=" + video_id
    #url = f"" idk check api docs again
    #video_id = json_to_dict(urlopen(url).read())["items"][0]["id"]["videoId"]
    #return "https://www.youtube.com/watch?v=" + video_id
def playlist_to_links(playlist_link, sp, skip = 0):
    """converts a spotify playlist into a list of youtube links"""
    return [name_to_link(x) for x in playlist_to_names(playlist_link, sp)[skip:]]
def index_to_alph(x):
    alph = [chr(x) for x in range(65, 65 + 26)]
    return [a + b for a in alph for b in alph][x]
def download_playlist(playlist_link, skip = 0):
    """finds the songs on youtube then downloads them"""
    cid = "XXX"
    secret = "XXX"
    client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
    sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)
    links = playlist_to_links(playlist_link, sp, skip = 0)
    playlist_URI = playlist_link.split("/")[-1].split("?")[0]
    playlist_name = sp.playlist(playlist_URI)["name"]
    #fragile?
    os.chdir(str(input("Please enter where you would like to create the folder with the mp3s (e.g. /Users/{username}/Desktop): ")))
    for i, link in enumerate(links):
        yt = YouTube(link)
        video = yt.streams.filter(only_audio=True).first()
        out_file = video.download(output_path=playlist_name)
        base, ext = os.path.splitext(out_file)
        new_file = base + '.mp3'
        print("New file at ", new_file)
        os.rename(out_file, new_file)
    rename_by_date(playlist_name)
def rename_by_date(d, offset = 0):
    files = os.listdir(d)
    files.sort(key=lambda x: os.path.getmtime(os.path.join(d, x)))
    for i, x in enumerate(files):
        os.rename(os.path.join(d, x), os.path.join(d, index_to_alph(i + offset) + " " + x))
download_playlist(str(input("Please enter the playlist link: ")))
print("Done!")     
