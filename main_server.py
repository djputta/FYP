from PerudoServer import PerudoServer
from time import sleep
import argparse


def main(players, num_games=10):
    p = PerudoServer(num_players=players, num_games=num_games)
    p.add_players()
    p.send_num_games()
    winner = {k: [0, 0, 0] for k in range(len(p.player_list))}

    for i in range(p.num_games):
        print("Game {}".format(i))
        while True:
            if sum([x.out for x in p.player_list.values()]) == len(p.player_list) - 1:
                p.send_game_over()
                sleep(.05)
                p.send_out()
                sleep(.05)
                break
            else:
                sleep(.05)
                p.send_game_over()
                sleep(.05)
                p.send_out()
                sleep(.05)
                call, player = p.play_round()
                winner[player][0 if call else 1] += 1
                # sleep(.15)
        sleep(.1)

        p.broadcast_win()
        for i, player in enumerate(list(p.player_list.keys())):
            if not p.player_list[player].out:
                won = i
                print("Player {} has won.".format(won+1))
                # print("Game Over")
                winner[won][2] += 1
                break

        p.reset()
        print("#############################################################")

    print(winner)

    p.sock.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("players", help="Number of players in the game", type=int)
    parser.add_argument("-n", "--number", help="Number of games to play", type=int)
    args = parser.parse_args()
    if args.number:
        main(args.players, args.numbers)
    else:
        main(args.players)
