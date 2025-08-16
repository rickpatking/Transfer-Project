import pandas as pd
import os
import requests
from bs4 import BeautifulSoup, Comment
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
from six import StringIO

def get_recent_transfers():
    url = 'https://www.on3.com/transfer-portal/wire/basketball/2025/'

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    while True:
        try:
            wait = WebDriverWait(driver, 10)
            load_more_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '.TransferPortalPage_btnLoadMore__JwJT3'))
            )
            driver.execute_script('arguments[0].click();', load_more_button)
        except Exception as e:
            print(f'No more products to load')
            print(f'{e}')
            break

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    driver.quit()

    all_ols = soup.find_all('ol', {'class': 'TransferPortalPage_transferPortalList__vbYpa' })
    if all_ols:
        transfers = pd.DataFrame(columns=['player', 'before_Team', 'Team'])
        for ol in all_ols:
            list_items = ol.find_all('li')
            for item in list_items:
                player = []
                link = item.find('div', class_='TransferPortalItem_playerStatusItem__srIrQ')
                if link.find('span').get_text(strip=True) == 'Committed' or link.find('span').get_text(strip=True) == 'Enrolled' or link.find('span').get_text(strip=True) == 'Signed':
                    name = item.find('a')
                    player.append(name.get_text(strip=True))

                    teams = item.find_all('img', class_='TransferPortalItem_teamLogo___on5w')
                    player.append(teams[0].get('title'))
                    player.append(teams[1].get('title'))
                if player:
                    transfers.loc[len(transfers)] = player

        return transfers

def scrape_player_page(old_player_id, before_team):
    id = 1
    going = True
    while going:
        time.sleep(3)
        player_id = old_player_id + f'-{id}'
        url = f'https://www.sports-reference.com/cbb/players/{player_id}.html'
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            player_stuff = soup.find('div', id='meta')
            if player_stuff:
                divs = player_stuff.find_all('div')
                if len(divs) > 1:
                    for team in divs[1].find_all('a'):
                        if team.text.strip()[:-6] == before_team:
                            going = False
                            break
                else:
                    if divs and divs[0].find_all('a'):
                        for team in divs[0].find_all('a'):
                            if team.text.strip()[:-6] == before_team:
                                going = False
                                break
                        # print(old_player_id, before_team)
                        # print('found nothing')
                        # return pd.DataFrame()
            id += 1
            continue
        except Exception as e:
            print(e)
            print(old_player_id, before_team)
            print('id error')
            return pd.DataFrame()

    print(f'Scraping data for {player_id}')

    time.sleep(1)

    per_game_table = soup.find('table', id='players_per_game')

    if not per_game_table:
        print(f'Couldnt find per game table for {player_id}')
        return pd.DataFrame()

    df_per_game = pd.read_html(StringIO(str(per_game_table)))[0]

    advanced_stats_table = None
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment_soup = BeautifulSoup(comment, 'html.parser')
        if comment_soup.find('table', id='players_advanced'):
            advanced_stats_table = comment_soup.find('table', id='players_advanced')
            break

    if advanced_stats_table:
        df_advanced = pd.read_html(StringIO(str(advanced_stats_table)))[0]
        df_combined = pd.merge(df_per_game, df_advanced, on=['Season', 'Team'], how='left')
    else:
        print(f'No advanced stats table for {player_id}')
        df_combined = df_per_game

    df_combined['player_id'] = player_id
    return df_combined

def scrape_all_players(player_id_team_list):
    all_player_stats = []

    for player_id in player_id_team_list:
        player_df = scrape_player_page(player_id[0], player_id[1])
        if not player_df.empty:
            player_df = player_df.fillna('Unknown')
            player_df = player_df[player_df['Season'].str.contains('-')]
            all_player_stats.append(player_df)

    if all_player_stats:
        combined_df = pd.concat(all_player_stats, ignore_index=True)
        return combined_df
    else:
        return pd.DataFrame()

