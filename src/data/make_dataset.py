import random

import requests
import time
from bs4 import BeautifulSoup
import pandas as pd
import os

def get_all_college_urls(cur_year = 2025):
    url = 'https://www.sports-reference.com/cbb/schools/'
    time.sleep(random.uniform(3, 5))

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    college_urls = []

    schools_table = soup.find('table', id='NCAAM_schools')

    if schools_table:
        for row in schools_table.find_all('tr')[1:]:
            cols = row.find_all('td')
            if len(cols) > 5:
                end_year = cols[3].text.strip()
                if end_year == str(cur_year):
                    link = row.find('a')
                    if link and '/cbb/schools/' in link['href']:
                        full_url = f'https://www.sports-reference.com{link['href']}'
                        college_urls.append(full_url)

    return list(set(college_urls))

def get_player_ids_from_rosters(college_urls, season=2025):
    player_ids=[]

    for url in college_urls:
        roster_url = f'{url}{season}.html'
        print(f'Scraping roster page: {roster_url}')

        time.sleep(random.uniform(3, 5))

        response = requests.get(roster_url)
        if response.status_code != 200:
            print(f'Fail {roster_url}')
            continue

        soup = BeautifulSoup(response.text, 'html.parser')

        roster_table = soup.find('table', id='roster')
        if roster_table:
            for row in roster_table.find_all('tr')[1:]:
                link = row.find('a')
                if link and '/cbb/players/' in link['href']:
                    player_id = link['href'].split('/')[-1].replace('.html', '')
                    player_ids.append(player_id)

    return list(set(player_ids))

if __name__ == '__main__':
    college_urls = get_all_college_urls()
    print(f'Found {len(college_urls)} college team URLs.')

    all_cbb_player_ids = get_player_ids_from_rosters(college_urls, 2025)

    if all_cbb_player_ids:
        os.makedirs('interim', exist_ok=True)
        df_ids = pd.DataFrame(all_cbb_player_ids, columns=['player_id'])
        file_path = '../../data/raw/all_cbb_player_ids.csv'
        df_ids.to_csv(file_path, index=False)
        print(f'Found and saved {len(all_cbb_player_ids)} unique player IDs to {file_path}')
    else:
        print('No Player IDs were found.')