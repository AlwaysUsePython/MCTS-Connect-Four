# MCTS Connect Four

This program uses the MCTS algorithm to play connect 4. 

The UCBI C value is 50 and the scoring for the simulations is +50 if maximizing player wins and -50 if minimizing player wins.

This implementation departs from the classic MCTS in that it has perspective shifts - each node has a player as a private instance variable, and its selection of child nodes to explore depends on whether that perspective is of the minimizing player or the maximizing player.


# Plans for Further Updates

At the moment, the code creates a completely new tree for each move. It should be able to retain the information from its previous simulations from move to move.
