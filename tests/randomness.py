import sys
import random
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

sys.path.insert(1, "./")
import pyaces as pyc

debug = True

# Initialize Repartition and ArithChannel
repartition = pyc.Repartition(n=5, p=2, upperbound=47601551)
repartition.construct()
ac = pyc.ArithChannel(p=4, N=10, deg_u=3, repartition=repartition)
public = ac.publish(publish_levels=True)

# Initialize Alice and Bob
alice = pyc.ACESReader(ac, debug=debug)
bob = pyc.ACES(**public, debug=debug)

# Generate embeddings and labels
bob_embeddings = []
alice_embeddings = []
colors_int = []

for _ in range(2000):
    m = random.randrange(ac.p)
    colors_int.append(m)
    
    bob_cip = bob.encrypt(m)
    bob_pseudo = bob_cip.pseudo()
    bob_embeddings.append((bob_pseudo.enc, *bob_pseudo.dec))
    
    alice_cip = alice.encrypt(m)
    alice_pseudo = alice_cip.pseudo()
    alice_embeddings.append((alice_pseudo.enc, *alice_pseudo.dec))

# Convert to NumPy arrays
bob_embeddings = np.array(bob_embeddings)
alice_embeddings = np.array(alice_embeddings)
colors_int = np.array(colors_int)

# Perform PCA to reduce to 3 dimensions
pca = PCA(n_components=3)
bob_pca = pca.fit_transform(bob_embeddings)
alice_pca = pca.fit_transform(alice_embeddings)

# Define colors for classes
color_map = {0: 'r', 1: 'g', 2: 'b', 3: 'y'}
colors = [color_map[c] for c in colors_int]

# Create 3D plots
fig = plt.figure(figsize=(12, 6))
ax1 = fig.add_subplot(121, projection='3d')
ax2 = fig.add_subplot(122, projection='3d')

# Plot Bob's embeddings
scatter1 = ax1.scatter(bob_pca[:, 0], bob_pca[:, 1], bob_pca[:, 2], c=colors, alpha=0.6)
ax1.set_title("Bob's PCA Embeddings")

# Plot Alice's embeddings
scatter2 = ax2.scatter(alice_pca[:, 0], alice_pca[:, 1], alice_pca[:, 2], c=colors, alpha=0.6)
ax2.set_title("Alice's PCA Embeddings")

# Add legend
import matplotlib.patches as mpatches
legend_patches = [mpatches.Patch(color=color_map[i], label=f'm = {i}') for i in color_map]
ax1.legend(handles=legend_patches, title="Message Value (m)")
ax2.legend(handles=legend_patches, title="Message Value (m)")

plt.show()