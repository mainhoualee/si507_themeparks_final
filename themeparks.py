#################################
##### Name: Mai Nhoua Lee
##### Uniqname: mainlee
#################################

import urllib.request
import sqlite3
import plotly.graph_objects as go

# Scraping state URLs

def scrape_state_urls():

    page_url = 'https://www.ultimaterollercoaster.com/themeparks/'

    entry = (page_url,)
    cursor.execute('SELECT * FROM main_cache WHERE url=?', entry)
    cache = cursor.fetchone()

    if cache != None:
        print('Using Cache')
        html_text = cache[1]
    else:
        print('Fetching')
        request = urllib.request.urlopen(page_url)
        html_bytes = request.read()
        html_text = html_bytes.decode('utf-8')
        entry = (page_url, html_text)
        conn.execute('INSERT INTO main_cache VALUES (?,?)', entry)
        conn.commit()

    html_lines = html_text.split('\n')

    states_dict = {}
    states_info = False
    for line in html_lines:
        if '<ul class="stateList">' in line:
            states_info = True
        elif '</ul>' in line:
            states_info = False
        elif states_info:
            line = line.strip().replace('<li><a href="','').replace('">',' ').replace('</a></li>','')
            state_url = page_url.split('/themeparks')[0] + line.split()[0]
            state = ' '.join(line.split()[1:])
            states_dict[state.lower()] = state_url

    return states_dict

# ThemePark object

class ThemePark:

    def __init__(self, name, park_type, opening_year, address, zip_code, phone_number):
        self.name = name
        self.park_type = park_type
        self.opening_year = opening_year
        self.address = address
        self.zip_code = zip_code
        self.phone_number = phone_number

    def info(self):
        result = self.name
        if self.park_type != None:
            result += ' (' + self.park_type + ')'
        if self.opening_year != None:
            result += ' ' + self.opening_year
        result += ':'
        if self.address != None:
            result += ' ' + self.address
        if self.zip_code != None:
            result += ' ' + self.zip_code
        return result

# Scraping instance of theme park website

def scrape_theme_park_site(page_url):

    entry = (page_url,)
    cursor.execute('SELECT * FROM park_cache WHERE url=?', entry)
    cache = cursor.fetchone()

    if cache != None:
        print('Using Cache')
        html_text = cache[1]
    else:
        print('Fetching')
        request = urllib.request.urlopen(page_url)
        html_bytes = request.read()
        html_text = html_bytes.decode('utf-8')
        entry = (page_url, html_text)
        conn.execute('INSERT INTO park_cache VALUES (?,?)', entry)
        conn.commit()

    html_lines = html_text.split('\n')

    name, park_type, opening_year, address, zip_code, phone_number = None, None, None, None, None, None
    for i in range(len(html_lines)):
        line = html_lines[i].strip()
        if '<h1 class="new">' in line:
            name = line.replace('<h1 class="new">','').replace('</h1>','')
        elif '<th>Park type:</th>' in line:
            park_type = html_lines[i+1].strip().replace('<td>','').replace('</td>','')
        elif '<th>Opening year:</th>' in line:
            opening_year = html_lines[i+1].strip().replace('<td>','').replace('</td>','').split()[-1]
        elif '<h3>Park Location</h3>' in line:
            location_info = html_lines[i+2].strip().replace('</p>','').split()
            zip_code = location_info[-1]
            address = ' '.join(location_info[:-1])
        elif '<p>Phone:' in line:
            phone_number = line.replace('<p>Phone:','').replace('</p>','').strip()

    theme_park = ThemePark(name, park_type, opening_year, address, zip_code, phone_number)
    return theme_park

# Crawling state website

def crawl_state_website(page_url):

    entry = (page_url,)
    cursor.execute('SELECT * FROM state_cache WHERE url=?', entry)
    cache = cursor.fetchone()

    if cache != None:
        print('Using Cache')
        html_text = cache[1]
    else:
        print('Fetching')
        request = urllib.request.urlopen(page_url)
        html_bytes = request.read()
        html_text = html_bytes.decode('utf-8')
        entry = (page_url, html_text)
        conn.execute('INSERT INTO state_cache VALUES (?,?)', entry)
        conn.commit()

    html_lines = html_text.split('\n')

    park_urls = []
    parks_info = False
    for line in html_lines:
        if '<div class="tpIdx">' in line:
            parks_info = True
        elif '</ul>' in line:
            parks_info = False
        elif parks_info:
            if '<ul>' in line:
                continue
            line = line.strip().replace('<li><a href="','').replace('">',' ').split('</a>')[0]
            park_url = page_url.split('/themeparks')[0] + line.split()[0]
            park_urls.append(park_url)

    return park_urls

