#!/usr/bin/python

import urllib2
import urllib
import re
import string

# It would also be nice to work out the formats for http://www.bbc.co.uk/6music/listen/playlist.shtml and http://www.bbc.co.uk/radio2/music-events/playlist/
# Albums might be good too http://www.bbc.co.uk/radio1/chart/albums
def normalize(input_string, for_search=False):
	s = re.sub('&amp;', '', input_string)
	s = re.sub('\(feat\..*?\)', '', s)
	if not for_search: s = re.sub('\W', '', s)
	#print '\tnormalized', input_string, string.lower(s)
	return string.lower(s)

def get_spotify_url(track, artist):
	arg_string = normalize(string.join([track, artist], ' '), True)
	arg_string = urllib.quote(arg_string)
	search_results = urllib2.urlopen('http://ws.spotify.com/search/1/track?q=' + arg_string).read()
	tracks = re.finditer(r'<track href="(?P<href>.*?)">(?P<contents>.*?)</track>', search_results, re.MULTILINE|re.DOTALL)
	for result_track in tracks:
		result_artist = re.search(r'<name>(?P<name>.*?)</name>\s*<artist href="(?P<artist_url>.*?)">\s*<name>(?P<artist>.*?)</name>\s*</artist>', result_track.group('contents'), re.MULTILINE|re.DOTALL)
		normalized_track, normalized_artist, normalized_result_track, normalized_result_artist = map(normalize, [track, artist, result_artist.group('name'), result_artist.group('artist')])
		#print normalized_track, normalized_artist, normalized_result_track, normalized_result_artist
		if (re.search(normalized_track, normalized_result_track) or re.search(normalized_result_track,normalized_track)) and (re.search(normalized_artist, normalized_result_artist) or re.search(normalized_result_artist, normalized_artist)):
			return result_track.group('href')
	return None

def get_radio_2_tracks(url):
	tracks = []
	html = urllib2.urlopen('http://www.bbc.co.uk/radio2/music-events/playlist/').read()
	items = re.findall(r'<div class="record">(.*?)</div>', html, re.MULTILINE|re.DOTALL)
	for item in items:
		subitems = string.split(item, ' - ')
		artist, track = subitems[0], string.join(subitems[1:], ' ')
		tracks.append([None, None, track, artist])
	return tracks



def get_tracks(url):
	tracks = []

	html = urllib2.urlopen(url).read()
	#print html
	items = re.findall(r'<li class="previewable.*?" id="(.*?)">(.*?)</li>', html, re.MULTILINE|re.DOTALL)
	for chart_pos, item in items:
		artists = re.findall(r'<a class="artist-link" href="(.*?)" id=".*?">(.*?)</a>', item, re.MULTILINE|re.DOTALL)
		for link, contents in artists:
			artist = re.findall(r'<span class="artist">(.*?)</span>', contents, re.MULTILINE|re.DOTALL)[0]
			track = re.findall(r'<span class="track">(.*?)</span>', contents, re.MULTILINE|re.DOTALL)[0]
			tracks.append([chart_pos, link, track, artist])
	return tracks

def get_playlist(tracks):
	matched = 0
	playlist = []
	for chart_pos, link, track, artist in tracks:
			print '\tGetting', artist, track, 
			spotify_url = get_spotify_url(track, artist)
			playlist.append([chart_pos, link, track, artist, spotify_url])
			if spotify_url: 
				matched = matched + 1 
				print 'success!'
			else:
				print 'failure!'
	print 'Matched', matched, '/', len(tracks)
	return playlist

charts = [
		['1Xtra All singles', 'http://www.bbc.co.uk/1xtra/chart/singles'],
		['1Xtra New entries', 'http://www.bbc.co.uk/1xtra/chart/singles/new'],
		['1Xtra Climbers', 'http://www.bbc.co.uk/1xtra/chart/singles/up'],
		['1Xtra Fallers', 'http://www.bbc.co.uk/1xtra/chart/singles/down'],
		['Top 40 Singles', 'http://www.bbc.co.uk/radio1/chart/singles'],
		['Top 40 Singles New entries', 'http://www.bbc.co.uk/radio1/chart/singles/new'],
		['Top 40 Singles Climbers', 'http://www.bbc.co.uk/radio1/chart/singles/up'],
		['Top 40 Singles Fallers', 'http://www.bbc.co.uk/radio1/chart/singles/down'],
		['Indie singles', 'http://www.bbc.co.uk/radio1/chart/indiesingles'],
		['RnB singles', 'http://www.bbc.co.uk/radio1/chart/rnbsingles'],
		['Rock singles', 'http://www.bbc.co.uk/radio1/chart/rocksingles'],
		['Asian downloads All Singles', 'http://www.bbc.co.uk/asiannetwork/chart/downloads'],
		['Asian downloads New entries', 'http://www.bbc.co.uk/asiannetwork/chart/downloads/new'],
		['Asian downloads Climbers', 'http://www.bbc.co.uk/asiannetwork/chart/downloads/up'],
		['Asian downloads Fallers', 'http://www.bbc.co.uk/asiannetwork/chart/downloads/down'],
		['Radio 1 Playlist', 'http://www.bbc.co.uk/radio1/playlist/'],
		['Radio 1 Playlist New tracks', 'http://www.bbc.co.uk/radio1/playlist/new'],
		['1Xtra Playlist All tracks', 'http://www.bbc.co.uk/1xtra/playlist/'],
		['1Xtra Playlist New tracks', 'http://www.bbc.co.uk/1xtra/playlist/new'],
		['Radio 2 Playlist', 'http://www.bbc.co.uk/radio2/music-events/playlist/'],
	]

if __name__ == '__main__':
	for name, url in charts:
		print 'Getting', name, 'from', url
		if name == 'Radio 2 Playlist':
			tracks = get_radio_2_tracks(url)
		else:
			tracks = get_tracks(url)
		playlist = get_playlist(tracks)
		#print name, playlist 
		safe_filename = 'output/' + re.sub(r'[:/]', '', url) + '.html' 
		f = open(safe_filename, 'w')
		f.write('<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>' + name + ' Spotify Playlist</title></head><body><h1><a href="' + url + '">' + name + '</a></h1><ul>')
		for track in playlist:
			print track
			if track[4]:
				f.write('<li><a href="%s" class="spotify">%s</a> by <span class="artist">%s</span> (<a href="http://bbc.co.uk%s" class="original">original</a>)</li>' % (track[4], track[2], track[3], track[1]))
			else:
				f.write('<li>%s by <span class="artist">%s</span> (<a href="http://bbc.co.uk%s" class="original">original</a>)</li>' % (track[2], track[3], track[1]))
		f.write('</ul></body></html>')
		f.close()
		print 'Wrote file'
