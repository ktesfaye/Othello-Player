"""
Kirubel Tesfaye
Artificial Intelligence
Project 2: Othello
"""

from othello import *
import random, sys
import math
import time

class MoveNotAvailableError(Exception):
    """Raised when a move isn't available."""
    pass

class OthelloTimeOut(Exception):
    """Raised when a player times out."""
    pass

class OthelloPlayer():
    """Parent class for Othello players."""

    def __init__(self, color):
        assert color in ["black", "white"]
        self.color = color

    def make_move(self, state, remaining_time):
        """Given a game state, return a move to make. Each type of player
        should implement this method. remaining_time is how much time this player
        has to finish the game."""
        pass

class RandomPlayer(OthelloPlayer):
    """Plays a random move."""

    def make_move(self, state, remaining_time):
        """Given a game state, return a move to make."""
        return random.choice(state.available_moves())

class HumanPlayer(OthelloPlayer):
    """Allows a human to play the game"""

    def make_move(self, state, remaining_time):
        """Given a game state, return a move to make."""
        available = state.available_moves()
        print("----- {}'s turn -----".format(state.current))
        print("Remaining time: {:0.2f}".format(remaining_time))
        print("Available moves are: ", available)
        move_string = input("Enter your move as 'r c': ")

        # Takes care of errant inputs and bad moves
        try:
            moveR, moveC = move_string.split(" ")
            move = OthelloMove(int(moveR), int(moveC), state.current)
            if move in available:
                return move
            else:
                raise MoveNotAvailableError # Indicates move isn't available

        except (ValueError, MoveNotAvailableError):
            print("({}) is not a legal move for {}. Try again\n".format(move_string, state.current))
            return self.make_move(state, remaining_time)

