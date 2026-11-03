import copy
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from game import (  # noqa: E402
    START_ENERGY,
    apply_action,
    available_actions,
    can_cross_bridge,
    can_light_beacon,
    is_win,
    new_game,
    parse_choice,
)


def player_at(location, inventory=None, energy=START_ENERGY):
    """Build a player standing at `location` for a test."""
    player = new_game("Tester")
    player["location"] = location
    player["inventory"] = list(inventory or [])
    player["energy"] = energy
    return player


class TestAcceptance(unittest.TestCase):
    def test_t1_new_game_start_state(self):
        player = new_game("Ada")
        self.assertEqual(player["location"], "Beach")
        self.assertEqual(player["energy"], 5)
        self.assertEqual(player["inventory"], [])
        self.assertFalse(player["game_over"])
        self.assertFalse(player["won"])

    def test_t2_invalid_command_changes_nothing(self):
        player = new_game("Ada")
        before = copy.deepcopy(player)
        self.assertEqual(apply_action(player, "banana"), "invalid")
        self.assertEqual(apply_action(player, ""), "invalid")
        self.assertEqual(player, before)

    def test_t3_legal_move_changes_location_and_costs_one_energy(self):
        player = new_game("Ada")
        result = apply_action(player, "go:Jungle")
        self.assertEqual(result, "moved")
        self.assertEqual(player["location"], "Jungle")
        self.assertEqual(player["energy"], 4)

    def test_t4_wrong_direction_is_rejected_without_cost(self):
        player = new_game("Ada")
        for bad in ("go:Old Bridge", "go:Lighthouse", "go:Atlantis"):
            self.assertEqual(apply_action(player, bad), "invalid")
        self.assertEqual(player["location"], "Beach")
        self.assertEqual(player["energy"], 5)

    def test_t5_rope_can_be_collected_only_once(self):
        player = player_at("Jungle")
        self.assertEqual(apply_action(player, "take:rope"), "picked_up")
        self.assertEqual(apply_action(player, "take:rope"), "already_have")
        self.assertEqual(player["inventory"], ["rope"])

    def test_t6_bridge_cannot_be_crossed_without_rope(self):
        player = player_at("Old Bridge", inventory=["lantern"])
        self.assertFalse(can_cross_bridge(player))
        self.assertEqual(apply_action(player, "cross"), "blocked_no_rope")
        self.assertEqual(player["location"], "Old Bridge")
        self.assertEqual(player["energy"], 5)

    def test_t7_lighthouse_cannot_be_lit_without_lantern(self):
        player = player_at("Lighthouse", inventory=["rope"])
        self.assertFalse(can_light_beacon(player))
        self.assertEqual(apply_action(player, "light"), "blocked_no_lantern")
        self.assertFalse(is_win(player))
        self.assertFalse(player["game_over"])

    def test_t8_correct_inventory_and_location_wins(self):
        player = player_at("Lighthouse", inventory=["rope", "lantern"], energy=1)
        self.assertEqual(apply_action(player, "light"), "won")
        self.assertTrue(is_win(player))
        self.assertTrue(player["game_over"])

    def test_t9_energy_exhaustion_causes_loss(self):
        player = player_at("Beach", energy=1)
        self.assertEqual(apply_action(player, "go:Jungle"), "lost")
        self.assertEqual(player["energy"], 0)
        self.assertTrue(player["game_over"])
        self.assertFalse(is_win(player))

    def test_t10_replay_resets_everything(self):
        old = new_game("Ada")
        old["location"] = "Cave"
        old["energy"] = 1
        old["inventory"].append("rope")
        fresh = new_game("Ada")
        self.assertEqual(fresh["location"], "Beach")
        self.assertEqual(fresh["energy"], 5)
        self.assertEqual(fresh["inventory"], [])
        self.assertIsNot(fresh["inventory"], old["inventory"])


