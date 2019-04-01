from PerudoServer import PerudoServer
import argparse


def print_results_table(data, player_list):
    col_names = ["Call Accuracy", "Avg Num Dice", "Games Won"]
    str_l = max(len(t) for t in col_names)
    print(" ".join(['{:>{length}s}'.format(t, length=str_l) for t in [" "] + col_names]))
    for t, row in zip(player_list, data):
        print(" ".join(['{:>{length}s}'.format(str(x), length=str_l) for x in [t] + row]))


def main(players, num_games, address, port):
    p = PerudoServer(num_players=players, num_games=num_games, host=address, port=port)
    p.add_players()
    p.send_num_games()
    winner = {k: [0, 0, 0, 0] for k in range(len(p.player_list))}

    for i in range(p.num_games):
        print("Game {}".format(i))
        while True:
            if sum([x.out for x in p.player_list.values()]) == len(p.player_list) - 1:
                p.send_game_over()

                p.send_out()

                break
            else:

                p.send_game_over()

                p.send_out()

                player, call = p.play_round()

                winner[player][0 if call else 1] += 1

        p.broadcast_win()
        for player in list(p.player_list.keys()):
            if not p.player_list[player].out:
                won = p.original_player_list[player]
                print("Original Player {} has won.".format(won+1))
                # print("Game Over")
                winner[won][2] += len(p.player_list[player].dice_list)
                winner[won][3] += 1
                break

        print("#############################################################")

        if i < num_games - 1:
            p.reset()

    stats = {}
    for i in range(len(p.player_list)):
        if sum(winner[i][:2]) == 0:
            if winner[i][3] == 0:
                stats[i] = ["Never Called", 0, winner[i][3]]
            else:
                stats[i] = ["Never Called", winner[i][2] / winner[i][3], winner[i][3]]
        else:
            if winner[i][3] == 0:
                stats[i] = [winner[i][0] / sum(winner[i][:2]), 0, winner[i][3]]
            else:
                stats[i] = [winner[i][0] / sum(winner[i][:2]), winner[i][2] / winner[i][3], winner[i][3]]

    print_results_table(list(stats.values()), ["Player {}".format(i+1) for i in range(len(p.player_list))])

    p.sock.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("players", help="Number of players in the game", type=int)
    parser.add_argument("-n", "--number", help="Number of games to play", type=int, default=1)
    parser.add_argument("-a", "--address", help="IP Address", type=str, default='127.0.0.1')
    parser.add_argument("-p", "--port", help="Port number", type=int, default=65445)
    args = parser.parse_args()
    main(args.players, args.number, args.address, args.port)
