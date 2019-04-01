from PlayerClient import PlayerClient
import argparse


def main(type, prob, bluff, host, port):
    p = PlayerClient(type=type, host=host, port=port)
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
    parser.add_argument("-c", "--cutoff", help="Probability cutoff", type=float, default=.1)
    parser.add_argument("-b", "--bluff", help="Bluff Probability", type=float, default=.1)
    parser.add_argument("-a", "--address", help="IP Address of host server", type=str, default='127.0.0.1')
    parser.add_argument("-p", "--port", help="Port number of host server", type=int, default=65445)
    args = parser.parse_args()
    main(args.type, args.cutoff, args.bluff, args.address, args.port)