class TestBugHunter(unittest.TestCase):
    def test_spaced_and_capitalised_exit_is_accepted(self):
        self.assertEqual(parse_choice(" EXIT ", ["go:Jungle"]), "quit")
        self.assertEqual(parse_choice(" Q ", ["go:Jungle"]), "quit")

    def test_menu_numbers_and_bad_menu_input(self):
        actions = ["go:Jungle", "go:Cave"]
        self.assertEqual(parse_choice(" 1 ", actions), "go:Jungle")
        self.assertEqual(parse_choice("2", actions), "go:Cave")
        for bad in ("banana", "", "0", "3", "-1", "1.5", "²"):
            self.assertIsNone(parse_choice(bad, actions))

    def test_energy_never_goes_negative(self):
        player = player_at("Beach", energy=1)
        apply_action(player, "go:Jungle")
        apply_action(player, "go:Beach")
        apply_action(player, "go:Jungle")
        self.assertEqual(player["energy"], 0)

    def test_cannot_act_after_game_over(self):
        player = player_at("Beach", energy=1)
        apply_action(player, "go:Jungle")
        before = copy.deepcopy(player)
        self.assertEqual(apply_action(player, "go:Beach"), "game_over")
        self.assertEqual(player, before)
        self.assertEqual(available_actions(player), [])

    def test_cannot_light_beacon_away_from_lighthouse(self):
        player = player_at("Cave", inventory=["rope", "lantern"])
        self.assertEqual(apply_action(player, "light"), "invalid")
        self.assertFalse(is_win(player))

    def test_cannot_take_item_from_wrong_place(self):
        player = new_game("Ada")
        self.assertEqual(apply_action(player, "take:rope"), "invalid")
        self.assertEqual(player["inventory"], [])

    def test_fruit_works_once_and_is_capped_at_max(self):
        player = player_at("Jungle", energy=2)
        self.assertEqual(apply_action(player, "eat"), "ate")
        self.assertEqual(player["energy"], 4)
        self.assertEqual(apply_action(player, "eat"), "invalid")
        self.assertEqual(player["energy"], 4)
        full = player_at("Jungle", energy=5)
        apply_action(full, "eat")
        self.assertEqual(full["energy"], 5)

    def test_quit_ends_game_without_winning(self):
        player = new_game("Ada")
        self.assertEqual(apply_action(player, "quit"), "quit")
        self.assertTrue(player["game_over"])
        self.assertFalse(is_win(player))

    def test_arriving_at_lighthouse_with_last_energy_is_a_loss(self):
        player = player_at("Old Bridge", inventory=["rope", "lantern"], energy=1)
        self.assertEqual(apply_action(player, "cross"), "lost")
        self.assertFalse(is_win(player))


class TestFullPlaythroughs(unittest.TestCase):
    def test_winning_path(self):
        player = new_game("Ada")
        steps = [
            ("go:Jungle", "moved"),
            ("take:rope", "picked_up"),
            ("go:Cave", "moved"),
            ("take:lantern", "picked_up"),
            ("go:Old Bridge", "moved"),
            ("cross", "moved"),
            ("light", "won"),
        ]
        for action, expected in steps:
            self.assertEqual(apply_action(player, action), expected)
        self.assertTrue(is_win(player))
        self.assertEqual(player["energy"], 1)

    def test_losing_path(self):
        player = new_game("Ada")
        results = [apply_action(player, a) for a in
                   ["go:Jungle", "go:Beach", "go:Jungle", "go:Beach", "go:Jungle"]]
        self.assertEqual(results[-1], "lost")
        self.assertTrue(player["game_over"])
        self.assertFalse(is_win(player))

    def test_cliff_shortcut_is_a_trap_without_fruit(self):
        player = new_game("Ada")
        for action in ["go:Cave", "take:lantern", "go:Jungle", "take:rope",
                       "go:Cave", "go:Old Bridge"]:
            apply_action(player, action)
        self.assertEqual(player["energy"], 1)
        self.assertEqual(apply_action(player, "cross"), "lost")
        self.assertTrue(player["game_over"])
        self.assertFalse(is_win(player))


if __name__ == "__main__":
    unittest.main()
