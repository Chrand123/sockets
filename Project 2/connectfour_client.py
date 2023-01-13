# contains all the client to server connections and commands for the
# network version of the Connect 4 Program

from collections import namedtuple
import connectfour_functions as game
import socket

_SHOW_DEBUG_TRACE = False

GameConnection = namedtuple('GameConnection', ['socket', 'input', 'output'])

class GameProtocolError(Exception):
    pass

def connect(host: str, port: int) -> GameConnection:
    'Connects to the server and returns the connection'
    game_socket = socket.socket()
    game_socket.connect((host, port))

    game_input = game_socket.makefile('r')
    game_output = game_socket.makefile('w')

    return GameConnection(
        socket = game_socket,
        input = game_input,
        output = game_output)

def hello(connection: GameConnection, username: str) -> bool:
    'Writes a "hello" message to verify that this is the correct server'
    _write_line(connection, f'I32CFSP_HELLO {username}')

    response = _read_line(connection)

    if response == f'WELCOME {username}':
        return True
    else:
        raise GameProtocolError

def request_game(connection: GameConnection, cols: int, rows: int) -> bool:
    'Requests the server to start the game with the specified columns and rows'
    _write_line(connection, f'AI_GAME {cols} {rows}')

    response = _read_line(connection)

    if response == 'READY':
        return True
    else:
        raise GameProtocolError

def send_move(connection: GameConnection, move: game.Move) -> None:
    '''Sends a move to the server, giving the option and column
    (1 = drop, 2 = pop) - option should only be 1 or 2
    Returns the response from the server indicating whether or not
    that was a valid move or if a player won'''
    move_type = None
    if move.option == 1:
        move_type = 'DROP'
    elif move.option == 2:
        move_type = 'POP'
        
    _write_line(connection, f'{move_type} {move.col}')
    

def get_move_response(connection: GameConnection) -> (bool, int):
    '''Gets the move response, which tells if the move was valid
    or if there was a winner'''
    response = _read_line(connection)

    if response == 'OKAY':
        return (True, 0)
    elif response == 'INVALID':
        return (False, 0)
    elif response == 'WINNER_RED':
        return (True, 1)
    elif response == 'WINNER_YELLOW':
        return (True, 2)
    else:
        raise GameProtocolError

def receive_move(connection: GameConnection) -> game.Move:
    '''Receives a move from the server'''
    server_message = _read_line(connection)

    move_parts = server_message.strip().split()

    move_col = None
    try:
        move_col = int(move_parts[1])
    except ValueError:
        raise GameProtocolError
    
    if move_parts[0] == 'DROP':
        return game.Move(1, move_col)
    elif move_parts[0] == 'POP':
        return game.Move(2, move_col)
    else:
        raise GameProtocolError

def check_winner_after_server(connection: GameConnection) -> int:
    '''Checks the server if there is a winner after the server
    has moved, if True returns an integer representing which
    player won (0 = EMPTY, 1 = RED, 2 = YELLOW)'''
    server_message = _read_line(connection)

    if server_message == 'READY':
        return 0
    elif server_message == 'WINNER_RED':
        return 1
    elif server_message == 'WINNER_YELLOW':
        return 2
    else:
        raise GameProtocolError

def close(connection: GameConnection) -> None:
    'Closes the connection to the server'
    connection.input.close()
    connection.output.close()
    connection.socket.close()

def _write_line(connection: GameConnection, line: str) -> None:
    'Writes a line to the server and flushes it'
    connection.output.write(line + '\r\n')
    connection.output.flush()

    if _SHOW_DEBUG_TRACE:
        print('SENT: ' + line)

def _read_line(connection: GameConnection) -> str:
    'Reads a line from the server'
    line = connection.input.readline().rstrip('\n')

    if _SHOW_DEBUG_TRACE:
        print(' GOT: ' + line)

    return line
