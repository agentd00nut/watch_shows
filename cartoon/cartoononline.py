from sys import argv, exit
from string import ascii_lowercase
import requests, re, pickle, os, json
from bs4 import BeautifulSoup


def setup():
    if os.path.exists("cartoon_online.txt"):
        os.remove("cartoon_online.txt")

    cartoon_list = open("cartoon_online.txt", "a")

    lst = list(set([link[6:-1] for link in re.findall('anime/.*?"', requests.get("http://www.watchcartoononline.com/dubbed-anime-list").text)]))
    for x in lst:
        cartoon_list.write(x+"\n")

    lst = list(set([link[6:-1] for link in re.findall('anime/.*?"', requests.get("http://www.watchcartoononline.com/subbed-anime-list").text)]))
    for x in lst:
        cartoon_list.write(x+"\n")

    lst = list(set([link[6:-1] for link in re.findall('anime/.*?"', requests.get("http://www.watchcartoononline.com/cartoon-list").text)]))
    for x in lst:
        cartoon_list.write(x+"\n")

    cartoon_list.close()
    with open("cartoon_online.txt", "r") as f:
        uniq_lines = set(f)
    os.remove("cartoon_online.txt");

    cartoon_list = open("cartoon_online.txt", "a")
    for line in uniq_lines:
        cartoon_list.write(line)


def pick_episode_from_matches(matches):
    i=0
    for match in matches:
        print str(i)+": "+match
        i+=1
    return input("pick ep: ")


def get_media_url(ep_url):
    print "Getting Media Url From: "+ep_url
    html = requests.get(ep_url).text.encode('ascii','ignore')
    soup = BeautifulSoup(html, 'html.parser')
    return soup.find('meta', {'itemprop': 'embedURL'}).get('content')


def get_video_link(media_url):
    print "Getting Video Link From: "+media_url
    r = requests.post(media_url, data={'fuck_you': '', 'confirm': 'Click+Here+to+Watch+Free%21%21'})
    html = r.text.encode('ascii','ignore')

    m = re.findall("file\:.*?\.flv", html)
    video_link =  m[-1][7:]
    r = requests.head(video_link, allow_redirects=True)
    video_link = r.url
    return video_link


def mpv_url(media_url):
    ec = os.system("mpv "+media_url)
    if ec == 0:
        exit(0)  # The episode ran so just die.


def get_episode_list(show_url, season, ep, retry=False):
    soup = BeautifulSoup(requests.get(show_url).text.encode('ascii','ignore'), 'html.parser')

    if retry:
        show_url += "season"  #Ghetto way to check for episode links without season in them.

    if "season" in show_url:
        search = ""+ep
    elif season == "LIST":
        search = "season-"+ep
    else:
        search = "season-"+season+"-episode-"+ep

    episodes = [link.get('href')[34:] for link in soup.find_all('a',  {'class': 'sonra'}) if search in link.get('href')]

    if len(episodes) == 0 and retry == False:
        return get_episode_list(show_url, season, ep, True)

    return episodes


def natural_sort(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(l, key = alphanum_key)

def check_for_200(url):
    r = requests.head(url)
    if r.status_code == 200:
        return True
    return False

def find_show(show, season, ep):

    if season == "LIST":
        print "Listing Episodes for "+show+" Season "+ep
    else:
        print "Searching for "+show+" Season "+season+" Episode "+ep

    show_url="http://watchcartoononline.com/anime/"+show
    episodes = get_episode_list(show_url, season, ep)


    if len(episodes) > 1:
        ep_url = "http://watchcartoononline.com/"+episodes[pick_episode_from_matches(episodes)]
    else:
        ep_url = "http://watchcartoononline.com/"+episodes[0]

    video_link = get_video_link(get_media_url(ep_url))

    tries = 0
    retries = 5
    while not check_for_200(video_link):
        print "Bad Link: "+video_link
        tries += 1
        if tries == retries:
            break
        video_link = get_video_link(get_media_url(ep_url))

    mpv_url(video_link)


show = argv[1].replace(" ", "-")
season = argv[2]
if len(argv) > 3:
    ep = argv[3]
else:
    ep =''

if show == "SETUP":
    setup()

show_list=[line.strip() for line in open("cartoon_online.txt", "r")]

matching_shows=natural_sort([match for match in show_list if show in match])

matches = len(matching_shows)
if matches > 1:
    print "Multiple results found.  Please pick one."
    i=0
    for match in matching_shows:
        print str(i)+": "+match
        i+=1
    choice=input("Enter a Number: ")
    show=matching_shows[choice]

elif matches == 1:
    show=matching_shows[0]

elif matches == 0:
    exit("Show not found")


find_show(show, season, ep)