# contains the UI for the network version of the Connect 4 Program

from collections import namedtuple
import connectfour_client as client
import connectfour_functions as game
import connectfour
import socket

# TODO:
# - Check prompt to make sure everything is correct
# - put docstrings on everything

# For Testing:
GAME_HOST = 'circinus-32.ics.uci.edu'
GAME_PORT = 4444

_SHOW_DEBUG_TRACE = False

Server = namedtuple('Server', ['host', 'port'])

def _ask_for_host_port() -> Server:
    '''
    Asks for server information from the user (host, port)
    If host and port are valid, returns a Server namedtuple
    Else, prints an error and returns None.
    '''
    host = None
    port = None

    while True:
        host = input('Enter the host of the server: ').strip()
        if host == '':
            print('Host cannot be empty!')
        else:
            break

    while True:
        try:
            port = int(input('Enter the port of the server: ').strip())
            if port > -1 and port < 65536:
                break
            else:
                print('Port must be 0-65535!')
        except ValueError:
            print ('Port must be an integer!')

    return Server(host, port)

def _connect_to_server(server: Server) -> client.GameConnection:
    'Connects to the server using server information (host, port)'
    connection = None
    try:  
        connection = client.connect(server.host, server.port)
    except ConnectionRefusedError:
        print('---ERROR: Cannot connect to this server---')
        return None
    except socket.gaierror:
        print('---ERROR: Host or port does not exist---')
        return None
    except OSError:
        print('---ERROR: No route to host---')
        return None

    return connection

def _ask_for_username(connection: client.GameConnection) -> str:
    'Asks for a username and returns it'
    while True:
        username = input('Enter a username: ').strip()
        if ' ' in username:
            print('Username must have no spaces!')
        elif username == '':
            print('Username must not be empty!')
        else:
            return username

def _send_user_move(connection: client.GameConnection,
                   game_state: connectfour.GameState) -> (connectfour.GameState,
                                                          bool,
                                                          int):
    '''Gets user move and sends it to the server,
    Returns the game_state, a boolean
    indicating if the move was valid, and an int for
    a winner if there is one'''
    move = game.get_move_input(game_state)
    
    client.send_move(connection, move)
    valid_for_server, winner = client.get_move_response(connection)
    
    game_state, is_valid_move = game.make_move(game_state,
                                               move)
    if is_valid_move and valid_for_server:
        # if the move is valid
        return (game_state, True, winner)
    elif is_valid_move or valid_for_server:
        # if client and server don't agree it is a valid move
        # most likely won't happen but just in case
        raise client.GameProtocolError
    else:
        # if the move is not valid
        return (game_state, False, winner)

def _receive_server_move(
    connection: client.GameConnection,
    game_state: connectfour.GameState) -> (connectfour.GameState,
                                           bool):
    '''Gets server move and applies it to game_state,
    Returns the game_state and a boolean
    indicating if the move was valid'''
    move = client.receive_move(connection)
        
    game_state, is_valid_move = game.make_move(game_state,
                                               move)

    if is_valid_move:
        return (game_state, True)
    else:
        return (game_state, False)

def _check_winner(game_state: connectfour.GameState, username: str) -> bool:
    'Returns True after declaring a winner; False if no winners exist'
    winner = connectfour.winner(game_state)
    if winner == 0:
        return False
    elif winner == 1:
        print(f'{username} (RED) is the winner!')
        return True
    elif winner == 2:
        print('The Server (YELLOW) is the winner!')
        return True

def run_user_interface() -> None:
    'Runs the user interface of the program'
    server = _ask_for_host_port()
    
    connection = _connect_to_server(server)

    # end early if not connected to server
    if connection == None:
        return None
    
    try:
        username = _ask_for_username(connection)
        client.hello(connection, username)
        game.print_welcome_banner()
        game_state = game.start_game()
        client.request_game(connection,
                            connectfour.columns(game_state),
                            connectfour.rows(game_state))
        game.print_board(game_state)
        while True:
            player = game_state.turn
                
            print(f"----{username}'s Move (RED)----")
            game_state, is_valid, winner = _send_user_move(connection,
                                                           game_state)
            
            if is_valid:
                game.print_board(game_state)

                if winner != 0 and _check_winner(game_state, username):
                    break
                    
                game_state, server_is_valid = _receive_server_move(connection,
                                                                   game_state)       

                print("----The Server's Move (YELLOW)----")
                game.print_board(game_state)

            winner = client.check_winner_after_server(connection)

            if winner != 0 and _check_winner(game_state, username):
                break

    except client.GameProtocolError:
        # whenever the server and client aren't in agreement
        # we need to break up the fight
        print('---ERROR: Server and client mismatch!---')
    finally:
        client.close(connection)


if __name__ == '__main__':
    run_user_interface()
    
