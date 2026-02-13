from Player_Class import Player

def main():
    player1 = Player("Alightenforce", "4040", "europe", 20)
    player1.update_profile()
   # player1.print_player_data()
   # player1.print_win_rate()
   # player1.print_champion_name_to_champion_mastery()
   # player1.print_side_bans()
   # player1.print_win_rate_per_champion()
   # player1.get_win_and_losses_per_champion()
   # player1.print_win_rate_per_champion()
   # player1.get_win_rate_per_champion()
   # print(player1.get_kda_of_champion_from_previous_matches())
    player1.print_average_kda_per_champion()
if __name__ == "__main__":
    main()