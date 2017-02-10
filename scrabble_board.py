#!/usr/bin/python
'''
scrabble_board.py -- contain class that models scrabble board and game
'''
import random
import re

import config


class Square(object):
    def __init__(self, column, row, tile, letter_multiplier, word_multiplier):
        self.column = column
        self.row = row
        self.tile = tile
        self.letter_multiplier = letter_multiplier
        self.word_multiplier = word_multiplier

    def __repr__(self):
        if self.tile:
            return_value = str(self.tile)
        else:
            return_value = '_'

        return return_value


class Tile(object):
    def __init__(self, letter, point_value):
        self.letter = letter
        self.point_value = point_value

    def __repr__(self):
        return self.letter


class Board(object):
    def __init__(self):
        self.square_dict = self.initialize_square_dict()

    def __getitem__(self, key):
        return self.square_dict.get(key)

    def __setitem__(self, key, val):
        self.square_dict[key] = val

    def __repr__(self):
        serial_str = ''.join(
            (str(square)
             for location_tuple, square in sorted(self.square_dict.items()))
        )

        return_value = re.sub("(.{15})", "\\1\n", serial_str, 0, re.DOTALL)
        return return_value

    @staticmethod
    def get_location_word_mutliplier(column, row):
        if (column, row) in config.DOUBLE_WORD_SCORE_LOCATION_LIST:
            word_multiplier = 2
        elif (column, row) in config.TRIPLE_WORD_SCORE_LOCATION_LIST:
            word_multiplier = 3
        else:
            word_multiplier = 1

        return word_multiplier

    @staticmethod
    def get_location_letter_multiplier(column, row):
        if (column, row) in config.DOUBLE_LETTER_SCORE_LOCATION_LIST:
            letter_multiplier = 2
        elif (column, row) in config.TRIPLE_LETTER_SCORE_LOCATION_LIST:
            letter_multiplier = 3
        else:
            letter_multiplier = 1

        return letter_multiplier

    @classmethod
    def initialize_square_dict(cls):
        initial_square_dict = {}
        for column in 'abcdefghijlkmno':
            for row in range(1, 16):
                word_multiplier = cls.get_location_word_mutliplier(column, row)
                letter_multiplier = cls.get_location_letter_multiplier(column,
                                                                       row)

                initial_square_dict[(column, row)] = Square(
                    column=column,
                    row=row,
                    tile=None,
                    word_multiplier=word_multiplier,
                    letter_multiplier=letter_multiplier
                )

        return initial_square_dict


class Game(object):
    def __init__(self, num_players):
        self.num_players = num_players
        self.tile_bag = self.initialize_tile_bag()
        self.player_rack_list = self.initialize_player_racks()
        self.board = Board()
        self.move_number = 0

    def next_player_move(self, letter_location_list):
        for letter, board_location in letter_location_list:
            player_to_move = self.move_number % self.num_players
            player_rack = self.player_rack_list[player_to_move]
            rack_tile_index = None

            for i in range(len(player_rack)):
                if player_rack[i].letter == letter:
                    rack_tile_index = i

            if rack_tile_index is None:
                print 'Letter {} does not appear in player {}\'s rack'.format(
                    letter,
                    player_to_move
                )
            else:
                self.move_tile(player_to_move, rack_tile_index, board_location)

        self.move_number += 1

    def move_tile(self, player_id, rack_tile_index, board_location):
        ''' Takes format of rack_tile_index, board_location '''
        tile = self.player_rack_list[player_id].pop(rack_tile_index)
        self.board[board_location] = tile

    def draw_random_tile(self):
        random_index = random.randrange(0, len(self.tile_bag))
        return self.tile_bag.pop(random_index)

    def initialize_player_racks(self):
        player_rack_list = []
        for _ in range(self.num_players):
            this_rack = []
            for _ in range(7):
                this_rack.append(self.draw_random_tile())

            player_rack_list.append(this_rack)

        return player_rack_list

    @staticmethod
    def initialize_tile_bag():
        tile_bag = []
        for letter, magnitude in config.LETTER_DISTRIBUTION_DICT.items():
            for _ in range(magnitude):
                tile_bag.append(
                    Tile(letter=letter,
                         point_value=config.LETTER_POINT_VALUES_DICT[letter])
                )

        return tile_bag


g = Game(4)
print g.board
print g.player_rack_list
