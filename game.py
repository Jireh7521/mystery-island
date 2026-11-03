"""Game rules for Mystery Island: The Lost Lighthouse.

This module holds ONLY the rules. It never calls input() or print(), so every
function can be tested by calling it directly.

Actions are plain strings:
    "go:<Place>"    walk to a neighbouring place (costs 1 energy)
    "take:<item>"   pick up an item (free)
    "eat"           eat the jungle fruit (free, once)
    "drink"         drink from the cave pool (free, once)
    "cross"         cross the old bridge to the lighthouse (costs 1 energy)
    "light"         light the beacon (free, wins the game)
    "quit"          leave the game
"""

START_ENERGY = 5
MAX_ENERGY = 5
START_LOCATION = "Beach"

# Where you can walk from each place. The Lighthouse is NOT reachable with
# "go": you can only get there with "cross", which needs the rope.
MAP = {
    "Beach": ["Jungle", "Cave"],  # Beach -> Cave is the risky cliff shortcut
    "Jungle": ["Beach", "Cave"],
    "Cave": ["Jungle", "Old Bridge", "Beach"],
    "Old Bridge": ["Cave"],
    "Lighthouse": ["Old Bridge"],
}

# Which item lies in which place.
ITEM_LOCATIONS = {"rope": "Jungle", "lantern": "Cave"}

FRUIT_BONUS = 2  # energy gained by eating the jungle fruit
POOL_BONUS = 1   # energy gained by drinking from the cave pool


def new_game(name):
    """Return a brand-new player dictionary (fresh lists every time)."""
    return {
        "name": name,
        "location": START_LOCATION,
        "energy": START_ENERGY,
        "inventory": [],
        "used": [],  # one-time actions already used: "fruit", "pool"
        "game_over": False,
        "won": False,
    }


def can_cross_bridge(player):
    """True if the player has what the bridge needs. Changes nothing."""
    return "rope" in player["inventory"]


def can_light_beacon(player):
    """True if the player is at the Lighthouse holding the lantern."""
    return player["location"] == "Lighthouse" and "lantern" in player["inventory"]


def is_win(player):
    """True once the beacon has been lit."""
    return player["won"]


def available_actions(player):
    """Return the list of actions that make sense right now (no 'quit')."""
    if player["game_over"]:
        return []

    location = player["location"]
    actions = ["go:" + place for place in MAP[location]]

    for item, where in ITEM_LOCATIONS.items():
        if where == location and item not in player["inventory"]:
            actions.append("take:" + item)

    if location == "Jungle" and "fruit" not in player["used"]:
        actions.append("eat")
    if location == "Cave" and "pool" not in player["used"]:
        actions.append("drink")
    if location == "Old Bridge":
        actions.append("cross")
    if location == "Lighthouse":
        actions.append("light")
    return actions


def parse_choice(raw, actions):
    """Turn what the user typed into an action, or None if it is not valid.

    Accepts the menu number of one of `actions`, or q / quit / exit.
    Spaces and capital letters are ignored. Never changes any game state.
    """
    choice = raw.strip().lower()
    if choice in ("q", "quit", "exit"):
        return "quit"
    numbered = {str(number): action for number, action in enumerate(actions, start=1)}
    return numbered.get(choice)


def _spend_move(player, destination):
    """Move the player and pay 1 energy. Ends the game if energy hits 0."""
    player["location"] = destination
    player["energy"] -= 1
    if player["energy"] <= 0:
        player["energy"] = 0
        player["game_over"] = True
        return "lost"
    return "moved"


def apply_action(player, action):
    """Apply one action to the player and return a result code.

    Result codes: "moved", "lost", "picked_up", "already_have", "ate",
    "drank", "blocked_no_rope", "blocked_no_lantern", "won", "quit",
    "invalid", "game_over".

    Blocked and invalid actions never change the player and never cost energy.
    """
    if player["game_over"]:
        return "game_over"

    if action == "quit":
        player["game_over"] = True
        return "quit"

    if action.startswith("take:"):
        item = action[5:]
        if (ITEM_LOCATIONS.get(item) == player["location"]
                and item in player["inventory"]):
            return "already_have"

    if action not in available_actions(player):
        return "invalid"

    if action.startswith("go:"):
        return _spend_move(player, action[3:])

    if action.startswith("take:"):
        player["inventory"].append(action[5:])
        return "picked_up"

    if action == "eat":
        player["used"].append("fruit")
        player["energy"] = min(MAX_ENERGY, player["energy"] + FRUIT_BONUS)
        return "ate"

    if action == "drink":
        player["used"].append("pool")
        player["energy"] = min(MAX_ENERGY, player["energy"] + POOL_BONUS)
        return "drank"

    if action == "cross":
        if not can_cross_bridge(player):
            return "blocked_no_rope"
        return _spend_move(player, "Lighthouse")

    if action == "light":
        if not can_light_beacon(player):
            return "blocked_no_lantern"
        player["won"] = True
        player["game_over"] = True
        return "won"

    return "invalid"
