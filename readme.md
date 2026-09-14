# Research Question

> Generally, what knife is the most effective weapon in experienced Team Fortress 2 lobbies?

Team Fortress 2 (abbreviated to tf2) is a first person shooter game. Each class has various unlockable weapons that can be substituted for their base forms.

In this project, we will explore the weapons of one class: the Spy. The class has a total of five options for knives (excluding cosmetics, which do not affect gameplay) and each have their own strengths and weaknesses. For example, the "Big Earner" lowers the Spy's health, but grants a speed boost after a backstab.

Although this question serves no broad societal purpose or commentary, and does not matter to the majority of the population, tf2 has a small and dedicated playerbase who want to perform to the best of their abilities.  Identifying the option that gives players the biggest advantage would be extremely useful to any who seek to improve their tf2 results. The target audience for tf2 players looking to learn more about the game. Not only does this apply to Spy players, who will be searching for the best knife they can use, but this applies to any player looking to counter Spy, as they should practice most against his strongest option.

# Data Description / Key Variables

To determine the most effective knife, we will be looking at a few variables. The first is the kills-to-deaths ratio. Across the match, how many players did the knife kill? How many times did the Spy die? This will provide a fair assessment of how the spy performed in their match.

We will also be investigating how much damage the knife dealt across the match duration. The benefit of this metric is to determine if the Spy was killing players who were a key threat, or if the Spy was picking off already weak players. This is the less important metric, due to the way the Spy's knife works. A backstab (hit from a players back 180 degrees) will always instantly kill the target, regardless of how much health they had remaining. So, a Spy may get 20 kills, but if each kill was already low health, the damage will reflect poorly. However, on the other extreme, if the Spy exclusively kills high-health Heavys (a class with the largest health pool), then this metric will be inflated.

Importantly, since all knives share the same backstab mechanic, and the predominate usage of knives *is* to backstab, damage between knives should be comparable. The two differences being the amount of kills and the "quality" of the kills, so to speak. Since kills-to-death ratio (henceforth abbreviated as KDR) already accounts for kills, the damage metric will be somewhat redundant.

# Dataset

The dataset was gathered through the api [logs.tf](https://logs.tf/). The website is a place for players to submit log files to add to the database. Our dataset was acquired by polling the api and scanning the resulting game data.

The api provides two main endpoints. Firstly, the api provides a way of retrieving a list of games played. This includes (exhaustively):

1. The match identifier.
2. The name of the map the match was played on (this includes the mode).
3. The title of the match (not useful to us).
4. The timestamp of the match (not useful to us).
5. The number of times the match was queried (not useful to us).
6. The number of players in the match (redundant).

The other endpoint the api provides is to retrieve match-specific data. We are not concerned with the overall match data. Instead, we focus on the player performance metrics. For every player, the api has a per-class breakdown of how the player did. This includes, but is not limited to:

1. The class the player played.
2. The number of kills they got.
3. The number of deaths they had.
4. Their total damage output.
5. The total time they played the class.

Additionally, the class breakdown also includes a per-weapon breakdown, listing:

1. Name of the weapon.
2. Damage of the weapon.
3. Average damage of the weapon over the match.

We analyze all of this data and collect it all into a table.
| game_id | map | game_type | player_id | weapon | kills | dmg | avg_dmg | deaths | total_time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 4120525 | cp_process_f12 | capture_point | [U:1:1145622737] | letranger | 0 | 0 | 0.0 | 1 | 46 |
| 4120520 | cp_snakewater_final1 | capture_point | [U:1:420680524] | letranger | 1 | 42 | 42.0 | 0 | 32 |

The size of the dataset was limited to the runtime of the api polling script.

# Data Cleaning

First, we remove all entries for weapons we do not care about.

```python
# Only keep weapons we care about
WEAPON_WHITELIST = {"knife", "kunai", "spy_cicle", "eternal_reward", "big_earner"}
df = df[df["weapon"].isin(WEAPON_WHITELIST)]
```

Before this step, the data included weapons such as the "Crusader's Crossbow". Notably, the Crusader's Crossbow is not a Spy weapon.
> The Crusader's Crossbow is a community-created primary weapon for the Medic. [^1]

[^1]: https://wiki.teamfortress.com/wiki/Crusader%27s_Crossbow

Additionally, the data also included the Spy's other weapons, such as various pistols. The simplest solution was to only analyze weapons from a predetermined list of Spy knives.

Next, we precalculate the kdr from the `kills` and `deaths` fields.

```python
# Calculate KDR
df["kdr"] = df["kills"] / df["deaths"].replace(0, 1)
```

# The Data

![this is a graph](FigureCapturePoint.png)

*Capture Point matches*

![this is a graph](FigurePayload.png)

*Payload matches*

> Explain the patterns, trends, or anomalies each graphic reveals

Snick

Connect your visual findings back to your research question.

Explain what story the data tells and what conclusions would be incorrect to draw.

# Ethics and Limitations

This dataset cannot perfectly represent the research question. “Experienced tf2 lobbies” are completely subjective and cannot be quantified. Does every player having 20 hours make them experienced? 50? 100? There is no way to be sure. However, a fair amount of work must be put in to reach a tf2 private server, so it is a decent benchmark of experience.

Furthermore, this private server does not represent all experienced tf2 players. Many tf2 players exclusively play in a tournament setting, which this server does not capture. There are also certain modes of play not covered, like a deathmatch (without respawns) and highlander (limit to one of each class).

The greatest limitation of this dataset is that there is no way to account for individual player skill. While one knife may be weaker than another, if there is an incredibly skillful player who uses what might be a weaker knife, the actual potential of the weapon will not be reflected in the dataset. I can only hope that the sheer sample size is enough to minimize the effect of outlier players in the dataset.

# Code and Transparency

[My GitHub Repository](https://github.com/StephenHeagarty/Project1)

I used AI to assist me in creating the graphs to represent my data. I used the default ChatGPT version with the prompt:
> given the following csv header game_id,map,game_type,player_id,weapon,kills,dmg,avg_dmg,deaths,total_time, using python pd and mpl create a boxplot graph of weapon name vs. kills/deaths and weapon name vs avg_dmg

I am not very experienced with the libraries Seaborn and Matplotlib. It was faster to generate the code and review it for understanding.

This was the only instance of AI usage in the project.