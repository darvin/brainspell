#!/usr/bin/env python
#-*- coding:cp1251 -*-

import unittest
from castfuck import Direction, Coords
from castfuck import Game, Player, Map, Robot, Letter
import castfuck

class TestDirections(unittest.TestCase):
    directions = ['n','w','s','e']
    def test_turns(self):
        d = Direction('n')
        d.turn_left()
        self.assertEqual(d, Direction('w'))
        d.turn_right()
        self.assertEqual(d, Direction('n'))
    
    def test_sanity(self):
        for dirname in self.directions:
            d = Direction(dirname)
            for x in range(4):
                d.turn_left()
            self.assertEqual(d, Direction(dirname))
        
            for x in range(4):
                d.turn_right()
            self.assertEqual(d, Direction(dirname))

    def test_errors(self):
        self.assertRaises(castfuck.WrongDirectionName, Direction, '-')

        


class TestCoords(unittest.TestCase):
    def test_sanity(self):
        c = Coords(1,1)
        d = Direction('n')
        for x in range(4):
            c = c.get_offset(d, 5)
            d.turn_left()
        self.assertEqual(c, Coords(1,1))

        for x in range(4):
            c = c.get_offset(d, -1)
            d.turn_right()
        self.assertEqual(c, Coords(1,1))
    
    def test_get_offset(self):
        c = Coords(10,1)
        self.assertEqual(Coords(2,1), c.get_offset(Direction('w'), 8))
        self.assertEqual(Coords(13,1), c.get_offset(Direction('e'), 3))
        self.assertEqual(Coords(10,-1), c.get_offset(Direction('n'), 2))
        self.assertEqual(Coords(10,2), c.get_offset(Direction('s')))
       

class TestGame(unittest.TestCase):
    def test_one_player(self):
        game = Game(Map(13,13))
        pl = Player("darvin")
        game.add_player(pl)
        
        self.assertEqual(pl.game, game)
        
        pl.cast("create_robot", Coords(-1,0), Direction('e'))
       
        program = "+.+.+.+.+"
        for op, x in zip(program, range(len(program))):
            pl.place_operator(op, Coords(x,0))
            
        pl.cast("run")
        
        for i in range(100):
            game.tick()
        
        self.assertEqual("ABCD", pl.robots[0].output)
        
        
    
if __name__=="__main__":
    unittest.main()