class OldTournamentPlayer(OthelloPlayer):
    """You should implement this class as your entry into the AI Othello tournament.
    You should implement other OthelloPlayers to try things out during your
    experimentation, but this is the only one that will be tested against your
    classmates' players."""

    def score_board(self, state):
        """ Give a score for ach gird as a heurstic """

        # CITE: https://othellomaster.com/OM/Report/HTML/report.html
        # HESC: A score for the othello grid that I can model mine after
        board_heurstic =[
        [10000, -10000, 1000,  800, 800, 1000,  -10000, 10000], \
        [-10000, -10000, -450, -500, -500, -450, -10000, -10000], \
        [1000,  -450,  30,  10,  10,  30,  -450, 1000], \
        [800,  -500,  10,  50,  50,  10,  -500,  800], \
        [800,  -500,  10,  50,  50,  10,  -500,  800], \
        [1000,  -450,  30,  10,  10,  30,  -450, 1000], \
        [-10000, -10000, -450, -500, -500, -450, -10000, -10000], \
        [10000, -10000, 1000,  800, 800, 1000,  -10000, 10000]]

        black_number = OthelloState.count(state, 'black')
        white_number = OthelloState.count(state, 'white')

        # Check each square and for each color, add the score of that cell to the number
        for i in range(8):
            for j in range(8):
                if state.board[i][j] == 'black':
                    black_number += board_heurstic[i][j]

                if state.board[i][j] == 'white':
                    white_number += board_heurstic[i][j]

        return black_number, white_number

    def alpha_beta_max_node(self, state, color, depth, alpha, beta, start_time):
        """ Traverse through the available moves and look down the depth moves
        ahead. So once you reach at the depth wanted, return the number of each color
        and choose the move that maximizes the current nodes number. """

        available = state.available_moves()

        # The value we want to compare against
        max_value = -math.inf

        # Variable to keep track of the best move
        end_time = time.time()

        # Once you either reach the depth we want to be searched deep, or
        # once you've used your time for each move, return the count of each color
        if depth == 0 or len(available) == 0 or (time.time() - start_time) > 6:
            black_number, white_number = self.score_board(state)

            if state.current == 'black': return black_number
            if state.current == 'white': return white_number

        else:
            # Traverse through each move and look to the depth given and always update
            # the biggest score you find for the color
            for move in available:
                new_state = OthelloState.apply_move(copy.deepcopy(state), move)

                # next_color = opposite_color(state.current)
                new_score = self.alpha_beta_min_node(new_state, new_state.current, depth - 1, alpha, beta, start_time)

                max_value = max(max_value, new_score)
                alpha = max(new_score, alpha)

                if (time.time() - start_time) > 4.5: return max_value

                # Keep update the alpha value until the you get a value that is big enough to be greater than the other
                # colors, in which case, don't look at the other moves in the available list
                if beta <= alpha:
                    break

            return max_value

    def alpha_beta_min_node(self, state, color, depth, alpha, beta, start_time):
        """ Traverse through the available moves and look down the depth moves
        ahead. So once you reach at the depth wanted, return the number of each color
        and choose the move that maximizes the current nodes number. """

        available = state.available_moves()

        # The value we want to compare against
        max_value = math.inf
        end_time = time.time()

        # Once you either reach the depth we want to be searched deep, or
        # once you've used your time for each move, return the count of each color
        if depth == 0 or len(available) == 0 or (time.time() - start_time) > 6:
            black_number, white_number = self.score_board(state)

            if state.current == 'black': return black_number
            if state.current == 'white': return white_number

        else:
            # Traverse through each move and look to the depth given and always update
            # the biggest score you find for the color
            for move in available:
                new_state = OthelloState.apply_move(copy.deepcopy(state), move)

                new_score = self.alpha_beta_max_node(new_state, new_state.current, depth - 1, alpha, beta, start_time)

                max_value = min(new_score, max_value)
                beta = min(new_score, beta)

                if (time.time() - start_time) > 4.5: return max_value

                # Keep update the alpha value until the you get a value that is big enough to be greater than the other
                # colors, in which case, don't look at the other moves in the available list
                if beta <= alpha:
                    break

            return max_value

    def make_move(self, state, remaining_time):
        """Given a game state, return a move to make."""

        # Give the curent time so that the functions can know how long to spend on each move

        start_time = time.time()
        available = state.available_moves()
        max_value = -math.inf
        best_move = None
        for move in available:
            state = OthelloState.apply_move(copy.deepcopy(state), move)

            for i in range(1, 30):
                if state.current == 'white':
                    new_score = self.alpha_beta_min_node(state, state.current, i, -math.inf, math.inf, start_time)
                else:
                    new_score = self.alpha_beta_max_node(state, state.current, i, -math.inf, math.inf, start_time)

            if new_score > max_value:
                max_value = new_score
                best_move = move
                break

        return best_move

