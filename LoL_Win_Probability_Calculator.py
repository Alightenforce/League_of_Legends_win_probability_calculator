from Player_Class import Player

def main():
    player1 = Player("BonBon125", "bon", "europe", 80)
    # link = player1.get_link_for_live_match()
    # print(player1.get_champion_in_current_match(link))
    # print(player1.get_banned_champions_in_current_match(link))
    # ban = player1.get_banned_champions_in_current_match(link)
    # print(player1.match_banned_champion_id_to_name(ban))
    # player1.print_player_data()
    # player1.print_banned_champions_in_current_match(ban)
    # player1.display_summoner_pfp_img()
    # player1.print_win_rate()
    # print(player1.get_link_for_live_match())
    # player2 = Player("Alightenforce", "4040", "europe", 20, "12.6.1")
    # player2.print_player_data()
    # player2.print_win_rate()
    # player1.print_win_rate()
    # dict1= player1.get_win_and_losses_per_champion()
    # print(player1.calculate_win_rate_per_champion(dict1))
    player1.print_win_rate_per_champion()
if __name__ == "__main__":
    main()