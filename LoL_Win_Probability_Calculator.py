from Player_Class import Player

def main():
    player1 = Player("Alightenforce", "4040", "europe", 5)
   #  player1.update_profile()
   #  player1.print_player_data()
   #  player1.print_player_data()
   #  player1.print_win_rate()
   #  player1.print_champion_name_to_champion_mastery()
   #  player1.print_side_bans()
   #  player1.print_win_rate_per_champion()
   #  player1.print_win_rate_per_champion()
   #  player1.print_average_kda_per_champion()
    player2 = Player("Sloppy", "BOMB", "europe", 5)
    player2.update_profile()
    player2.print_player_data()
    player2.print_side_bans()


if __name__ == "__main__":
    main()