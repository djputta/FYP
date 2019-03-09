from PlayerClient import PlayerClient
from time import sleep
import argparse


def main(type):
    p = PlayerClient(type=type)
    num_games = p.num_games()

    for i in range(num_games):
        while True:
            if p.game_over:
                break
            else:
                p.check_game_over()
                sleep(.01)
                p.check_out()
                sleep(.01)
                if p.out:
                    print("You are out")
                elif not p.game_over:
                    p.play_round()
                    # sleep(.1)

        if p.check_won():
            print("You have won")
        else:
            print("You have lost")

        p.reset()

    p.sock.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("type", help="0 for Human, 1-3 for different AI", type=int)
    args = parser.parse_args()
    main(args.type)