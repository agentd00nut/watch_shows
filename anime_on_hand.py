from sys import argv, exit
from string import ascii_lowercase
import requests, re, pickle, os
from bs4 import BeautifulSoup


def setup():
    if os.path.exists("anime_on_hand.txt"):
        os.remove("anime_on_hand.txt")

    anime_list = open("anime_on_hand.txt", "a")

    for letter in range(0, 9):
        print letter
        lst = list(set([link[4:-1] for link in re.findall('iam/.*"', requests.get("http://www.animeonhand.com/anime/list/"+str(letter)).text)]))
        for x in lst:
            anime_list.write(x+"\n")

    for letter in ascii_lowercase:
        print letter
        lst = list(set([link[4:-1] for link in re.findall('iam/.*"', requests.get("http://www.animeonhand.com/anime/list/"+str(letter)).text)]))
        for x in lst:
            anime_list.write(x+"\n")

    anime_list.close()


def get_episode_total(show_url):
    html = requests.get(show_url).text.encode('ascii','ignore')
    return re.search("total: [0-9]*", html).group(0)[7:]


def pad_episode_string(episode, total_episodes):
    pad_chars = len(total_episodes) - len(episode)
    if pad_chars > 0:
        for i in xrange(pad_chars):
            episode = "0"+episode
    return episode


def clean_showname(show):
    return re.sub("-[0-9]*$", "", show)


def get_media_urls(html):
    m =  re.search("http\:\/\/cdn[0-9]+\.hostyourmediafiles\.com.*\.mp4", html)
    if m:
        media_url = m.group(0)
        fixed_media_url = re.sub("cdn[0-9]*", "cdn18", media_url)
        return fixed_media_url, media_url
    return ""


def watch_show(url):

    print "Trying: "+url

    r = requests.get(url)
    if r.status_code == 200:
        for m_url in get_media_urls(r.text.encode('ascii','ignore')):
            print "Checking: "+m_url
            r = requests.head(m_url)
            if r.status_code == 200:
                print "Valid, Running mpv..."
                ec = os.system("mpv "+m_url)
                if ec == 0:
                    exit(0)  # The episode ran so just die.

    return 1  # All the media urls failed.


def pick_episode_from_matches(matches):
    i=0
    for match in matches:
        print str(i)+": "+match
        i+=1

    select = input("pick ep (-1 for none): ")

    return select


def search_for_episode(show_url, page, episode, max_page=10):

    url = show_url+"?page="+str(page)
    html = requests.get(url).text.encode('ascii','ignore')
    soup = BeautifulSoup(html, "html.parser")
    matches = []

    for link in soup.find_all('a',  {'class': 'ui-link-inherit'} ):
        match=re.search("/watch/.*"+str(episode)+".*", link.get('href'))
        if match:
            matches.append(match.group(0))

    select = pick_episode_from_matches(matches)
    if select >= 0:
        return matches[select]

    max_page = re.search("Page [0-9]* of [0-9]*", html).group(0)
    last_space=max_page.find(" ",10)
    max_page=max_page[last_space-1:]

    page+=1

    if page <= max_page:
        search_for_episode(show_url, page, episode, int(max_page))
    else:
        return []


def find_show(show, episode):

    clean_show = clean_showname(show)
    show_url = "http://www.animeonhand.com/iam/"+show
    total_episodes = get_episode_total(show_url)
    p_episode = pad_episode_string(episode, total_episodes)

    e_url = "http://www.animeonhand.com/watch/"+show+"/"+clean_show+"-"+p_episode
    alt_e_url = "http://www.animeonhand.com/watch/"+show+"/"+clean_show+"-"+episode

    watch_show(e_url)
    watch_show(alt_e_url)

    e_url = search_for_episode(show_url, 1, show, episode)

    if len(e_url) > 0:
        watch_show(e_url)

    exit("We give up")


# MAIN

show = argv[1].replace(" ", "-")
ep = argv[2]

if show == "SETUP":
    setup()

anime_list=[line.strip() for line in open("anime_on_hand.txt", "r")]

matching_shows=[match for match in anime_list if show in match]

if len(matching_shows) > 1:
    print "Multiple results found.  Please pick one."
    i=0
    for match in matching_shows:
        print str(i)+": "+match
        i+=1
    choice=input("Enter a Number: ")
    show=matching_shows[choice]


find_show(show, ep)