"""Command-line front end for Mystery Island: The Lost Lighthouse.

This file only reads the keyboard and prints text. All rules live in game.py.
"""

from game import MAX_ENERGY, apply_action, available_actions, new_game, parse_choice

SCENES = {
    "Beach": "You are on the Beach. Wreckage is scattered along the sand. "
             "A steep cliff rises to the east.",
    "Jungle": "You are in the Jungle. Thick vines hang everywhere and a "
              "strange fruit tree grows nearby.",
    "Cave": "You are in the Cave. It is cool and dark, and a still pool "
            "glimmers near the wall. A tunnel leads on to the bridge.",
    "Old Bridge": "You stand at the Old Bridge. It spans a deep gorge, and the "
                  "far side is the Lighthouse. The planks look rotten.",
    "Lighthouse": "You are inside the Lighthouse. The great lamp at the top "
                  "is cold and dark.",
}

ITEM_TEXT = {
    "rope": "You coil up a strong length of rope.",
    "lantern": "You pick up an old lantern that still has oil in it.",
}


def ask(prompt, default_on_eof):
    """Read a line of input. If input ends (Ctrl+D), return default_on_eof."""
    try:
        return input(prompt)
    except EOFError:
        print()
        return default_on_eof


def describe_action(action, player):
    """Return the menu text for an action."""
    if action.startswith("go:"):
        place = action[3:]
        if {player["location"], place} == {"Beach", "Cave"}:
            return f"Climb the cliff to the {place} (shortcut)"
        return f"Walk to the {place}"
    if action.startswith("take:"):
        return f"Pick up the {action[5:]}"
    return {
        "eat": "Eat the strange fruit",
        "drink": "Drink from the cave pool",
        "cross": "Cross the old bridge to the Lighthouse",
        "light": "Light the beacon",
    }[action]


def result_message(result, action, player):
    """Return the text to show after an action."""
    if result == "picked_up":
        return ITEM_TEXT[action[5:]]
    if result == "already_have":
        return "You already took that."
    if result == "ate":
        return "The fruit is sweet and you feel stronger. (+2 energy, up to 5)"
    if result == "drank":
        return "The cold water refreshes you. (+1 energy, up to 5)"
    if result == "blocked_no_rope":
        return "The planks are rotten. You need a rope to cross safely."
    if result == "blocked_no_lantern":
        return "The lamp needs a flame. You have nothing to light it with."
    if result == "moved":
        return f"You make your way to the {player['location']}. (-1 energy)"
    if result == "lost":
        return f"You reach the {player['location']}, but your legs give way. (-1 energy)"
    return ""


def show_status(player):
    inventory = ", ".join(player["inventory"]) if player["inventory"] else "empty"
    print()
    print(f"[Energy: {player['energy']}/{MAX_ENERGY} | "
          f"Location: {player['location']} | Inventory: {inventory}]")
    print(SCENES[player["location"]])


def play(player):
    """Run one game until the player wins, loses or quits."""
    while not player["game_over"]:
        show_status(player)
        actions = available_actions(player)
        for number, action in enumerate(actions, start=1):
            print(f"  {number}. {describe_action(action, player)}")
        print("  q. Quit")

        raw = ask("What do you do? ", "q")
        action = parse_choice(raw, actions)
        if action is None:
            print("Sorry, that is not a choice. Type one of the numbers above, or q.")
            continue

        result = apply_action(player, action)
        message = result_message(result, action, player)
        if message:
            print(message)

    print()
    if player["won"]:
        print("You light the beacon. A rescue boat sees it and heads for the island.")
        print(f"YOU WIN, {player['name']}! You escaped Mystery Island.")
    elif player["energy"] == 0:
        print("You collapse on the sand and the night closes in.")
        print(f"YOU LOSE, {player['name']}. You ran out of energy.")
    else:
        print(f"You give up. Goodbye, {player['name']}.")


def ask_play_again():
    """Return True if the player wants another game."""
    while True:
        answer = ask("Play again? (y/n) ", "n").strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("Please type y or n.")


def main():
    print("=" * 40)
    print("   MYSTERY ISLAND: THE LOST LIGHTHOUSE")
    print("=" * 40)
    print("A storm has wrecked your ship. The lighthouse is dark and the")
    print("bridge is rotten. Find what you need and light the beacon so a")
    print("rescue boat can find you. Every walk costs 1 energy. If your")
    print("energy reaches 0, you lose. Type a menu number, or q to quit.")
    print()

    name = ask("What is your name? ", "").strip() or "Explorer"
    print(f"Welcome, {name}!")

    while True:
        play(new_game(name))
        if not ask_play_again():
            break
    print("Thanks for playing!")


if __name__ == "__main__":
    main()
