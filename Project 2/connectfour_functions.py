# contains overlapping functions for both the network version and the
# shell-only version of the Connect 4 Program

from collections import namedtuple
import connectfour

Cell = namedtuple('Cell', ['row', 'col'])
Move = namedtuple('Move', ['option', 'col'])

# Public Functions:

def print_welcome_banner() -> None:
    'Prints the welcome banner'
    print('-----------------')
    print(' . . . . . . . . ')
    print(' . Welcome  to . ')
    print(' . . . . . . . . ')
    print(' . Connect  4! . ')
    print(' . . . . . . . . ')
    print('-----------------')
    print()

def start_game() -> connectfour.GameState:
    'Creates a new game with a board size determined by the user inputs'
    cols = None
    rows = None
    
    print('How many columns should the board have?')
    print(f'(min = {connectfour.MIN_COLUMNS}, max = {connectfour.MAX_COLUMNS})')
    cols = _ask_valid_input(connectfour.MIN_COLUMNS, connectfour.MAX_COLUMNS)

    print('Great! Now how many rows should the board have?')
    print(f'(min = {connectfour.MIN_ROWS}, max = {connectfour.MAX_ROWS})')
    rows = _ask_valid_input(connectfour.MIN_ROWS, connectfour.MAX_ROWS)

    return connectfour.new_game(int(cols), int(rows))

def get_move_input(game_state: connectfour.GameState) -> Move:
    '''Asks the option for move type (1 = drop, 2 = pop) and the column
    to move the move, then returns it in a Move namedtuple'''
    move_type = 1 # default is drop so 1
    chosen_col = None # there is no default
    # player is not always able to pop, so skip this part in that case
    if _able_to_pop(game_state):
        print('Choose a Move Type (1 or 2):')
        print('1) Drop')
        print('2) Pop')
        move_type = _ask_valid_input(1, 2)
    print(f'Choose a column (1-{connectfour.columns(game_state)}):')
    chosen_col = _ask_valid_input(1, connectfour.columns(game_state))
    return Move(move_type, chosen_col)

def make_move(game_state: connectfour.GameState,
              move: Move) -> (connectfour.GameState, bool):
    '''Allows the user to make a move; returns the new game state
    and a boolean indicated if the move was valid'''
    is_valid_move = True
    try:
        if move.option == 1:
            game_state = connectfour.drop(game_state, move.col - 1)
        elif move.option == 2:
            game_state = connectfour.pop(game_state, move.col - 1)
    except connectfour.InvalidMoveError:
        if move.option == 1:
            print('---Invalid Move!---')
            print('That column is full!\n')
        elif move.option == 2:
            print('---Invalid Move!---')
            print("You don't have a chip in the bottom of that column!\n")
        is_valid_move = False
    return (game_state, is_valid_move)

def print_board(game_state: connectfour.GameState) -> None:
    'Prints the board based on the game state'
    board = game_state.board
    rows = connectfour.rows(game_state) + 1
    cols = connectfour.columns(game_state)
    print()
    for row in range(rows):
        for col in range(cols):
            cell = Cell(row, col + 1)
            print(_space_between(cell), end='')
            if row == 0:
                print(str(cell.col), end='')
            else:
                print(_cell_piece(game_state, cell), end='')
        print()
    print()
    
# Only for testing
def restart_game() -> bool:
    'Determines whether or not to restart the game based on user input'
    return _ask_for_input('Restart? (Yes / No)\n').strip().lower() == 'yes'

# Private Functions:

def _ask_for_input(prompt: str) -> str:
    'Asks for input with a prompt and returns it, stripped'
    return input(prompt).strip()

def _ask_valid_input(min: int, max: int) -> int:
    'Asks for and determines the validity of the row/column inputted'
    while True:
        input = _ask_for_input('')
        try:
            num = int(input)
            
            if num < min:
                print(f'Too Small! Enter a value between {min}-{max}:')
            elif num > max:
                print(f'Too Large! Enter a value between {min}-{max}:')
            else:
                return num
        except ValueError:
            print(f'Invalid Input. Please enter a value between {min}-{max}:')

def _able_to_pop(game_state: connectfour.GameState) -> bool:
    'Checks if the player is able to pop'
    board = game_state.board
    for col in board:
        if col[connectfour.rows(game_state) - 1] == game_state.turn:
            return True
    return False
    

def _cell_piece(game_state: connectfour.GameState, cell: Cell) -> str:
    'Returns a string representing the cell piece for a cell'
    game_piece = game_state.board[cell.col - 1][cell.row - 1]
    if game_piece == 1:
        return 'R'
    elif game_piece == 2:
        return 'Y'
    else:
        return '.'

def _space_between(cell: Cell) -> str:
    'Returns the amount of spaces between the column cells (either 1 or 2)'
    spaces = ' '
    if cell.col > 1:
        if cell.row == 0:
            digits = len(str(cell.col))
            spaces = ' ' * (3 - digits)
        else:
            spaces = '  '
    else:
        spaces = ''
    
    return spaces
