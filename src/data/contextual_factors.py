import requests
from bs4 import BeautifulSoup, Comment
import pandas as pd
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from six import StringIO

def scrape_team_kenpom(Team, Year):
    url = f'https://kenpom.com/index.php?y={str(Year)}'
    print(f'Scraping data for {Team}')
    team_stats = pd.DataFrame(columns=['rank', 'netrtg', 'adjt', 'luck', 'sos', 'sos_ooc', 'team', 'year'])

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(5)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    driver.quit()

    ratings_table = soup.find('table', id='ratings-table')
    if ratings_table:
        for row in ratings_table.find_all('tbody'):
            for row2 in row.find_all('tr'):
                link = row2.find('a')
                if link.text.strip() == Team:
                    rank = row2.find('td', class_='hard_left')
                    if rank:
                        team_stats.loc[0, 'rank'] = (rank.text.strip())

                    net = row2.find_all('td')
                    if net:
                        for tag in net:
                            if tag.get('class') is None:
                                team_stats.loc[0, 'netrtg'] = tag.text.strip()
                            else:
                                continue
                    left_divide = row2.find_all('td', class_='td-left divide')
                    if left_divide:
                        team_stats.loc[0, 'adjt'] = (left_divide[1]).text.strip()
                        team_stats.loc[0, 'luck'] = (left_divide[2]).text.strip()
                        team_stats.loc[0, 'sos'] = (left_divide[3]).text.strip()
                        team_stats.loc[0, 'sos_ooc'] = (left_divide[4]).text.strip()
                        team_stats.loc[0, 'team'] = Team
                        team_stats.loc[0, 'year'] = Year

                    return team_stats

    if team_stats.empty:
        print('found nothing')
        for col in team_stats.columns:
            team_stats[col] = 'error'
        team_stats.loc[0, 'team'] = Team
        team_stats.loc[0, 'year'] = Year
        return team_stats

def scrape_mul_teams(team_list):
    all_team_stats = []

    for Team, Year in team_list:
        team_stats = scrape_team_kenpom(Team, Year)
        if not team_stats.empty:
            all_team_stats.append(team_stats)
        else:
            all_team_stats.append(team_stats)
            print('dog')

    if all_team_stats:
        combined_df = pd.concat(all_team_stats, ignore_index=True)
        return combined_df
    else:
        return pd.DataFrame()