# Creating an interactive search interface

def run_search_interface():
    states_dict = scrape_state_urls()
    while True:
        state_name = input('\nEnter a state name (e.g. Alabama, alabama) or "exit": ')
        if state_name == 'exit':
            break
        elif len(state_name) > 1:
            if state_name.lower() in states_dict:
                state_url = states_dict[state_name.lower()]
                theme_parks = []
                park_urls = crawl_state_website(state_url)
                for park_url in park_urls:
                    theme_park = scrape_theme_park_site(park_url)
                    theme_parks.append(theme_park)
                print('----------------------------------------')
                print('List of theme parks in ' + state_name)
                print('----------------------------------------')
                for i in range(len(theme_parks)):
                    print('[' + str(i+1) + '] ' + theme_parks[i].info())
            else:
                print('Error: Unknown state ' + state_name)

# Database Implementation

conn = sqlite3.connect('theme-parks.db')

cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
if len(cursor.fetchall()) == 0:
    cursor.execute('''CREATE TABLE main_cache
                    (url text, html text)''')
    cursor.execute('''CREATE TABLE state_cache
                    (url text, html text)''')
    cursor.execute('''CREATE TABLE park_cache
                    (url text, html text)''')

# Data Presentation

def run_data_presentation():
    states_dict = scrape_state_urls()
    while True:
        print('\nData Presentation Menu:')
        print('  1. Barplot of Number of Theme Parks in each State')
        print('  2. Histogram of Number of Theme Parks in each State')
        print('  3. Barplot of Number of Theme Parks Opened Each Year')
        print('  4. Histogram of Theme Park Name Lengths')
        choice = input('Choice or "exit": ')
        if choice == 'exit':
            return
        if choice == '1':
            states = []
            counts = []
            for state_name in states_dict:
                state_url = states_dict[state_name]
                states.append(' '.join([word[0].upper() + word[1:] for word in state_name.split()]))
                counts.append(len(crawl_state_website(state_url)))
            bar_data = go.Bar(x=states, y=counts)
            basic_layout = go.Layout(title='Barplot of Number of Theme Parks in each State')
            fig = go.Figure(data=bar_data, layout=basic_layout)
            fig.show()
        elif choice == '2':
            counts = []
            for state_name in states_dict:
                state_url = states_dict[state_name]
                counts.append(len(crawl_state_website(state_url)))
            hist_data = go.Histogram(x=counts)
            basic_layout = go.Layout(title='Histogram of Number of Theme Parks in each State')
            fig = go.Figure(data=hist_data, layout=basic_layout)
            fig.show()
        elif choice == '3':
            opening_year_data = []
            for state_name in states_dict:
                state_url = states_dict[state_name]
                park_urls = crawl_state_website(state_url)
                for park_url in park_urls:
                    theme_park = scrape_theme_park_site(park_url)
                    if theme_park.opening_year != None:
                        opening_year_data.append(int(theme_park.opening_year))
            opening_years = sorted(list(set(opening_year_data)))
            opening_year_counts = [opening_year_data.count(opening_year) for opening_year in opening_years]
            bar_data = go.Bar(x=opening_years, y=opening_year_counts)
            basic_layout = go.Layout(title='Barplot of Number of Theme Parks Opened Each Year')
            fig = go.Figure(data=bar_data, layout=basic_layout)
            fig.show()
        elif choice == '4':
            counts = []
            for state_name in states_dict:
                state_url = states_dict[state_name]
                park_urls = crawl_state_website(state_url)
                for park_url in park_urls:
                    theme_park = scrape_theme_park_site(park_url)
                    if theme_park.name != None:
                        counts.append(len(theme_park.name))
            hist_data = go.Histogram(x=counts)
            basic_layout = go.Layout(title='Histogram of Theme Park Name Lengths')
            fig = go.Figure(data=hist_data, layout=basic_layout)
            fig.show()
        else:
            print('Error: Invalid choice')

# Main method to run program

def main():
    print('Enter 1 for Search Interface or 2 for Data Presentation')
    choice = input('Choice: ')
    if choice == '1':
        run_search_interface()
    elif choice == '2':
        run_data_presentation()
    else:
        print('Error: Invalid choice')

# Run main method on program launch

if __name__ == '__main__':
    main()
    conn.close()