class AlphaBetaPlayer(OthelloPlayer):

    def score_board(self, state):
        """ Give a score for ach gird as a heurstic """

        # CITE: https://othellomaster.com/OM/Report/HTML/report.html
        # HESC: A score for the othello grid that I can model mine after
        board_heurstic =[
        [10000, -5000, 1000,  800, 800, 1000,  -5000, 10000], \
        [-5000, -5000, -450, -500, -500, -450, -5000, -5000], \
        [1000,  -450,  30,  10,  10,  30,  -450, 1000], \
        [800,  -500,  10,  50,  50,  10,  -500,  800], \
        [800,  -500,  10,  50,  50,  10,  -500,  800], \
        [1000,  -450,  30,  10,  10,  30,  -450, 1000], \
        [-5000, -5000, -450, -500, -500, -450, -5000, -5000], \
        [10000, -5000, 100,  800, 800, 100,  -5000, 10000]]

        black_number = OthelloState.count(state, 'black')
        white_number = OthelloState.count(state, 'white')

        # Check each square and for each color, add the score of that cell to the number
        for i in range(8):
            for j in range(8):
                if state.board[i][j] == 'black':
                    black_number += board_heurstic[i][j]

                if state.board[i][j] == 'white':
                    white_number += board_heurstic[i][j]

        return black_number, white_number

    def alpha_beta_max_node(self, state, color, depth, alpha, beta, start_time):
        """ Traverse through the available moves and look down the depth moves
        ahead. So once you reach at the depth wanted, return the number of each color
        and choose the move that maximizes the current nodes number. """

        new_state = None
        available = state.available_moves()

        # The value we want to compare against
        max_value = -math.inf

        # Variable to keep track of the best move
        best_move = None
        end_time = time.time()

        # Once you either reach the depth we want to be searched deep, or
        # once you've used your time for each move, return the count of each color
        if depth == 0 or len(available) == 0:
            black_number, white_number = self.score_board(state)

            if state.current == 'black': return best_move, black_number - white_number
            if state.current == 'white': return best_move, white_number - black_number

        else:
            # Traverse through each move and look to the depth given and always update
            # the biggest score you find for the color
            for move in available:
                new_state = OthelloState.apply_move(copy.deepcopy(state), move)

                # next_color = opposite_color(state.current)
                new_move, new_score = self.alpha_beta_min_node(new_state, new_state.current, depth - 1, alpha, beta, start_time)

                if new_score > max_value:
                    max_value = new_score
                    best_move = move

                alpha = max(new_score, alpha)

                if (time.time() - start_time) > 4.5: return best_move, max_value

                # Keep update the alpha value until the you get a value that is big enough to be greater than the other
                # colors, in which case, don't look at the other moves in the available list
                if beta <= alpha:
                    break

            return best_move, max_value

    def alpha_beta_min_node(self, state, color, depth, alpha, beta, start_time):
        """ Traverse through the available moves and look down the depth moves
        ahead. So once you reach at the depth wanted, return the number of each color
        and choose the move that maximizes the current nodes number. """

        new_state = None
        available = state.available_moves()

        # The value we want to compare against
        max_value = math.inf
        best_move = None
        end_time = time.time()

        # Once you either reach the depth we want to be searched deep, or
        # once you've used your time for each move, return the count of each color
        if depth == 0 or len(available) == 0:
            black_number, white_number = self.score_board(state)

            if  state.current == 'black': return best_move, black_number - white_number
            else: return best_move, white_number - black_number

        else:
            # Traverse through each move and look to the depth given and always update
            # the biggest score you find for the color
            for move in available:
                new_state = OthelloState.apply_move(copy.deepcopy(state), move)

                # next_color = opposite_color(state.current)

                new_move, new_score = self.alpha_beta_max_node(new_state, new_state.current, depth - 1, alpha, beta, start_time)

                if new_score < max_value:
                    max_value = new_score
                    best_move = move

                beta = min(new_score, beta)

                if (time.time() - start_time) > 4.5: return best_move, max_value

                # Keep update the alpha value until the you get a value that is big enough to be greater than the other
                # colors, in which case, don't look at the other moves in the available list
                if beta <= alpha:
                    break

            return best_move, max_value

    def make_move(self, state, remaining_time):
        """Given a game state, return a move to make."""

        # Give the curent time so that the functions can know how long to spend on each move

        start_time = time.time()

        for i in range(1, 30):
            state = copy.deepcopy(state)
            if state.current == 'black':
                best_move, best_score = self.alpha_beta_max_node(state, state.current, i, -math.inf, math.inf, start_time)
            if state.current == 'white':
                best_move, best_score = self.alpha_beta_min_node(state, state.current, i, -math.inf, math.inf, start_time)

                return best_move

