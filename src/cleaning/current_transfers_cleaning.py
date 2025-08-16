import pandas as pd
import requests
from bs4 import BeautifulSoup, Comment
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


def split_university_team(full_name):
    sorted_teams = sorted(team_names, key=len, reverse=True)

    for team in sorted_teams:
        if team in full_name:
            university = full_name.replace(team, "").strip()
            return pd.Series([university, team])

    university = full_name.rsplit(' ', 1)
    return pd.Series([university[0], university[1]])

team_names = [
    "Tar Heels", "Blue Devils", "Fighting Irish", "Crimson Tide",
    "Golden Eagles", "Red Storm", "Green Wave", 'Fighting Illini',
    'Golden Gophers', 'Sun Devils', 'Yellow Jackets', 'Demon Deacons',
    'Golden Bears', 'Ragin Cajuns', "Fightin' Blue Hens", 'Red Wolves',
    'Nittany Lions', 'Red Raiders', 'Mean Green', 'Scarlet Knights', 'Golden Panthers',
    'Blue Demons', "Runnin' Bulldogs", 'Horned Frogs', 'Wolf Pack'
]

if __name__ == '__main__':
    transfer_data = pd.read_csv('../../data/interim/current_transfers.csv')

    transfer_data[['new_university_name', 'new_team_name']] = transfer_data['new_team'].apply(split_university_team)

    team_list = []
    for index, player in transfer_data.iterrows():
        team = []
        year = 2025
        if 'State' in player['before_Team']:
            player.replace('State', 'St.', regex=True, inplace=True)
        if 'The University of Texas Rio Grande Valley' in player['before_Team']:
            player['before_Team'] = 'UT Rio Grande Valley'
        if "Miami" in player['before_Team']:
            player['before_Team'] = "Miami FL"
        if "Loyola (Chi)" in player['before_Team']:
            player['before_Team'] = "Loyola Chicago"
        if "Ole Miss" in player['before_Team']:
            player['before_Team'] = "Mississippi"
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
        if "Texas A & M University Corpus Christi" in player['before_Team']:
            player['before_Team'] = 'Texas A&M Corpus Chris'
        if "Miami (OH)" in player['before_Team']:
            player['before_Team'] = 'Miami OH'
        if "University of Nebraska at Omaha" in player['before_Team']:
            player['before_Team'] = 'Nebraska Omaha'
        if 'California St. University Northridge' in player['before_Team']:
            player['before_Team'] = 'Cal State Northridge'
        if 'Manhattan College' in player['before_Team']:
            player['before_Team'] = 'Manhattan'
        if 'George Washington University' in player['before_Team']:
            player['before_Team'] = 'George Washington'
        if 'New Jersey Institute of Technology' in player['before_Team']:
            player['before_Team'] = 'NJIT'
        if 'Grand Canyon University' in player['before_Team']:
            player['before_Team'] = 'Grand Canyon'
        if 'University of San Francisco' in player['before_Team']:
            player['before_Team'] = 'San Francisco'
        if 'University of South Carolina Upstate' in player['before_Team']:
            player['before_Team'] = 'USC Upstate'
        if 'University of California Riverside' in player['before_Team']:
            player['before_Team'] = 'UC Riverside'
        if 'Denver University' in player['before_Team']:
            player['before_Team'] = 'Denver'
        if 'Manhattan College' in player['before_Team']:
            player['before_Team'] = 'Manhattan'
        if 'Binghamton University' in player['before_Team']:
            player['before_Team'] = 'Binghamton'
        if 'Nicholls St.' in player['before_Team']:
            player['before_Team'] = 'Nicholls'
        if "Saint Mary's College of California" in player['before_Team']:
            player['before_Team'] = "Saint Mary's"
        if 'Utah Valley University' in player['before_Team']:
            player['before_Team'] = 'Utah Valley'
        if 'University of California San Diego' in player['before_Team']:
            player['before_Team'] = 'UC San Diego'
        if 'Middle Tennessee St.' in player['before_Team']:
            player['before_Team'] = 'Middle Tennessee'
        if "Saint Joseph's University" in player['before_Team']:
            player['before_Team'] = "Saint Joseph's"
        if 'California St. University Bakersfield' in player['before_Team']:
            player['before_Team'] = 'Cal St. Bakersfield'
        if 'University of Massachusetts Lowell' in player['before_Team']:
            player['before_Team'] = 'UMass Lowell'
        if 'McNeese St.' in player['before_Team']:
            player['before_Team'] = 'McNeese'
        if 'Virginia Military Institute' in player['before_Team']:
            player['before_Team'] = 'VMI'
        if 'St. Bonaventure University' in player['before_Team']:
            player['before_Team'] = 'St. Bonaventure'
        if 'Santa Clara University' in player['before_Team']:
            player['before_Team'] = 'Santa Clara'
        if 'USF' in player['before_Team']:
            player['before_Team'] = 'South Florida'
        if 'Missouri St. University' in player['before_Team']:
            player['before_Team'] = 'Missouri St.'
        if 'University of North Carolina Wilmington' in player['before_Team']:
            player['before_Team'] = 'UNC Wilmington'
        if 'Monmouth College' in player['before_Team']:
            player['before_Team'] = 'Monmouth'
        if 'Gonzaga University' in player['before_Team']:
            player['before_Team'] = 'Gonzaga'
        if 'Wisconsin Green Bay' in player['before_Team']:
            player['before_Team'] = 'Green Bay'
        if 'Bryant University' in player['before_Team']:
            player['before_Team'] = 'Bryant'
        if 'University of California Santa Barbara' in player['before_Team']:
            player['before_Team'] = 'UC Santa Barbara'
        if 'Stonehill College' in player['before_Team']:
            player['before_Team'] = 'Stonehill'
        if 'Cleveland St. University' in player['before_Team']:
            player['before_Team'] = 'Cleveland St.'
        if 'University of California Irvine' in player['before_Team']:
            player['before_Team'] = 'UC Irvine'
        if 'The University of Texas Arlington' in player['before_Team']:
            player['before_Team'] = 'UT Arlington'
        if 'Belmont University' in player['before_Team']:
            player['before_Team'] = 'Belmont'
        if 'Southeast Missouri St.' in player['before_Team']:
            player['before_Team'] = 'Southeast Missouri'

        team.append(player['before_Team'])
        team.append(year)
        team_list.append(team)
    all_data = scrape_mul_teams(team_list)

    if not all_data.empty:
        os.makedirs('../data/processed', exist_ok=True)
        transfer_file_path = '../../data/interim/current_transfers_teams.csv'
        all_data.to_csv(transfer_file_path, index=False)
    else:
        print('No transfers found')

    new_team_list = []
    for index, player in transfer_data.iterrows():
        team = []
        year = 2025
        if 'State' in player['new_university_name']:
            player.replace('State', 'St.', regex=True, inplace=True)
        if 'The University of Texas Rio Grande Valley' in player['new_university_name']:
            player['new_university_name'] = 'UT Rio Grande Valley'
        if "Miami" in player['new_university_name']:
            player['new_university_name'] = "Miami FL"
        if "Loyola (Chi)" in player['new_university_name']:
            player['new_university_name'] = "Loyola Chicago"
        if "Ole Miss" in player['new_university_name']:
            player['new_university_name'] = "Mississippi"
        if "College of Charleston" in player['new_university_name']:
            player['new_university_name'] = "Charleston"
        if "Saint Francis (PA)" in player['new_university_name']:
            player['new_university_name'] = "St. Francis PA"
        if "NC St." in player['new_university_name']:
            player['new_university_name'] = "N.C. State"
        if "UT Martin" in player['new_university_name']:
            player['new_university_name'] = "Tennessee Martin"
        if "Pennsylvania" in player['new_university_name']:
            player['new_university_name'] = "Penn"
        if "Texas A & M University Corpus Christi" in player['new_university_name']:
            player['new_university_name'] = 'Texas A&M Corpus Chris'
        if "Miami (OH)" in player['new_university_name']:
            player['new_university_name'] = 'Miami OH'
        if "University of Nebraska at Omaha" in player['new_university_name']:
            player['new_university_name'] = 'Nebraska Omaha'
        if 'California St. University Northridge' in player['new_university_name']:
            player['new_university_name'] = 'Cal State Northridge'
        if 'Manhattan College' in player['new_university_name']:
            player['new_university_name'] = 'Manhattan'
        if 'George Washington University' in player['new_university_name']:
            player['new_university_name'] = 'George Washington'
        if 'New Jersey Institute of Technology' in player['new_university_name']:
            player['new_university_name'] = 'NJIT'
        if 'Grand Canyon University' in player['new_university_name']:
            player['new_university_name'] = 'Grand Canyon'
        if 'University of San Francisco' in player['new_university_name']:
            player['new_university_name'] = 'San Francisco'
        if 'University of South Carolina Upstate' in player['new_university_name']:
            player['new_university_name'] = 'USC Upstate'
        if 'University of California Riverside' in player['new_university_name']:
            player['new_university_name'] = 'UC Riverside'
        if 'Denver University' in player['new_university_name']:
            player['new_university_name'] = 'Denver'
        if 'Manhattan College' in player['new_university_name']:
            player['new_university_name'] = 'Manhattan'
        if 'Binghamton University' in player['new_university_name']:
            player['new_university_name'] = 'Binghamton'
        if 'Nicholls St.' in player['new_university_name']:
            player['new_university_name'] = 'Nicholls'
        if "Saint Mary's College of California" in player['new_university_name']:
            player['new_university_name'] = "Saint Mary's"
        if 'Utah Valley University' in player['new_university_name']:
            player['new_university_name'] = 'Utah Valley'
        if 'University of California San Diego' in player['new_university_name']:
            player['new_university_name'] = 'UC San Diego'
        if 'Middle Tennessee St.' in player['new_university_name']:
            player['new_university_name'] = 'Middle Tennessee'
        if "Saint Joseph's University" in player['new_university_name']:
            player['new_university_name'] = "Saint Joseph's"
        if 'California St. University Bakersfield' in player['new_university_name']:
            player['new_university_name'] = 'Cal St. Bakersfield'
        if 'University of Massachusetts Lowell' in player['new_university_name']:
            player['new_university_name'] = 'UMass Lowell'
        if 'McNeese St.' in player['new_university_name']:
            player['new_university_name'] = 'McNeese'
        if 'Virginia Military Institute' in player['new_university_name']:
            player['new_university_name'] = 'VMI'
        if 'St. Bonaventure University' in player['new_university_name']:
            player['new_university_name'] = 'St. Bonaventure'
        if 'Santa Clara University' in player['new_university_name']:
            player['new_university_name'] = 'Santa Clara'
        if 'USF' in player['new_university_name']:
            player['new_university_name'] = 'South Florida'
        if 'Missouri St. University' in player['new_university_name']:
            player['new_university_name'] = 'Missouri St.'
        if 'University of North Carolina Wilmington' in player['new_university_name']:
            player['new_university_name'] = 'UNC Wilmington'
        if 'Monmouth College' in player['new_university_name']:
            player['new_university_name'] = 'Monmouth'
        if 'Gonzaga University' in player['new_university_name']:
            player['new_university_name'] = 'Gonzaga'
        if 'Wisconsin Green Bay' in player['new_university_name']:
            player['new_university_name'] = 'Green Bay'
        if 'Bryant University' in player['new_university_name']:
            player['new_university_name'] = 'Bryant'
        if 'University of California Santa Barbara' in player['new_university_name']:
            player['new_university_name'] = 'UC Santa Barbara'
        if 'Stonehill College' in player['new_university_name']:
            player['new_university_name'] = 'Stonehill'
        if 'Cleveland St. University' in player['new_university_name']:
            player['new_university_name'] = 'Cleveland St.'
        if 'University of California Irvine' in player['new_university_name']:
            player['new_university_name'] = 'UC Irvine'
        if 'The University of Texas Arlington' in player['new_university_name']:
            player['new_university_name'] = 'UT Arlington'
        if 'Belmont University' in player['new_university_name']:
            player['new_university_name'] = 'Belmont'
        if 'Southeast Missouri St.' in player['new_university_name']:
            player['new_university_name'] = 'Southeast Missouri'



        team.append(player['new_university_name'])
        team.append(year)
        new_team_list.append(team)
    new_all_data = scrape_mul_teams(new_team_list)

    if not new_all_data.empty:
        os.makedirs('../data/processed', exist_ok=True)
        transfer_file_path = '../../data/interim/current_transfers_teams_2.csv'
        new_all_data.to_csv(transfer_file_path, index=False)
    else:
        print('No transfers found')