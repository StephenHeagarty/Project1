import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("spy_capture_point.csv")

# Only keep weapons we care about
WEAPON_WHITELIST = {"knife", "kunai", "spy_cicle", "eternal_reward", "big_earner"}
df = df[df["weapon"].isin(WEAPON_WHITELIST)]

# Exclude 0 death 0 kill
df = df[(df["kills"] != 0) | (df["deaths"] != 0)]

# Calculate KDR
df["kdr"] = df["kills"] / df["deaths"].replace(0, 1)

fig, axes = plt.subplots(1, 2, figsize=(14, 7))

# Average damage
sns.violinplot(
    data=df,
    y="weapon",
    x="avg_dmg",
    ax=axes[0],
    color="skyblue",
    cut=0,
)

axes[0].set_title("Average Damage by Weapon")
axes[0].set_xlabel("Average Damage")
axes[0].set_ylabel("Weapon")
axes[0].grid(axis="x", alpha=0.3)

# KDR
sns.violinplot(
    data=df,
    y="weapon",
    x="kdr",
    ax=axes[1],
    color="lightgreen",
    cut=0,
)

axes[1].set_title("K/D Ratio by Weapon")
axes[1].set_xlabel("Kills / Deaths")
axes[1].set_ylabel("")
axes[1].grid(axis="x", alpha=0.3)

plt.tight_layout()
plt.show()
