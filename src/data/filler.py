import pandas as pd

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

full_name_to_original_name = {
    'cameron haffner': 'cam haffner',
    'davin cosby jr': 'davin cosby',
    'naithan george': 'nait george',
    'allen david mukeba': 'allen mukeba',
    'nicholas boyd': 'nick boyd',
    'jerome brewer jr': 'jerome brewer',
    'george turkson jr': 'george turkson',
    'wesley yates iii': 'wesley yates',
    'robert wright': 'rob wright',
    'rodney brown jr': 'rodney brown',
    'barry dunning jr': 'barry dunning',
    'matthew reed': 'matt reed',
    'jaron pierrejr': 'jaron pierre',
    'vincent brady ii': 'vincent brady',
    'dan skillings': 'dan skillings jr',
    'melvin council jr': 'melvin council',
    'barrington hargress': 'barrington hargess',
    'adam njie jr': 'adam njie',
    'trey fort': 'trey fort iii',
    'juan cranford jr': 'juan cranford',
    'dennis parker jr': 'dennis parker',
    'marcus banks': 'marcus banks jr',
    'jamal west jr': 'jamal west',
    'ubong abasi etim': 'ubongabasi etim',
    'alfred worrell jr': 'alfred worrell',
    'chas kelley iii': 'chas kelley',
    'curtis givens iii': 'curtis givens',
    'james evans jr': 'james evans'
}

current_transfers = pd.read_csv('processed/current_transfers.csv')
current_transfers_stats = pd.read_csv('processed/current_transfers_stats_clusters.csv')
current_teams1 = pd.read_csv('processed/current_transfers_teams.csv')
current_teams2 = pd.read_csv('processed/current_transfers_teams_2.csv')

current_transfers_stats['standard_player'] = current_transfers_stats['player_id'].str.replace('-', ' ', regex=False).str.replace(r'\d+', '', regex=True).str.strip().str.lower()
for full, original in full_name_to_original_name.items():
    current_transfers_stats['standard_player'] = current_transfers_stats['standard_player'].str.replace(full, original, regex=False)
current_transfers['standard_player'] = current_transfers['player'].str.lower()

combined_transfers = pd.merge(current_transfers_stats, current_transfers, on='standard_player', how='left')
combined_transfers = combined_transfers.dropna()
combined_transfers = combined_transfers.rename(columns={'before_team': 'before_Team'})

combined_transfers[['new_university_name', 'new_team_name']] = combined_transfers['new_team'].apply(split_university_team)

for index, player in combined_transfers.iterrows():
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

current_teams1 = current_teams1.add_prefix('old_')
current_teams2 = current_teams2.add_prefix('new_')

current_cols = combined_transfers.columns.tolist()
new_order = ['Season', 'Team', 'Conf_x', 'Class_x', 'Pos_x', 'G_x', 'GS_x', 'MP_x', 'FG', 'FGA', 'FG%', '3P', '3PA', '3P%', '2P', '2PA', '2P%', 'eFG%', 'FT', 'FTA', 'FT%', 'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', 'Awards_x', 'Conf_y', 'Class_y', 'Pos_y', 'G_y', 'GS_y', 'MP_y', 'PER', 'TS%', '3PAr', 'FTr', 'PProd', 'ORB%', 'DRB%', 'TRB%', 'AST%', 'STL%', 'BLK%', 'TOV%', 'USG%', 'OWS', 'DWS', 'WS', 'WS/40', 'OBPM', 'DBPM', 'BPM', 'Awards_y', 'player_id', 'cluster', 'standard_player', 'player', 'new_team', 'new_university_name', 'new_team_name', 'before_Team']
combined_transfers = combined_transfers[new_order]

merged_df = pd.merge(
    combined_transfers,
    current_teams1,
    left_on='before_Team',
    right_on='old_team',
    how='left',
)

merged_df.drop_duplicates(inplace=True)
merged_df = merged_df.dropna()
merged_df.reset_index(inplace=True)

final_df = pd.merge(
    merged_df,
    current_teams2,
    left_on='new_university_name',
    right_on='new_team',
    how='left',
)

final_df.drop_duplicates(inplace=True)
final_df = final_df.dropna()
final_df.reset_index(inplace=True)

cong_stats = final_df.copy()
# print(cong_stats.columns)
cong_stats = cong_stats.drop(columns=['old_team', 'old_year', 'new_team_y', 'new_year'])

cong_stats['rank_change'] = cong_stats['new_rank'] - cong_stats['old_rank']
cong_stats['netrtg_change'] = cong_stats['new_netrtg'] - cong_stats['old_netrtg']
cong_stats['adjt_change'] = cong_stats['new_adjt'] - cong_stats['old_adjt']
cong_stats['luck_change'] = cong_stats['new_luck'] - cong_stats['old_luck']
cong_stats['sos_change'] = cong_stats['new_sos'] - cong_stats['old_sos']
cong_stats['sos_ooc_change'] = cong_stats['new_sos_ooc'] - cong_stats['old_sos_ooc']

cong_stats = cong_stats.dropna()
cong_stats = cong_stats

# print(cong_stats.columns)

position_dummies = pd.get_dummies(cong_stats['Pos_x'], prefix='Pos').astype(int)
class_dummies = pd.get_dummies(cong_stats['Class_x'], prefix='Class').astype(int)
cong_stats = pd.concat([cong_stats, position_dummies, class_dummies], axis=1)

# cong_stats = cong_stats.apply(pd.to_numeric, errors='coerce')

cong_stats = cong_stats.dropna(axis=1)
cong_stats.drop(columns=['level_0', 'index'], inplace=True)
# print(cong_stats.columns)

cong_stats.to_csv('processed/current_final_stats.csv', index=False)