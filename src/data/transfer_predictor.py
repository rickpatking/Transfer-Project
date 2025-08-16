import pandas as pd
import joblib
import numpy as np
from mistune.markdown import preprocess

from src.data.machine_learning import feature_importance


class TransferSuccessPredictor:
    def __init__(self):
        self.model = joblib.load('../../models/transfer_success_model.pkl')
        self.scaler = joblib.load('../../models/scaler.pkl')

        with open('../../models/feature_names.txt', 'r') as f:
            self.feature_names = [line.strip() for line in f]

    def preprocess_player_data(self, processed_data):
        # player_data = player_data[player_data['Season'].str.contains('2024-25')]
        # player_data = player_data[player_data['G_y'] != 'Did not play - juco']
        #
        # player_data.columns = [f'before_{col}' for col in player_data.columns]
        # player_data.rename(columns={'before_cluster': 'cluster'}, inplace=True)
        # player_data = player_data.reset_index(drop=True)
        #
        # team_stats1 = team_stats1.add_prefix('old_')
        # team_stats2 = team_stats2.add_prefix('new_')
        #
        # cong_stats = pd.concat([team_stats1, team_stats2], axis=1)
        # cong_stats = cong_stats.drop(columns=['old_team', 'old_year', 'new_team', 'new_year'])
        #
        # cong_stats['rank_change'] = cong_stats['new_rank'] - cong_stats['old_rank']
        # cong_stats['netrtg_change'] = cong_stats['new_netrtg'] - cong_stats['old_netrtg']
        # cong_stats['adjt_change'] = cong_stats['new_adjt'] - cong_stats['old_adjt']
        # cong_stats['luck_change'] = cong_stats['new_luck'] - cong_stats['old_luck']
        # cong_stats['sos_change'] = cong_stats['new_sos'] - cong_stats['old_sos']
        # cong_stats['sos_ooc_change'] = cong_stats['new_sos_ooc'] - cong_stats['old_sos_ooc']
        #
        # cong_stats2 = pd.concat([player_data, cong_stats], axis=1)
        # df_final = cong_stats2.dropna()
        #
        processed_data = pd.DataFrame([processed_data])

        for col in self.feature_names:
            if col not in processed_data.columns:
                processed_data[col] = 0

        X = processed_data[self.feature_names].copy()

        # numerical_cols = X.select_dtypes(include=[np.number]).columns
        # scaled_values = self.scaler.transform(X[numerical_cols])
        # X.loc[:, numerical_cols] = scaled_values.astype(float)

        numerical_cols = X.select_dtypes(include=[np.number]).columns

        if len(numerical_cols) > 0:
            X_new = pd.DataFrame(index=X.index)

            non_numerical_cols = X.select_dtypes(exclude=[np.number]).columns
            for col in non_numerical_cols:
                X_new[col] = X[col].values

            scaled_values = self.scaler.transform(X[numerical_cols].astype(float))
            scaled_df = pd.DataFrame(
                scaled_values,
                columns=numerical_cols,
                index=X.index,
                dtype=float
            )

            X_final = pd.concat([X_new, scaled_df], axis=1)

            X_final = X_final[self.feature_names]

            return X_final
        else:
            return X

    def predict_transfer_success(self, processed_data):
        processed_data = self.preprocess_player_data(processed_data)

        success_prob = self.model.predict_proba(processed_data)[0,1]
        prediction = self.model.predict(processed_data)[0]

        feature_importance = self.model.feature_importances_

        return {
            'success_probability': success_prob,
            'predicted_successful': bool(prediction),
            'confidence': 'High' if abs(success_prob - 0.5) > 0.3 else 'Medium' if abs(
                success_prob - 0.5) > 0.15 else 'Low',
            'key_factors': self._get_key_factors(processed_data, feature_importance)
        }

    def _get_key_factors(self, processed_data, importance):
        feature_values = processed_data.iloc[0]
        factor_scores = feature_values * importance

        top_factors = factor_scores.abs().nlargest(5)
        return {
            'positive_factors': [f for f in top_factors.index if factor_scores[f] > 0],
            'negative_factors': [f for f in top_factors.index if factor_scores[f] < 0]
        }

predictor = TransferSuccessPredictor()

transfers = pd.read_csv('processed/current_final_stats.csv')
# processed_transfers = predictor.preprocess_player_data(transfers)

successful_transfers = []
unsuccessful_transfers = []
all_transfers = []
for index, transfer in transfers.iterrows():
    # transfer = pd.DataFrame(transfer)
    result = predictor.predict_transfer_success(transfer)
    result['player'] = transfer['player_id']
    all_transfers.append(result)
    if result['predicted_successful']:
        successful_transfers.append(result)
    else:
        unsuccessful_transfers.append(result)

if successful_transfers:
    # successful_transfers = pd.concat(successful_transfers)
    successful_transfers = pd.DataFrame(successful_transfers)
    successful_transfers = successful_transfers.sort_values(by='success_probability', ascending=True)
    # successful_transfers.
    # print(successful_transfers['success_probability'])
    # print(successful_transfers['player'])
    # print(f"Success Probability: {result['success_probability']:.1%}")
    # print(f"Prediction: {'Successful' if result['predicted_successful'] else 'Unsuccessful'}")
    # print(f"Confidence: {result['confidence']}")
    # print(f'Player: {transfer['player_id']}')

all_transfers = pd.DataFrame(all_transfers)
all_transfers.to_csv('processed/transfer_success.csv')