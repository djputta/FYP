from Perudo import Perudo

p = Perudo(human_players=1, bot_player=1)

while True:
    if sum([x.out for x in p.player_list]) == len(p.player_list) - 1:
        break
    else:
        p.play_round()

p.sock.close()
