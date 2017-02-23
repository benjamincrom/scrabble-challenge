import copy
import itertools
import json

import scrabble_board
import scrabble_game

scrabble_game.input = lambda x: 'N'

def get_kleene_closure(input_iterable):
    return set(this_set
               for i in range(len(input_iterable) + 1)
               for this_set in itertools.combinations(input_iterable, i))

def load_file(input_filename):
    with open(input_filename, 'r') as filehandle:
        input_str = filehandle.read()

    input_dict = json.loads(input_str)
    board_character_array = input_dict['board']
    player_score_list_list = input_dict['scores']

    return board_character_array, player_score_list_list

def read_input_file(input_filename):
    board_character_array, player_score_list_list = load_file(input_filename)

    num_players = len(player_score_list_list)
    game = scrabble_game.ScrabbleGame(num_players)
    game.player_score_list_list = player_score_list_list
    game.player_rack_list = [[] for _ in range(num_players)]
    game.tile_bag = []
    game.move_number = sum(1 for player_score_list in player_score_list_list
                             for _ in player_score_list)

    for row_number, row in enumerate(board_character_array):
        for column_number, letter in enumerate(row):
            if letter:
                column_letter = chr(ord('a') + column_number)
                this_location = (column_letter, row_number + 1)
                game.board[this_location] = scrabble_board.ScrabbleTile(letter)

    return game

def get_all_board_tiles(game):
    return set((square_tuple[1].tile, square_tuple[0])  # tile then location
               for square_tuple in game.board.board_square_dict.items()
               if square_tuple[1].tile)

def move_is_board_subset(move_set, board):
    for tile, location in move_set:
        move_letter = tile.letter
        board_tile = board[location]
        if not board_tile or board_tile.letter != move_letter:
            return False

    return True

def boards_are_equivalent(board_1, board_2):
    return str(board_1) == str(board_2)

def get_all_possible_moves_set(new_game, reference_game):
    game_tile_location_set = get_all_board_tiles(new_game)
    reference_tile_location_set = get_all_board_tiles(reference_game)

    search_set = set()
    for reference_tile, reference_location in reference_tile_location_set:
        flag = True
        for game_tile, game_location in game_tile_location_set:
            if (game_tile.letter == reference_tile.letter and
                    game_location == reference_location):
                flag = False

        if flag:
            search_set.add((reference_tile, reference_location))

    return get_kleene_closure(search_set)

def get_legal_move_set(new_game, reference_game):
    all_possible_moves_set = get_all_possible_moves_set(new_game,
                                                        reference_game)

    legal_move_set = set()
    for move_set in all_possible_moves_set:
        temp_game = copy.deepcopy(new_game)
        is_board_subset = move_is_board_subset(move_set, reference_game.board)
        is_legal = scrabble_game.move_is_legal(temp_game.board,
                                               new_game.move_number,
                                               move_set)

        if is_legal and is_board_subset:
            for tile, location in move_set:
                temp_game.board[location] = tile

            legal_move_set.add(
                (scrabble_game.score_move(move_set, temp_game.board), move_set)
            )

    return legal_move_set

def get_move_set_generator(new_game, reference_game, move_list):
    legal_move_set = get_legal_move_set(new_game, reference_game)

    player_to_move_id = new_game.move_number % len(new_game.player_rack_list)
    player_score_list = reference_game.player_score_list_list[player_to_move_id]
    player_move_number = new_game.move_number // len(new_game.player_rack_list)
    target_score = player_score_list[player_move_number]

    next_move_set = set(
        frozenset((tile.letter, location) for tile, location in move_set)
        for score, move_set in legal_move_set
        if score == target_score
    )

    for next_move in next_move_set:
        new_game_copy = copy.deepcopy(new_game)
        move_list_copy = copy.deepcopy(move_list)
        player_to_move_id = (
            new_game_copy.move_number % len(new_game_copy.player_rack_list)
        )

        next_move_str = ''.join(letter for letter, location in next_move)
        new_game_copy.cheat_create_rack_word(next_move_str, player_to_move_id)
        new_game_copy.next_player_move(next_move)
        move_list_copy.append(next_move)

        if new_game_copy.move_number == reference_game.move_number:
            if boards_are_equivalent(reference_game.board, new_game_copy.board):
                yield move_list_copy
        else:
            yield from get_move_set_generator(new_game_copy,
                                              reference_game,
                                              move_list_copy)

reference_game = read_input_file('sample_input.json')
new_game = scrabble_game.ScrabbleGame(len(reference_game.player_rack_list))
move_set_generator = get_move_set_generator(new_game, reference_game, [])
move_set_list = [this_set for this_set in move_set_generator]
