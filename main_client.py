from PlayerClient import PlayerClient
import argparse


def main(type, prob=.1, bluff=.1):
    p = PlayerClient(type=type)
    num_games = p.num_games()

    for i in range(num_games):
        while True:
            if p.game_over:
                break
            else:
                p.check_game_over()
                p.check_out()
                if p.out:
                    print("You are out")
                    pass
                elif not p.game_over:
                    p.play_round(prob, bluff)

        if p.check_won():
            print("You have won")
            print("------------------------------------------------")
        else:
            print("You have lost")
            print("------------------------------------------------")

        if i < num_games - 1:
            p.reset()

    p.sock.close()


help_string = """
0: Human Player
1: DumbAIPlayer
2: SLDumbAIPlayer
3: LDumbAIPlayer
4: SLMiniMax
5: LMiniMax
6: RandomAI
"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("type", type=int, help=help_string)
    parser.add_argument("-p", "--probability", help="Probability cutoff", type=float)
    parser.add_argument("-b", "--bluff", help="Bluff Probability", type=float)
    args = parser.parse_args()
    if args.probability and args.bluff:
        main(args.type, args.probability, args.bluff)
    elif args.probability:
        main(args.type, prob=args.probability)
    elif args.bluff:
        main(args.type, bluff=args.bluff)
    else:
        main(args.type)