if __name__ == '__main__':
    transfer_data = pd.read_csv('processed/transfers_stats_with_clusters.csv')

    new_team_list = []
    for index, player in transfer_data.iterrows():
        team = []
        year = player['before_Season']
        year = year[:2] + year[5:]
        if 'State' in player['before_Team']:
            player.replace('State', 'St.', regex=True, inplace=True)
        if 'Louisiana St.' in player['before_Team']:
            player['before_Team'] = 'LSU'
        if 'Gardner-Webb' in player['before_Team']:
            player['before_Team'] = 'Gardner Webb'
        if 'TexasâRio Grande Valley' in player['before_Team']:
            player['before_Team'] = 'UT Rio Grande Valley'
        if "St. Mary's (CA)" in player['before_Team']:
            player['before_Team'] = "Saint Mary's"
        if "Miami (FL)" in player['before_Team']:
            player['before_Team'] = "Miami FL"
        if "Queens (NC)" in player['before_Team']:
            player['before_Team'] = "Queens"
        if "St. John's (NY)" in player['before_Team']:
            player['before_Team'] = "St. John's"
        if "Loyola (MD)" in player['before_Team']:
            player['before_Team'] = "Loyola MD"
        if "Texas A&MâCommerce" in player['before_Team']:
            player['before_Team'] = "East Texas A&M"
        if "ArkansasâPine Bluff" in player['before_Team']:
            player['before_Team'] = "Arkansas Pine Bluff"
        if "Ole Miss" in player['before_Team']:
            player['before_Team'] = "Mississippi"
        if "Central Connecticut St." in player['before_Team']:
            player['before_Team'] = "Central Connecticut"
        if "IllinoisâChicago" in player['before_Team']:
            player['before_Team'] = "Illinois Chicago"
        if "FDU" in player['before_Team']:
            player['before_Team'] = "Fairleigh Dickinson"
        if "Florida International" in player['before_Team']:
            player['before_Team'] = "FIU"
        if "Southern California" in player['before_Team']:
            player['before_Team'] = "USC"
        if "Brigham Young" in player['before_Team']:
            player['before_Team'] = "BYU"
        if "College of Charleston" in player['before_Team']:
            player['before_Team'] = "Charleston"
        if "Saint Francis (PA)" in player['before_Team']:
            player['before_Team'] = "St. Francis PA"
        if "NC St." in player['before_Team']:
            player['before_Team'] = "N.C. State"
        if "UT Martin" in player['before_Team']:
            player['before_Team'] = "Tennessee Martin"
        if "Pennsylvania" in player['before_Team']:
            player['before_Team'] = "Penn"
        if "Southern Mississippi" in player['before_Team']:
            player['before_Team'] = "Southern Miss"
        if "Bethune-Cookman" in player['before_Team']:
            player['before_Team'] = "Bethune Cookman"
        if "St. Francis Brooklyn" in player['before_Team']:
            player['before_Team'] = "St. Francis NY"
        if "SIU Edwardsville" in player['before_Team'] and year == '2025':
            player['before_Team'] = "SIUE"
        if "LouisianaâMonroe" in player['before_Team']:
            player['before_Team'] = 'Louisiana Monroe'
        if "Texas A&MâCorpus Christi" in player['before_Team']:
            player['before_Team'] = 'Texas A&M Corpus Chris'
        if "Albany (NY)" in player['before_Team']:
            player['before_Team'] = 'Albany'
        if "Miami (OH)" in player['before_Team']:
            player['before_Team'] = 'Miami OH'
        if "Omaha" in player['before_Team']:
            player['before_Team'] = 'Nebraska Omaha'

        team.append(player['before_Team'])
        team.append(year)
        new_team_list.append(team)
    new_all_data = scrape_mul_teams(new_team_list)

    if not new_all_data.empty:
        os.makedirs('processed', exist_ok=True)
        transfer_file_path = 'processed/team_stats.csv'
        new_all_data.to_csv(transfer_file_path, index=False)
    else:
        print('No transfers found')

    team_list = []
    for index, player in transfer_data.iterrows():
        team = []
        year = player['Season']
        year = year[:2] + year[5:]
        if 'State' in player['Team']:
            player.replace('State', 'St.', regex=True, inplace=True)
        if 'Louisiana St.' in player['Team']:
            player['Team'] = 'LSU'
        if 'Gardner-Webb' in player['Team']:
            player['Team'] = 'Gardner Webb'
        if 'TexasâRio Grande Valley' in player['Team']:
            player['Team'] = 'UT Rio Grande Valley'
        if "St. Mary's (CA)" in player['Team']:
            player['Team'] = "Saint Mary's"
        if "Miami (FL)" in player['Team']:
            player['Team'] = "Miami FL"
        if "Queens (NC)" in player['Team']:
            player['Team'] = "Queens"
        if "St. John's (NY)" in player['Team']:
            player['Team'] = "St. John's"
        if "Loyola (MD)" in player['Team']:
            player['Team'] = "Loyola MD"
        if "Texas A&MâCommerce" in player['Team']:
            player['Team'] = "East Texas A&M"
        if "ArkansasâPine Bluff" in player['Team']:
            player['Team'] = "Arkansas Pine Bluff"
        if "Ole Miss" in player['Team']:
            player['Team'] = "Mississippi"
        if "Central Connecticut St." in player['Team']:
            player['Team'] = "Central Connecticut"
        if "IllinoisâChicago" in player['Team']:
            player['Team'] = "Illinois Chicago"
        if "FDU" in player['Team']:
            player['Team'] = "Fairleigh Dickinson"
        if "Florida International" in player['Team']:
            player['Team'] = "FIU"
        if "Southern California" in player['Team']:
            player['Team'] = "USC"
        if "Brigham Young" in player['Team']:
            player['Team'] = "BYU"
        if "College of Charleston" in player['Team']:
            player['Team'] = "Charleston"
        if "Saint Francis (PA)" in player['Team']:
            player['Team'] = "St. Francis PA"
        if "NC St." in player['Team']:
            player['Team'] = "N.C. State"
        if "UT Martin" in player['Team']:
            player['Team'] = "Tennessee Martin"
        if "Pennsylvania" in player['Team']:
            player['Team'] = "Penn"
        if "Southern Mississippi" in player['Team']:
            player['Team'] = "Southern Miss"
        if "Bethune-Cookman" in player['Team']:
            player['Team'] = "Bethune Cookman"
        if "St. Francis Brooklyn" in player['Team']:
            player['Team'] = "St. Francis NY"
        if "SIU Edwardsville" in player['Team'] and year == '2025':
            player['Team'] = "SIUE"
        if "LouisianaâMonroe" in player['Team']:
            player['Team'] = 'Louisiana Monroe'
        if "Texas A&MâCorpus Christi" in player['Team']:
            player['Team'] = 'Texas A&M Corpus Chris'
        if "Albany (NY)" in player['Team']:
            player['Team'] = 'Albany'
        if "Miami (OH)" in player['Team']:
            player['Team'] = 'Miami OH'
        if "Omaha" in player['Team']:
            player['Team'] = 'Nebraska Omaha'

        team.append(player['Team'])
        team.append(year)
        team_list.append(team)
    all_data = scrape_mul_teams(team_list)

    if not all_data.empty:
        os.makedirs('processed', exist_ok=True)
        transfer_file_path = 'processed/team_stats2.csv'
        all_data.to_csv(transfer_file_path, index=False)
    else:
        print('No transfers found')





# def scrape_player_page(Team, Year):
#     url = f'https://barttorvik.com/team.php?year={Year}&team={Team}'
#     print(f'Scraping data for {Team}')
#     team_stats = pd.DataFrame()
#
#     time.sleep(3)
#
#     response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
#     response.raise_for_status()
#     soup = BeautifulSoup(response.text, 'html.parser')
#
#     if 'Verifying Browser...' in soup.title.string:
#         print('switching to sleneium')
#
#         options = webdriver.ChromeOptions()
#         options.add_argument('--headless')
#
#         driver = webdriver.Chrome(options=options)
#         driver.get(url)
#         time.sleep(5)
#         page_source = driver.page_source
#         soup = BeautifulSoup(page_source, 'html.parser')
#         driver.quit()
#
#     rank = soup.find('td', id='rk')
#     if rank:
#         team_rank = rank.text.strip()
#         team_stats['rank'] = team_rank
#     else:
#         print('found nothing')
#         return pd.DataFrame()

    # if not rank:
    #     print(f'Couldnt find per game table for {Team}')
    #     return pd.DataFrame()
    # else:
    #     for parent_row in rank.parents:
    #         if parent_row.name == 'tr':
    #             break

# scrape_player_page('Houston', '2025')