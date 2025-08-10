import pandas as pd

# transfer_df = pd.read_csv('processed/identified_transfers.csv')
# transfer_df = transfer_df.fillna('Unknown')
# # transfer_df = transfer_df[transfer_df['Season'].str.contains('-')]
# transfer_df['prev_school'] = transfer_df.groupby('player_id')['Team'].shift(1)
# # transfer_df['Pos_x'] = transfer_df.groupby('player_id')['Pos_x']
# search_values = ['(1 Yr)', '(2 Yr)', '(3 Yr)', '(4 Yr)', '(5 Yr)']
# pattern = '|'.join(search_values)
# transfer_df = transfer_df[transfer_df['Season'].str.contains(pattern)]
# transfer_df = transfer_df.drop('previous_school', axis=1)
# transfer_df = transfer_df.reset_index(drop=True)

# print(transfer_df['MP_x'])
# print(transfer_df)

# all_transfers = transfer_df['player_id'].unique()
# all_transfers = pd.read_csv('processed/identified_transfers.csv')
# all_transfers = pd.DataFrame(all_transfers)
# all_transfers.columns = ['player_id']
# all_transfers.to_csv('processed/identified_transfers.csv', index=False)

trans_clust = pd.read_csv('processed/transfers_stats_with_clusters.csv')
team_stats = pd.read_csv('processed/team_stats.csv')
team_stats2 = pd.read_csv('processed/team_stats2.csv')
team_stats = team_stats.add_prefix('old_')
team_stats2 = team_stats2.add_prefix('new_')

cong_stats = pd.concat([team_stats, team_stats2], axis=1)
cong_stats = cong_stats.drop(columns=['old_team', 'old_year', 'new_team', 'new_year'])

cong_stats['rank_change'] = cong_stats['new_rank'] - cong_stats['old_rank']
cong_stats['netrtg_change'] = cong_stats['new_netrtg'] - cong_stats['old_netrtg']
cong_stats['adjt_change'] = cong_stats['new_adjt'] - cong_stats['old_adjt']
cong_stats['luck_change'] = cong_stats['new_luck'] - cong_stats['old_luck']
cong_stats['sos_change'] = cong_stats['new_sos'] - cong_stats['old_sos']
cong_stats['sos_ooc_change'] = cong_stats['new_sos_ooc'] - cong_stats['old_sos_ooc']

cong_stats2 = pd.concat([trans_clust, cong_stats], axis=1)
cong_stats2 = cong_stats2.dropna()
cong_stats2 = cong_stats2.drop(columns=['Unnamed: 0.1', 'Unnamed: 0'])

cong_stats2.to_csv('processed/final_stats.csv', index=False)