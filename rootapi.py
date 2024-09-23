#!/bin/python3
from urllib.request import urlopen
from bs4 import BeautifulSoup

# Get root me username
username = input("Entrer le nom d'utilisateur root me : ")

# HTTPS Request
url = f"https://www.root-me.org/{username}"
page = urlopen(url)
soup = BeautifulSoup(page.read().decode("utf-8"), 'html.parser')

# Start parsing
stats = {}
row = soup.find_all("div", {"class": "small-6 medium-3 columns text-center"})
for line in row:
    array = line.get_text().split()
    stats[array[1]] = array[0]

print(f"Stats de {username} : {stats}")
