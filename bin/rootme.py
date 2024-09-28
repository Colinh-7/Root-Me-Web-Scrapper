#!/bin/python3

import csv, sys, time, curses
from urllib.request import urlopen, HTTPError
from bs4 import BeautifulSoup  

def split_words(list):
    # Liste des mois en français
    month = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", 
            "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]

    result = []
    new = []
    for temp in list:
        done = False
        for m in month:
            if m in temp:
                part= temp.split(m)
                new.append(part[0])
                new.append(m)
                done = True
                break
        if not done:
            new.append(temp)
    return new

def normalize_challenges(list):
    new = []
    for tmp in list:
        line = ""
        for word in tmp:
            line += word
            line += " "
        new.append(line)
    return new
            
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
    challenges = []
    find = False
    challenge_section = None

    sections = userpage.find_all("div", class_= "t-body tb-padding")
    for section in sections:
        activity = section.find_all("h3")
        for a in activity:
            if a.get_text().find("Activité") > -1:
                find = True
                break
        if find :
            challenge_section = section
            break
    
    if challenge_section != None :
        challenge_section = challenge_section.find_all("li")

        for line in challenge_section:
            challenges.append(split_words(line.get_text().split()))

    return challenges

class User:
    def __init__(self, name):
        self.name = name
        try:
            user_response = https_request(self.name)
            self.stats = get_user_stats(user_response)
            self.challenges = get_last_challenges(user_response)
            self.challenges = normalize_challenges(self.challenges)
        except HTTPError as e:
            self.stats = {}
            self.challenges = []
            print(f"{e}")

    def get_name(self):
        return self.name

    def get_stats(self):
        return self.stats
    
    def get_last_challenges(self):
        return self.challenges
    
    def __repr__(self):
        return f"{self.name} : {self.stats}, {self.challenges}"

class Window:
    class MenuOpt:
        CHALLENGES = 0
        STATS = 1
        QUIT = 2

    NB_CHAR = 60

    def __init__(self):
        # Curses init
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        #curses.start_color()
        self.stdscr.keypad(True)

    def update_progress_bar(self, user, nb_char):
        load_text = "Chargement: "
        percent = nb_char / self.NB_CHAR * 100
        self.stdscr.clear()
        self.stdscr.addstr(0, 0, load_text)
        self.stdscr.addstr(0, len(load_text), "#" * nb_char)
        self.stdscr.addstr(0, len(load_text) + self.NB_CHAR, f"({percent:.1f}%)")
        self.stdscr.addstr(1, 0, f"Récupération des données de {user}.")
        self.stdscr.refresh()

    def load (self, csv):
        try:
            users_csv = csv_parsing(csv)
        except FileNotFoundError as e:
            print("Erreur : fichier introuvable.")

        self.users = {}
        i = 1
        # Get data for all users
        for user in users_csv:
            self.update_progress_bar(user, self.NB_CHAR // len(users_csv) * i)
            self.users[user] = User(user)
            time.sleep(1)
            i += 1

        self.stdscr.clear()
    
    def print_challenges(self):
        self.stdscr.addstr(0, 0, "Listes des challenges : ", curses.A_BOLD | curses.A_UNDERLINE)
        idx = 1
        for user in self.users:
            self.stdscr.addstr(idx, 0, f"{user} :", curses.A_UNDERLINE)
            idx += 1
            for challenge in self.users[user].get_last_challenges():
                self.stdscr.addstr(idx, 5, challenge)  
                idx += 1

        self.stdscr.getch()
        self.stdscr.clear()         
        
    def print_stats(self):
        self.stdscr.addstr(0, 0, "Statistiques :", curses.A_BOLD | curses.A_UNDERLINE)
        idx = 1
        for user in self.users:
            self.stdscr.addstr(idx, 0, f"{user} :", curses.A_UNDERLINE)
            idx += 1
            stats = self.users[user].get_stats()
            for stat in stats:
                self.stdscr.addstr(idx, 5, f"{stat} : {stats[stat]}")  
                idx += 1

        self.stdscr.getch()
        self.stdscr.clear() 

    def start(self, csv):
        self.load(csv)

        menu = ["Afficher les challenges", "Afficher les stats", "Quitter"]
        current_row = self.MenuOpt.CHALLENGES

        while True:
            h, w = self.stdscr.getmaxyx()
            menu_win = curses.newwin(len(menu), w // 2, 0, 0)
            members_win = curses.newwin(len(self.users)+2, w // 3, 0, int(w * 0.66))
            
            # Members menu
            members_win.border(0)
            members_win.addstr(0, 1, "Liste des membres :", curses.A_BOLD | curses.A_UNDERLINE)
            for idx, username in enumerate(self.users):
                members_win.addstr(idx+1, 1, username)

            # Left menu
            for idx, row in enumerate(menu):
                if idx == current_row:
                    menu_win.addstr(idx, 0, row, curses.A_REVERSE) 
                else:
                    menu_win.addstr(idx, 0, row)

            self.stdscr.refresh()
            members_win.refresh()
            menu_win.refresh()
            
            key = self.stdscr.getch()

            if key == curses.KEY_UP:
                current_row = (current_row - 1) % len(menu)
            elif key == curses.KEY_DOWN:
                current_row = (current_row + 1) % len(menu)
            elif key == ord('\n'):
                match current_row:
                    case self.MenuOpt.CHALLENGES:
                        self.stdscr.clear()
                        self.print_challenges()
                    case self.MenuOpt.STATS:
                        self.stdscr.clear()
                        self.print_stats()
                    case self.MenuOpt.QUIT:
                        break

            self.stdscr.clear()
            
        curses.endwin()

def main(args):
    win = Window()
    win.start(args)
   
if __name__ == "__main__":
    try:
        main(sys.argv[1])
    except IndexError:
        print(f"Usage : {sys.argv[0]} <csv>")
