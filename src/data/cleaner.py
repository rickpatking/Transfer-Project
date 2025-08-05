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
all_transfers = pd.read_csv('processed/identified_transfers.csv')
all_transfers = pd.DataFrame(all_transfers)
all_transfers.columns = ['player_id']
all_transfers.to_csv('processed/identified_transfers.csv', index=False)