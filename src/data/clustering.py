import os
os.environ["OMP_NUM_THREADS"] = '10'

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from kneed import KneeLocator


transfer_df = pd.read_csv('processed/transfers_stats_before_after.csv')
cluster_df = transfer_df.copy()
cluster_df[cluster_df['3P%'].str.isalpha()] = 0
cluster_df = cluster_df[[
    'FG%', '3P%', '2P%', 'eFG%', 'FT%', 'TS%', 'PER', '3PAr', 'FTr', 'ORB%', 'DRB%',
    'TRB%', 'AST%', 'STL%', 'BLK%', 'TOV%', 'USG%', 'WS/40', 'OBPM', 'DBPM', 'BPM'
]]

cluster_df = cluster_df.replace('Unknown', 0)
cluster_df = cluster_df.fillna(0)

scaler = StandardScaler()
cluster_scaled = scaler.fit_transform(cluster_df)

k_values = range(1, 11)
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