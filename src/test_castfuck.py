#!/usr/bin/env python
#-*- coding:cp1251 -*-

import unittest
from brainspell import Direction, Coords
from brainspell import Game, Player, Map, Robot, Letter
import brainspell

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
        self.assertRaises(brainspell.WrongDirectionName, Direction, '-')

        


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
        
    @staticmethod
    def place_operators(player, map_as_str_list, start_x, start_y):
        for y in range(len(map_as_str_list)):
            for x in range(len(map_as_str_list[y])):
                if map_as_str_list[y][x]!=' ':
                    player.place_operator(\
                        map_as_str_list[y][x],\
                        Coords(start_x+x, start_y+y)\
                    )
        
    def test_many_programms(self):
        programms = (
            (["++++++++.>+++++.<++++..++++-."], "HELLO"),
            (["++++++++.>+++++.<++++..++++-."], "HELLO"),
            (["++++++++.>+++++.<++++..++++-."], "HELLO"),
            (["++++++++.>+++++.<++++..++++-."], "HELLO"),
                ([\
"+++/",\
"   +",\
"   +",\
".++/",\
"",\
], "G"),

            )
        
        for program, rightresult in programms:
            game = Game(Map(60,60))
            pl = Player("darvin")
            game.add_player(pl)
            
            pl.cast("create_robot", Coords(-1,0), Direction('e'))
            self.place_operators(pl, program, 0,0)
            
            pl.cast("run") 
            for i in range(100):
                game.tick()
            pl.robots[0].coord = Coords(0,2)
            game.tick()
            game.tick()
            game.tick()
            game.tick()
            self.assertEqual(rightresult, pl.robots[0].output)
                
    
    def test_cycled_programms(self):
        programms = (
            #(["+++[>++<-]>."], "F"),
            #(["+++[>+++++<-]>."], "O"),
            #(["++[>+++[>+++<-]<-]>>."], "R"),
            #(["++[>++[>+++++<-]<-]>>+."], "U"),
            ([
r"++[/  />+++++/     ",                
r"   >  [      <     ",                
r"   \++\      -     ",                
r"             ]     ",                
r"      .+>>]-</     ",                
r"                   ",                
r"                   ",                
r"                   ",                
r"                   ",                
r"                   ",                
r"                   ",                
                
                
                ], "U"),
                    )
        
        for program, rightresult in programms:
            game = Game(Map(60,60))
            pl = Player("darvin")
            game.add_player(pl)
            
            pl.cast("create_robot", Coords(-1,0), Direction('e'))
            self.place_operators(pl, program, 0,0)
            
            pl.cast("run") 
            for i in range(100):
                game.tick()
            
            self.assertEqual(rightresult, pl.robots[0].output)
                
if __name__=="__main__":
    unittest.main()