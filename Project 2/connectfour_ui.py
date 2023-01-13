# contains the UI for the shell-only version of the Connect 4 Program

from collections import namedtuple
import connectfour_functions as game
import connectfour

def _make_player_move(game_state:
                      connectfour.GameState) -> (connectfour.GameState,
                                                 bool):
    '''Makes the player move for any of the two players, and
    Returns the new game state and a boolean indicating
    if the move was a valid move'''
    player = game_state.turn
    player_names = ['EMPTY', 'RED', 'YELLOW']
    print(f"----Player {player}'s Turn ({player_names[player]})----")
    move = game.get_move_input(game_state)
    return game.make_move(game_state, move)

def _check_winner(game_state: connectfour.GameState) -> bool:
    'Returns True after declaring a winner; False if no winners exist'
    winner = connectfour.winner(game_state)
    player_names = ['EMPTY', 'RED', 'YELLOW']
    if winner:
        print(f'Player {winner} ({player_names[winner]}) is the winner!\n')
        return True
    else:
        return False

def play_connectfour() -> None:
    'Runs the main program to play the game Connect Four'
    game.print_welcome_banner()
    # change to make it so that there is no restart option (check prompt)
    game_state = game.start_game()
    game.print_board(game_state)
    while True:
        while True:
            game_state, is_valid_move = _make_player_move(game_state)
            if is_valid_move:
                break
        game.print_board(game_state)
        if _check_winner(game_state):
            break

# For Running as a Script:

if __name__ == '__main__':
    play_connectfour()
