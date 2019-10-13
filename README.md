# MechMania25 Python Code - Team Kris Lindahl

## Performance
7th Place / 17 Teams (Top NDSU Team)

## Strategy
* We first attempted to implement a movement *tree search* through tiles based off of a policy function that attempted to find the strategic value of tiles. 
* After scrapping this idea due to difficulty of determining a strong policy function, we built a relatively simple system that moves to a tile that is within our attack pattern from a randomly determined nearby enemy or rock that is blocking us from the enemy units.
* Our code has built-in functions to prevent running into our units' future locations. `find_new_blocked_by_ally(self, our_location, blocks)`
* The next step to improve this bot would be implementing a system to identify the movement order of the opponent. This is difficult due to the ability to query the game-state only occurring between rounds. With this information we could optimize our attack orders and locations. *For a non random move order enemy this would lead to a **100%** increase in attacks that connect.* (**125%** increase for the common zero point move speed teams)
* We experimented with adding a small spread to our attack pattern. This **slightly increased** our win-rate against zero point move speed teams, but **significantly reduced** our power against fast bots similar to ours. With more optimization into not hitting our own bots with a spread, it may have been worthwhile.