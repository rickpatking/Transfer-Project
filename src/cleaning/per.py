import pandas as pd

transfer_df = pd.read_csv('../../data/interim/identified_transfers_stats.csv')
transfer_df = transfer_df[transfer_df['Team'] != transfer_df['previous_school']]
transfer_df = transfer_df[transfer_df['Season'].str.contains('0')]

# Get rid of guys who didn't play more than 2 games
transfer_df = transfer_df[transfer_df['G_y'] != 'Did not play - juco']
transfer_df = transfer_df[transfer_df['G_y'].astype(float) >= 2]

# find all rows with the same player_id and then subtract their PERs
transfer_df['previous_PER'] = transfer_df.groupby('player_id')['PER'].shift(1)
transfer_df['PER'] = transfer_df['PER'].astype(float)
transfer_df['previous_PER'] = transfer_df['previous_PER'].astype(float)
transfer_df['change_in_PER'] = transfer_df['PER'] - transfer_df['previous_PER']
# print(transfer_df)

before_df = transfer_df.groupby('player_id').shift(1)
# print(before_df['player_id'])
is_after_row = before_df['Season'].notna()
df_wide = transfer_df.loc[is_after_row].copy()
before_df = before_df.loc[is_after_row].copy()
before_df.columns = [f'before_{col}' for col in before_df.columns]
df_final = pd.concat([before_df, df_wide], axis=1)

df_final = df_final.drop(columns=['before_previous_school', 'before_previous_PER', 'before_change_in_PER'])
df_final = df_final.reset_index(drop=True)

df_final.to_csv('processed/transfers_stats_before_after.csv')


y = df_final['change_in_PER']

X = df_final.copy()

X = X[[
    'before_G_x', 'before_GS_x', 'before_Class_x', 'before_Pos_x',
    'before_MP_x', 'before_FG', 'before_FGA', 'before_FG%', 'before_3P', 'before_3PA',
    'before_3P%', 'before_2P', 'before_2PA', 'before_2P%', 'before_eFG%', 'before_FT',
    'before_FTA', 'before_FT%', 'before_ORB', 'before_DRB', 'before_TRB', 'before_AST',
    'before_STL', 'before_BLK', 'before_TOV', 'before_PF', 'before_PTS', 'before_TS%',
    'before_3PAr', 'before_FTr', 'before_PProd', 'before_ORB%', 'before_DRB%', 'before_TRB%',
    'before_AST%', 'before_STL%', 'before_BLK%', 'before_TOV%', 'before_USG%', 'before_OWS',
    'before_DWS', 'before_WS', 'before_WS/40', 'before_OBPM', 'before_DBPM', 'before_BPM'
]]

X['is_freshman'] = (X['before_Class_x'] == 'FR').astype(int)
X['is_sophomore'] = (X['before_Class_x'] == 'SO').astype(int)
X['is_junior'] = (X['before_Class_x'] == 'JR').astype(int)
X['is_senior'] = (X['before_Class_x'] == 'SR').astype(int)
X = X.drop(columns=['before_Class_x'])

X['is_guard'] = (X['before_Pos_x'] == 'G').astype(int)
X['is_forward'] = (X['before_Pos_x'] == 'F').astype(int)
X['is_center'] = (X['before_Pos_x'] == 'C').astype(int)
X = X.drop(columns=['before_Pos_x'])

X = X.apply(pd.to_numeric, errors='coerce')

# X.to_csv('processed/transfers_stats_before_after.csv')

# from sklearn.model_selection import train_test_split
# from sklearn.ensemble import RandomForestRegressor
#
# X = X.dropna()
# y = y.loc[X.index]
#
# X_train, X_test, y_train, y_test = train_test_split(
#     X, y, test_size=0.2, random_state=42
# )
#
# model = RandomForestRegressor(n_estimators=100, random_state=42)
# model.fit(X_train, y_train)
#
# y_pred = model.predict(X_test)
#
# from sklearn.metrics import mean_absolute_error, r2_score
#
# mae = mean_absolute_error(y_test, y_pred)
# print(f"Mean Absolute Error (MAE): {mae:.2f}")
#
# r2 = r2_score(y_test, y_pred)
# print(f"R-squared (R²): {r2:.2f}")
#
# import numpy as np
#
# feature_importances = model.feature_importances_
#
# feature_importance_df = pd.DataFrame({
#     'feature': X_train.columns,
#     'importance': feature_importances
# }).sort_values(by='importance', ascending=False)
#
# print("\nTop 10 Most Important Features:")
# print(feature_importance_df.head(10))