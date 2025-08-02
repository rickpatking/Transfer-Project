import random

import requests
from bs4 import BeautifulSoup, Comment
import pandas as pd
import time
import os

from six import StringIO


def scrape_player_page(player_id):
    url = f'https://www.sports-reference.com/cbb/players/{player_id}.html'
    print(f'Scraping data for {player_id}')

    time.sleep(3)

    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        per_game_table = soup.find('table', id='players_per_game')

        if not per_game_table:
            print(f'Couldnt find per game table for {player_id}')
            return pd.DataFrame()
        # else:
        #     for row in per_game_table.find_all('tr')[1:]:
        #         link = row.find('a')

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

    except requests.exceptions.RequestException as e:
        print(f'Error scraping {url}: {e}')
        return pd.DataFrame()

def scrape_all_players(player_id_list):
    all_player_stats = []

    for player_id in player_id_list:
        player_df = scrape_player_page(player_id)
        if not player_df.empty and len(player_df) > 2:
            all_player_stats.append(player_df)

    if all_player_stats:
        combined_df = pd.concat(all_player_stats, ignore_index=True)
        return combined_df
    else:
        return pd.DataFrame()

def identify_transfers(df):
    # df_clean = df[df['Season'].str.contains('-')]
    df_clean = df.sort_values(by=['player_id', 'Season'])
    df_clean['previous_school'] = df_clean.groupby('player_id')['Team'].shift(1)

    transfers_df = df_clean[df_clean['School'] != df_clean['previous_school']]
    transfers_df = transfers_df[transfers_df['previous_school'].notna()]
    return transfers_df

if __name__ == '__main__':
    player_id_list = pd.read_csv('interim/all_cbb_player_ids.csv')
    df_raw = scrape_all_players(player_id_list['player_id'].tolist())
    df_transfers = identify_transfers(df_raw)

    if not df_transfers.empty:
        os.makedirs('processed', exist_ok=True)
        transfer_file_path = 'processed/identified_transfers.csv'
        df_transfers.to_csv(transfer_file_path, index=False)
        print(f'Found and saved {len(df_transfers)} transfers to {transfer_file_path}')
    else:
        print('No transfers found')

# print(scrape_player_page('deivon-smith-1'))