class TournamentPlayer(OthelloPlayer):
    """ An intelligent player to play the game """

    def count_numbers(self, state):
        """ Count and return the number of each color on the board """

        board_heurstic =[
        [10000, -10000, 1000,  800, 800, 1000,  -10000, 10000], \
        [-10000, -10000, -450, -500, -500, -450, -10000, -10000], \
        [1000,  -450,  30,  10,  10,  30,  -450, 1000], \
        [800,  -500,  10,  50,  50,  10,  -500,  800], \
        [800,  -500,  10,  50,  50,  10,  -500,  800], \
        [1000,  -450,  30,  10,  10,  30,  -450, 1000], \
        [-10000, -10000, -450, -500, -500, -450, -10000, -10000], \
        [10000, -10000, 1000,  800, 800, 1000,  -10000, 10000]]

        black_number = OthelloState.count(state, 'black')
        white_number = OthelloState.count(state, 'white')

        # Check each square and for each color, add the score of that cell to the number
        for i in range(8):
            for j in range(8):
                if state.board[i][j] == 'black':
                    black_number += board_heurstic[i][j]

                if state.board[i][j] == 'white':
                    white_number += board_heurstic[i][j]

        return black_number, white_number


    def minimax_max_node(self, state, color, depth, alpha, beta, start_time):
        """ Traverse through the available moves and look down the depth moves
        ahead. So once you reach at the depth wanted, return the number of each color
        and choose the move that maximizes the current nodes number. """

        available = state.available_moves()

        # The value we want to compare against
        max_value = -math.inf

        # Variable to keep track of the best move
        best_move = None
        end_time = time.time()

        # Once you either reach the depth we want to be searched deep, or
        # once you've used your time for each move, return the count of each color
        if depth == 0 or len(available) == 0:
            black_number, white_number = self.count_numbers(state)
            if state.current == 'black': return best_move, black_number
            if state.current == 'white': return best_move, white_number

        else:
            # Traverse through each move and look to the depth given and always update
            # the biggest score you find for the color
            for move in available:
                new_state = OthelloState.apply_move(copy.deepcopy(state), move)

                new_move, new_score = self.minimax_min_node(new_state, new_state.current, depth - 1, alpha, beta, start_time)

                if new_score >= max_value:
                    max_value = new_score
                    best_move = move
                alpha = max(alpha, new_score)

                if alpha >= beta or (time.time() - start_time) > 4.5:
                    break

            return best_move, max_value

    def minimax_min_node(self, state, color, depth, alpha, beta, start_time):
        """ Traverse through the available moves and look down the depth moves
        ahead. So once you reach at the depth wanted, return the number of each color
        and choose the move that maximizes the current nodes number. """

        # new_state = copy.deepcopy(state)
        available = state.available_moves()

        # The value we want to compare against
        max_value = math.inf

        # Variable to keep track of the best move
        best_move = None
        end_time = time.time()

        # Once you either reach the depth we want to be searched deep, or
        # once you've used your time for each move, return the count of each color
        if depth == 0 or len(available) == 0:
            black_number, white_number = self.count_numbers(state)
            if state.current == 'black': return best_move, black_number
            if state.current == 'white': return best_move, white_number

        else:
            # Traverse through each move and look to the depth given and always update
            # the biggest score you find for the color
            for move in available:
                new_state = OthelloState.apply_move(copy.deepcopy(state), move)

                new_move, new_score = self.minimax_max_node(new_state, new_state.current, depth - 1, alpha, beta, start_time)

                if new_score <= max_value:
                    max_value = new_score
                    best_move = move
                beta = min(beta, new_score)

                if alpha >= beta or (time.time() - start_time) > 4.5:
                    break

            return best_move, max_value

    def make_move(self, state, remaining_time):
        """Given a game state, return a move to make."""

        # Give the curent time so that the functions can know how long to spend on each move
        start_time = time.time()
        for i in range(30):
            state = copy.deepcopy(state)
            if state.current == 'white':
                best_move, best_score = self.minimax_max_node(state, state.current, i, -math.inf, math.inf, start_time)
            else:
                best_move, best_score = self.minimax_max_node(state, state.current, i, -math.inf, math.inf, start_time)

        return best_move
################################################################################

def main():
    """Plays the game."""

    black_player = RandomPlayer("black")
    white_player = TournamentPlayer("white")

    game = OthelloGame(black_player, white_player, verbose=True)

    # winner = game.play_game_timed()

    ##### Use this method if you want to use a HumanPlayer
    # winner = game.play_game()

    result = []

    for _ in range(10):
        game = copy.deepcopy(OthelloGame(black_player, white_player, verbose=True))

        winner = game.play_game_timed()
        result.append(winner)
        # if winner is 'white': break

    print(result)
    print("Number of black wins: ", result.count('black'))
    print("Number of white wins: ", result.count('white'))
    print("Number of draws: ", result.count('draw'))

    if not game.verbose:
        print("Winner is", winner)


if __name__ == "__main__":
    main()
