import os
os.environ["OMP_NUM_THREADS"] = '10'

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from kneed import KneeLocator
import joblib


transfer_df = pd.read_csv('../../data/interim/current_transfers_stats.csv')
precluster_df = transfer_df.copy()
precluster_df = precluster_df[precluster_df['Season'].str.contains('2024-25')]
precluster_df = precluster_df[precluster_df['G_y'] != 'Did not play - juco']
precluster_df = precluster_df.reset_index(drop=True)
precluster_df = precluster_df.fillna({'3P%': 'Unknown'})
precluster_df.loc[precluster_df['3P%'].str.isalpha(), '3P%'] = 0
cluster_df = precluster_df[[
    'FG%', '3P%', '2P%', 'eFG%', 'FT%', 'TS%', 'PER', '3PAr', 'FTr', 'ORB%', 'DRB%',
    'TRB%', 'AST%', 'STL%', 'BLK%', 'TOV%', 'USG%', 'WS/40', 'OBPM', 'DBPM', 'BPM'
]]

cluster_df = cluster_df.replace('Unknown', 0)
cluster_df = cluster_df.fillna(0)

scaler = StandardScaler()
cluster_scaled = scaler.fit_transform(cluster_df)

k_values = range(1, 15)
inertia = []
for k in k_values:
    kmeans = KMeans(n_clusters=k, n_init='auto', random_state=0)
    kmeans.fit(cluster_scaled)

    inertia.append(kmeans.inertia_)
kl = KneeLocator(k_values, inertia, S=1.0, curve='convex', direction='decreasing')

clustering_kmeans = KMeans(n_clusters=kl.elbow, n_init='auto', random_state=0)
cluster_labels = clustering_kmeans.fit_predict(cluster_scaled)

pca_num_components = 2
reduced_data = PCA(n_components=pca_num_components).fit_transform(cluster_scaled)
results = pd.DataFrame(reduced_data, columns=['pca1', 'pca2'])
results['cluster'] = cluster_labels
sns.scatterplot(x='pca1', y='pca2', hue='cluster', data=results, s=30)
plt.title('K-means clustering with 2 dimensions')
plt.show()

joblib.dump(clustering_kmeans, '../../models/kmeans.pkl')

clustered_df = cluster_df.copy()
clustered_df = clustered_df.astype(float)
clustered_df['cluster'] = cluster_labels

cluster_means = clustered_df.groupby('cluster').mean()
cluster_medians = clustered_df.groupby('cluster').median()

# cluster_means.to_csv('processed/cluster_means.csv')
# cluster_medians.to_csv('processed/cluster_medians.csv')

precluster_df['cluster'] = cluster_labels
# precluster_df.to_csv('processed/current_transfers_stats_clusters.csv', index=False)