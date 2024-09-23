#!/bin/python3

import csv
import sys
from urllib.request import urlopen, HTTPError
from bs4 import BeautifulSoup    

# CSV parsing
def csv_parsing(file):
    users = []
    with open(file, 'r', newline='') as csvfile:
        dict_read = csv.reader(csvfile, delimiter=';')
        for line in dict_read:
            users.append(line[0])
        return users
        
# Web response from the request
def https_request(username):
    url = f"https://www.root-me.org/{username}"
    page = urlopen(url)
    return BeautifulSoup(page.read().decode("utf-8"), 'html.parser')

# Get user's profile stats
def get_user_stats(userpage):
    stats = {}
    row = userpage.find_all("div", {"class": "small-6 medium-3 columns text-center"})
    for line in row:
        array = line.get_text().split()
        stats[array[1]] = array[0]
    return stats

# Get user's last challenges
def get_last_challenges(userpage):
    challenges = {}
    find = False
    challenge_section = None

    sections = userpage.find_all("div", class_= "t-body tb-padding")
    for section in sections:
        activity = section.find_all("h3")
        for a in activity:
            if a.get_text().find("Activité") > -1:
                print("Activité récente trouvé.")
                find = True
                break
        if find :
            challenge_section = section
            break
    
    # =========== A FAIRE ==================

    #row = section.find_all("ul")
    #for line in row:
        #array = line.get_text()#.split()
        #print(array)
    return

class User:
    def __init__(self, name):
        self.name = name
        try:
            user_response = https_request(self.name)
            self.stats = get_user_stats(user_response)
            self.challenges = get_last_challenges(user_response)
        except HTTPError as e:
            print(f"{e}")

    def get_stats(self):
        return self.stats
    
    def get_last_challenges(self):
        return self.challenges
    
    def __repr__(self):
        return f"{self.name} : {self.stats}, {self.challenges}"


def main(args):
    try:
        users_csv = csv_parsing(args)
    except FileNotFoundError as e:
        print("Erreur : fichier introuvable.")

    users = {} 
    # Get data for all users
    for user in users_csv:
        print(user)
        users[user] = User(user)
        #print(users[user])


if __name__ == "__main__":
    try:
        main(sys.argv[1])
    except IndexError:
        print(f"Usage : {sys.argv[0]} <csv>")
