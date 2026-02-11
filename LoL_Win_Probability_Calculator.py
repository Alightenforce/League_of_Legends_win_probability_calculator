from Player_Class import Player

def main():
    player1 = Player("Alightenforce", "4040", "europe", 5, "12.6.1")
    # player1.print_player_data()
    # player1.print_win_rate()
    link = player1.get_link_for_player_mastery()
    mastery_data = player1.get_all_champion_masteries(link)
    print(mastery_data)


if __name__ == "__main__":
    main()