def get_all_college_names(before_Teams, cur_year = 2025):
    url = 'https://www.sports-reference.com/cbb/schools/'

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    valid_colleges = pd.DataFrame(columns=['valid_teams'])
    invalid_colleges = pd.DataFrame(columns=['before_Team', 'valid_team'])

    schools_table = soup.find('table', id='NCAAM_schools')

    if schools_table:
        for row in schools_table.find_all('tr')[1:]:
            time.sleep(3)
            cols = row.find_all('td')
            if len(cols) > 5:
                end_year = cols[3].text.strip()
                if end_year == str(cur_year):
                    link = row.find('a')
                    if link:
                        print(f'scraping {link.text.strip()}')
                        if link.text.strip() in before_Teams:
                            print('valid team')
                            valid_colleges.loc[len(valid_colleges)] = link.text.strip()
                            # return valid_colleges
                        else:
                            print('invalid team')
                            num = len(invalid_colleges)
                            invalid_colleges.loc[num, 'valid_team'] = link.text.strip()
        # return invalid_colleges
        return valid_colleges, invalid_colleges

    return pd.DataFrame()








if __name__ == '__main__':
    # transfers = get_recent_transfers()
    transfers = pd.read_csv('data/processed/current_transfers2.csv')
    player_ids = []
    for index, transfer in transfers.iterrows():
        if 'California State University Northridge' in transfer['before_Team']:
            transfer['before_Team'] = 'Cal State Northridge'
        if 'Indiana University   Indianapolis' in transfer['before_Team']:
            transfer['before_Team'] = 'IU Indy'
        if 'Manhattan College' in transfer['before_Team']:
            transfer['before_Team'] = 'Manhattan'
        if 'Le Moyne College' in transfer['before_Team']:
            transfer['before_Team'] = 'Le Moyne'
        if 'LSU' in transfer['before_Team']:
            transfer['before_Team'] = 'Louisiana State'
        if 'Gardner Webb' in transfer['before_Team']:
            transfer['before_Team'] = 'Gardner-Webb'
        if 'Albany' in transfer['before_Team']:
            transfer['before_Team'] = 'Albany (NY)'
        if 'Binghamton University' in transfer['before_Team']:
            transfer['before_Team'] = 'Binghamton'
        if 'Bowling Green' in transfer['before_Team']:
            transfer['before_Team'] = 'Bowling Green State'
        if 'BYU' in transfer['before_Team']:
            transfer['before_Team'] = 'Brigham Young'
        if 'California State University Bakersfield' in transfer['before_Team']:
            transfer['before_Team'] = 'Cal State Bakersfield'
        if 'Cleveland State University' in transfer['before_Team']:
            transfer['before_Team'] = 'Cleveland State'
        if 'Delaware' in transfer['before_Team']:
            transfer['before_Team'] = 'Delaware State'
        if 'Denver University' in transfer['before_Team']:
            transfer['before_Team'] = 'Denver'
        if 'Fairleigh Dickinson' in transfer['before_Team']:
            transfer['before_Team'] = 'FDU'
        if 'George Washington University' in transfer['before_Team']:
            transfer['before_Team'] = 'George Washington'
        if 'Gonzaga University' in transfer['before_Team']:
            transfer['before_Team'] = 'Gonzaga'
        if 'Grand Canyon University' in transfer['before_Team']:
            transfer['before_Team'] = 'Grand Canyon'
        if 'Illinois Chicago' in transfer['before_Team']:
            transfer['before_Team'] = 'Illinois-Chicago'
        if 'Louisiana Monroe' in transfer['before_Team']:
            transfer['before_Team'] = 'Louisiana-Monroe'
        if 'Loyola (Chi)' in transfer['before_Team']:
            transfer['before_Team'] = 'Loyola (IL)'
        if 'Maryland Eastern Shore' in transfer['before_Team']:
            transfer['before_Team'] = 'Maryland-Eastern Shore'
        if 'Miami' in transfer['before_Team']:
            transfer['before_Team'] = 'Miami (FL)'
        if 'Middle Tennessee State' in transfer['before_Team']:
            transfer['before_Team'] = 'Middle Tennessee'
        if 'Missouri State University' in transfer['before_Team']:
            transfer['before_Team'] = 'Missouri State'
        if 'Monmouth College' in transfer['before_Team']:
            transfer['before_Team'] = 'Monmouth'
        if "Saint Joseph's University" in transfer['before_Team']:
            transfer['before_Team'] = "Saint Joseph's"
        if "Saint Mary's College of California" in transfer['before_Team']:
            transfer['before_Team'] = "Saint Mary's (CA)"
        if 'Sam Houston State' in transfer['before_Team']:
            transfer['before_Team'] = 'Sam Houston'
        if 'University of San Francisco' in transfer['before_Team']:
            transfer['before_Team'] = 'San Francisco'
        if 'Santa Clara University' in transfer['before_Team']:
            transfer['before_Team'] = 'Santa Clara'
        if 'University of South Carolina Upstate' in transfer['before_Team']:
            transfer['before_Team'] = 'South Carolina Upstate'
        if 'Southern Miss' in transfer['before_Team']:
            transfer['before_Team'] = 'Southern Mississippi'
        if 'St. Bonaventure University' in transfer['before_Team']:
            transfer['before_Team'] = 'St. Bonaventure'
        if "St. John's" in transfer['before_Team']:
            transfer['before_Team'] = "St. John's (NY)"
        if 'Stonehill College' in transfer['before_Team']:
            transfer['before_Team'] = 'Stonehill'
        if 'Texas A & M University Corpus Christi' in transfer['before_Team']:
            transfer['before_Team'] = 'Texas A&M-Corpus Christi'
        if 'The University of Texas Rio Grande Valley' in transfer['before_Team']:
            transfer['before_Team'] = 'Texas-Rio Grande Valley'
        if 'University of California Riverside' in transfer['before_Team']:
            transfer['before_Team'] = 'UC Riverside'
        if 'University of California San Diego' in transfer['before_Team']:
            transfer['before_Team'] = 'UC San Diego'
        if 'University of California Santa Barbara' in transfer['before_Team']:
            transfer['before_Team'] = 'UC Santa Barbara'
        if 'University of North Carolina Wilmington' in transfer['before_Team']:
            transfer['before_Team'] = 'UNC Wilmington'
        if 'Utah Valley University' in transfer['before_Team']:
            transfer['before_Team'] = 'Utah Valley'
        if 'USC' in transfer['before_Team']:
            transfer['before_Team'] = 'Southern California'
        if 'New Jersey Institute of Technology' in transfer['before_Team']:
            transfer['before_Team'] = 'NJIT'
        if 'USF' in transfer['before_Team']:
            transfer['before_Team'] = 'South Florida'
        if 'UNLV' in transfer['before_Team']:
            transfer['before_Team'] = 'Nevada-Las Vegas'
        if 'University of Nebraska at Omaha' in transfer['before_Team']:
            transfer['before_Team'] = 'Omaha'
        if 'Bryant University' in transfer['before_Team']:
            transfer['before_Team'] = 'Bryant'
        if 'Missouri Kansas City' in transfer['before_Team']:
            transfer['before_Team'] = 'Kansas City'
        if 'Wisconsin Green Bay' in transfer['before_Team']:
            transfer['before_Team'] = 'Green Bay'
        if 'VCU' in transfer['before_Team']:
            transfer['before_Team'] = 'Virginia Commonwealth'
        if 'Wisconsin Milwaukee' in transfer['before_Team']:
            transfer['before_Team'] = 'Milwaukee'
        if 'Delaware State' in transfer['before_Team']:
            transfer['before_Team'] = 'Delaware'
        if 'Ole Miss' in transfer['before_Team']:
            transfer['before_Team'] = 'Mississippi'
        if 'University of Massachusetts Lowell' in transfer['before_Team']:
            transfer['before_Team'] = 'Massachusetts-Lowell'
        if 'University of Maryland Baltimore County' in transfer['before_Team']:
            transfer['before_Team'] = 'Maryland-Baltimore County'
        if 'California State University Long Beach' in transfer['before_Team']:
            transfer['before_Team'] = 'Long Beach State'
        if 'University of North Carolina Asheville' in transfer['before_Team']:
            transfer['before_Team'] = 'UNC Asheville'
        if 'FIU' in transfer['before_Team']:
            transfer['before_Team'] = 'Florida International'
        if 'UT Martin' in transfer['before_Team']:
            transfer['before_Team'] = 'Tennessee-Martin'


        player_id = transfer['player'].lower()
        player_id = player_id.replace("'", '')
        player_id = player_id.replace('.', '')
        player_id = player_id.replace(' ', '-')
        if 'cam-haffner' in player_id:
            player_id = 'cameron-haffner'
        if 'davin-cosby' in player_id:
            player_id = 'davin-cosby-jr'
        if 'nait-george' in player_id:
            player_id = 'naithan-george'
        if 'allen-mukeba' in player_id:
            player_id = 'allen-david-mukeba'
        if 'nick-boyd' in player_id:
            player_id = 'nicholas-boyd'
        if 'jerome-brewer' in player_id:
            player_id = 'jerome-brewer-jr'
        if 'george-turkson' in player_id:
            player_id = 'george-turkson-jr'
        if 'wesley-yates' in player_id:
            player_id = 'wesley-yates-iii'
        if 'rob-wright' in player_id:
            player_id = 'robert-wright'
        if 'rodney-brown' in player_id:
            player_id = 'rodney-brown-jr'
        if 'barry-dunning' in player_id:
            player_id = 'barry-dunning-jr'
        if 'matt-reed' in player_id:
            player_id = 'matthew-reed'
        if 'jaron-pierre' in player_id:
            player_id = 'jaron-pierrejr'
        if 'vincent-brady' in player_id:
            player_id = 'vincent-brady-ii'
        if 'dan-skillings-jr' in player_id:
            player_id = 'dan-skillings'
        if 'melvin-council' in player_id:
            player_id = 'melvin-council-jr'
        if 'barrington-hargess' in player_id:
            player_id = 'barrington-hargress'
        if 'adam-njie' in player_id:
            player_id = 'adam-njie-jr'
        if 'trey-fort-iii' in player_id:
            player_id = 'trey-fort'
        if 'juan-cranford' in player_id:
            player_id = 'juan-cranford-jr'
        if 'dennis-parker' in player_id:
            player_id = 'dennis-parker-jr'
        if 'marcus-banks-jr' in player_id:
            player_id = 'marcus-banks'
        if 'jamal-west' in player_id:
            player_id = 'jamal-west-jr'
        if 'ubongabasi-etim' in player_id:
            player_id = 'ubong-abasi-etim'
        if 'alfred-worrell' in player_id:
            player_id = 'alfred-worrell-jr'
        if 'chas-kelley' in player_id:
            player_id = 'chas-kelley-iii'
        if 'curtis-givens' in player_id:
            player_id = 'curtis-givens-iii'
        if 'james-evans' in player_id:
            player_id = 'james-evans-jr'
        if 'reece-potter' in player_id:
            transfer['before_Team'] = 'Miami (OH)'
        if 'kam-craft' in player_id:
            transfer['before_Team'] = 'Miami (OH)'
        player_ids.append(player_id)
    transfers['player_id'] = player_ids

    player_id_team_list = []
    for index, transfer in transfers.iterrows():
        player_id_team_list.append([transfer['player_id'], transfer['before_Team']])


    current_transfers_stats = scrape_all_players(player_id_team_list)
    os.makedirs('processed', exist_ok=True)
    transfer_file_path = 'data/processed/current_transfers_stats2.csv'
    current_transfers_stats.to_csv(transfer_file_path, index=False)

    # all_teams = []
    # for play_id, team in player_id_team_list:
    #     all_teams.append(team)
    # all_teams = list(set(all_teams))

    # valid_teams, invalid_teams = get_all_college_names(all_teams)

    # os.makedirs('processed', exist_ok=True)
    # valid_teams.to_csv('processed/valid_teams.csv', index=False)
    # invalid_teams.to_csv('processed/invalid_teams.csv', index=False)
# potential idea for the future, get the rankings of the transfer class and compare it to my own