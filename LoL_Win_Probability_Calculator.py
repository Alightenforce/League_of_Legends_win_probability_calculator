from Player_Class import Player

def main():
    player1 = Player("Alightenforce", "4040", "europe", 10, "12.6.1")
    player1.print_win_rate()
    player1.print_champion_name_to_champion_mastery()

if __name__ == "__main__":
    main()