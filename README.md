# Mystery Island: The Lost Lighthouse

A text-adventure game for the terminal. You wake up on Mystery Island after a
storm. The lighthouse is dark and the bridge is rotten. Find what you need,
cross the bridge, and light the beacon before your energy runs out.

## Prerequisites

- Python 3.8 or newer (built and tested with Python 3.13)
- Nothing to install: only the standard library is used

## How to runplyed

```
python main.py
```

Type the number of a menu choice and press Enter. Type `q` (or `quit` / `exit`)
at any time to quit. Spaces and capital letters are ignored.

## How to run the tests

```
python -m unittest discover -s tests -v
```

## Map and moves

```
Beach <----> Jungle
  |             |
  |  (cliff)    |
  +-----------> Cave <----> Old Bridge ----(cross, needs rope)----> Lighthouse
```

| From | You can walk to |
|---|---|
| Beach | Jungle, Cave (cliff shortcut) |
| Jungle | Beach, Cave |
| Cave | Jungle, Old Bridge, Beach (cliff shortcut) |
| Old Bridge | Cave (and `cross` to the Lighthouse) |
| Lighthouse | Old Bridge |

You cannot walk straight to the Lighthouse. Only crossing the bridge gets you there.

## Items and where to find them

- **Rope**: in the Jungle. Needed to cross the bridge.
- **Lantern**: in the Cave. Needed to light the beacon.
- Each item can be picked up only once. Picking up is free.

## Energy rules

- Energy starts at 5 and can never go above 5.
- **Every walk and every bridge crossing costs 1 energy.** Arriving somewhere
  is not charged separately: the *move* is what costs energy.
- There is no free starting action.
- Picking up items, eating, drinking and lighting the beacon are free.
- Blocked or invalid actions are free and change nothing.
- Energy never goes below 0.

## Decisions with consequences

1. **Cliff shortcut (Beach <-> Cave).** It skips the Jungle, so you reach the
   lantern fast but you must walk back to the Jungle for the rope. Without
   extra energy you will run out before the Lighthouse.
2. **Jungle fruit.** Eating it gives +2 energy (up to 5), once only. Eating
   when your energy is full wastes it, so timing matters.
3. **Cave pool.** Drinking gives +1 energy (up to 5), once only, and the
   same timing rule applies.

## Win and lose conditions

- **Win:** be at the Lighthouse holding the lantern and choose "Light the
  beacon". Lighting is free, but you must get there with at least 1 energy.
- **Lose:** energy reaches 0. If the move that uses your last energy point
  brings you to the Lighthouse, you still lose: the game ends before you can
  light the beacon.
- **Quit:** type `q`. This is neither a win nor a loss.
- After any ending you are asked whether to play again. A replay starts a
  brand-new game: Beach, 5 energy, empty inventory.

## Rejected input

These are all rejected with a friendly message and the game state is unchanged
(no energy used, location and inventory the same):

- A blank line or only spaces
- Words that are not a menu choice (for example `banana`)
- Numbers outside the menu (`0`, `99`, `-1`) and decimals (`1.5`)

## Player state

```python
player = {
    "name": "Ada",
    "location": "Beach",
    "energy": 5,
    "inventory": [],   # list of item names, for example ["rope"]
    "used": [],        # one-time actions already used: "fruit", "pool"
    "game_over": False,
    "won": False,
}
```

The one addition to the recommended example is `used`, which remembers that the
fruit and the pool have already been used.

## Files

- `main.py`: reads the keyboard and prints text. Contains no game rules.
- `game.py`: all the rules (`new_game`, `available_actions`, `apply_action`,
  `parse_choice`, `can_cross_bridge`, `can_light_beacon`, `is_win`). It never
  calls `input()` or `print()`.
- `tests/test_game.py`: unit tests for the rules, including T1 to T10.

## Example winning run

Menu numbers change as items are picked up, so read the menu each turn. One
winning sequence of choices: walk to the Jungle, pick up the rope, walk to the
Cave, pick up the lantern, walk to the Old Bridge, cross the bridge, light the
beacon. That uses 4 energy and leaves 1.

## Known limits

- One fixed map and one fixed set of puzzles. There is no randomness.
- No save and load.
- There is no way to drop items or look at your inventory on its own. The
  status line shows it every turn.
- Menu numbers shift when options disappear (for example after picking up an
  item), so always read the menu before typing.
