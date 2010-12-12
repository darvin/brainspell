import StringIO
import random
import string


def find_key(dic, val):
    """return the key of dictionary dic given the value"""
    for k, v in dic.items():
        if v == val:
            return k



class WrongDirectionName(Exception):
    pass
                
class Direction(object):
    """
    Class of direction (north, west, south, east)
    """
    directions = ['n', 'w', 's', 'e']
    def __init__(self, dir_str):
        """
        @param dir_str: one of 'n', 'w', 's', 'e'
        """
        if dir_str not in self.directions:
            raise WrongDirectionName
        if dir_str in self.directions:
            self.__dir = self.directions.index(dir_str)
        else:
            raise AssertionError
    
        
    def turn_right(self):
        """
        Turns direction clockwise
        """
        self.__dir -= 1
        if self.__dir < 0:
            self.__dir = len(self.directions)-1
        return self
    
    def turn_left(self):
        """
        Turns direction anticlockwise
        """
        self.__dir +=1
        if self.__dir >= len(self.directions):
            self.__dir = 0
        return self
            
    def __eq__(self, other):
        return self.__dir == other.__dir
    
    def __hash__(self):
        return self.__dir
    
    def __unicode__(self):
        return u"Dir: '%s'" % self.directions[self.__dir]
        
    def copy(self):
        """
        @return: copy of direction
        """
        return Direction(self.directions[self.__dir])
    def angle(self):
        return {
            'n': -90,
            'e': 0,
            's': 90,
            'w': 180,
        }[self.directions[self.__dir]]



class Coords(object):
    """
    Coordinate of some object in game map
    """
    __offset_dir = {
        Direction('n'): lambda x, y, o: (x, y-o),
        Direction('s'): lambda x, y, o: (x, y+o),
        Direction('w'): lambda x, y, o: (x-o, y),
        Direction('e'): lambda x, y, o: (x+o, y),
        }
    def __init__(self, x, y):
        """
        @param x: X coordinate
        @param y: Y coordinate
        """
        self.x, self.y = x,y
        
    def __eq__(self, other):
        return self.x==other.x and self.y==other.y
    
    def get_offset(self, direction, offset=1):
        """
        @param direction: to which direction go
        @param offset: coordination offset
        @return: coords with offset
        """
        return Coords(*self.__offset_dir[direction](self.x, self.y, offset))
    
    def move(self, direction, offset=1):
        """
        Moves coordinates to direction
        @param direction: to which direction go
        @param offset: coordination offset
        @return: coords with offset
        """
        #new = self.get_offset(direction, offset)
        (self.x, self.y) = (self.__offset_dir[direction](self.x, self.y, offset))
        
    def __unicode__(self):
        return u"Coords: %d,%d" % (self.x, self.y)
    
    def copy(self):
        """
        @return: copy of coordinates
        """
        return Coords(self.x, self.y)
         



class MapObject(object):
    """
    Game object on game map
    """
    def __init__(self, world, coord):
        """
        @param world: GameMap object
        @param coord: Coordinates of map object
        """
        self.coord = coord.copy()
        self.world = world
        self.world.add_object(self)
        
    def tick(self):
        """
        Performs one game tick
        """
        pass
        
class Player(object):
    """
    Player object
    """
    __casts = {
        "create_robot": 20,
        "run": 30,
        "stop": 25,
    }
    def __init__(self, name, game):
        """
        @param name: name of player
        @param game: game
        """
        self.game = game
        self.game.players.append(self)
        self.name = name
        self.robots = []
        
        self.max_mana = 200
        self.mana_regeneration = 1
        self.mana = self.max_mana

    def cast(self, cast, *args):
        """
        Casts game cast
        @param cast: name of cast
        @param args: arguments for cast
        @return: game objects, results of cast ()
        """
        if cast is 'run':
            for robot in self.robots:
                robot.run()
        if cast is 'stop':
            for robot in self.robots:
                robot.stop()
        if cast is 'create_robot':
            robot = Robot(world=self.game.gamemap, coords=args[0], player=self,\
                          direction=args[1])
            return robot
        if cast in self.__casts:
            self.mana -= self.__casts[cast]
    
    def place_operator(self, operator, coords):
        """
        Places operator object to coords at gamemap
        @param operator: operator name
        @param coords: coordinators
        @return: operator object
        """
        return BFOperator(world=self.game.gamemap, coords=coords, player=self, op_text=operator)

    def tick(self):
        if self.mana < self.max_mana:
            self.mana += self.mana_regeneration
    
    def get_casts(self):
        """
        Returns all availably casts and mana cost as dict
        """
        return self.__casts
    def outputs(self):
        return [robot.output for robot in self.robots]
            

class Memory(object):
    """
    Memory of robot object
    """
    def __init__(self):
        self.__pointer = 0
        self.__memory = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

    def inc(self):
        """
        Increase current register value
        """
        self.__memory[self.__pointer] += 1

    def dec(self):
        """
        Decrease current register value
        """
        self.__memory[self.__pointer] -= 1

    def inc_ptr(self):
        """
        Shifts current register pointer to right
        """
        self.__pointer += 1

    def dec_ptr(self):
        """
        Shifts current register pointer to left
        """
        self.__pointer -= 1
    
    def current(self):
        """
        @return: current register value
        """
        return  self.__memory[self.__pointer] 
    
    def input(self, data):
        """
        Saves data to current register
        @param data: integer value to save
        """
        self.__memory[self.__pointer] = data 
    
    def get_memory(self):
        """
        Returns memory state
        @return: tuple of memory list and memory current register pointer
        """
        res = [el for el in self.__memory]
        return (res, self.__pointer)

class WrongBFOperatorTextError(Exception):
    pass

class BFOperator(MapObject):
    """
    Operator of BrainFuck dialect on game map
    """

    valid_operators = "/\\,.<>+-[] "
    
    def __init__(self, world, coords, player, op_text):
        """
        @param world: game map
        @param coords: coordinates of object
        @param player: player, that places operator
        @param op_text: operator name
        """
        super(BFOperator, self).__init__(world, coords)
        self.player = player
        if len(op_text)==1 and op_text in self.valid_operators:
            self.operator = op_text
        else:
            raise WrongBFOperatorTextError

import numerology

class WrongLettersTextError(Exception):
    pass

class Letter(MapObject):
    """
    Letter on game map
    """
    
    def __init__(self, world, coords, letter_text):
        """
        @param world: game map
        @param coords: coordinates of letter
        @param letter_text: string that contains letter
        """
        super(Letter, self).__init__(world, coords)
        numerology.alpha_to_int(letter_text)
        if len(letter_text)==1:
            self.letter = letter_text
        else:
            raise WrongBFOperatorTextError
            
        
class Robot(MapObject):
    """
    Robot object, also known as 'Ghost'
    """
    def __init__(self, world, coords, player, direction=Direction('n')):
        """
        @param world: game map
        @param coords: coordinates of letter
        @param player: player that creates robot
        @param direction: initial direction of robot
        """
        super(Robot, self).__init__(world, coords)
        self.player = player
        self.player.robots.append(self)
        self.direction = direction.copy()
        self.memory = Memory()

        self.__operators_func = { 
            "\\": lambda op: None,
            r"/": lambda op: None,
            "+": lambda op: self.memory.inc(),
            "-": lambda op: self.memory.dec(),
            ">": lambda op: self.memory.inc_ptr(),
            "<": lambda op: self.memory.dec_ptr(),
            ".": lambda op: self.putchar(),
            ",": lambda op: self.getchar(),
            "[": lambda op: self.begin_cycle(op),
            "]": lambda op: self.end_cycle(op),
        }
        self.__cycle_stack = []
        
        self.__running = False
        self.output = ""
        self.trapped = False
    
    def putchar(self):
        """
        Puts current registry value to output
        """
        self.output += numerology.int_to_alpha(self.memory.current())

    def getchar(self):
        """
        Gets letter from game map to current registry value
        """
        letter = self.world.get_letter(self.coord)
        if letter is not None:
            l = letter.letter
            self.memory.input(numerology.alpha_to_int(l))
        else:
            self.memory.input(0)
            
        
        
    def begin_cycle(self, operator):
        if self.memory.current()==0:
            cur_operator = operator
            while cur_operator.operator!="]":
                self.step()
                cur_operator = self.world.get_bfoperator(self.coord)
        else:
            self.__cycle_stack.append((operator, self.direction))

            
        
    def end_cycle(self, operator):
        if self.memory.current()!=0:
            last, lastdir = self.__cycle_stack.pop()
            self.coord = Coords(last.coord.x, last.coord.y)
            self.direction = lastdir
            self.begin_cycle(self.world.get_bfoperator(self.coord))
        else:
            self.__cycle_stack.pop()
            
        
    def run(self):
        """
        Runs robot
        """
        self.__running = True
        
    def stop(self):
        """
        Stops robot
        """
        self.__running = False


    def execute(self, operator):
        """
        Executes operator
        @param operator: operator to execute
        """
        self.__operators_func[operator.operator](operator)
    
    def step(self, in_cycle=False):
        self.coord.move(self.direction,1)
        current_operator = self.world.get_bfoperator(self.coord)
        if current_operator is not None:
            if current_operator.operator=="/":
                self.direction.turn_right()
            if current_operator.operator=="\\":
                self.direction.turn_left()
            
        
    def tick(self):
        if self.__running:
            self.step()
            current_operator = self.world.get_bfoperator(self.coord)
            if current_operator is not None:
                self.execute(current_operator)
                
            
            


class NonUniqueMapObjectsError(Exception):
    pass

            
            
class Map(object):
    """
    Game map
    """
    def __init__(self, size_x, size_y, place_letters = True):
        """
        @param size_x: Size by X axe
        @param size_y: Size by Y axe
        @param place_letters: if true, fills map with random letters
        """
        self.size_x, self.size_y = size_x, size_y
        self.map_objects = []
        self.robots = []
        self.bfoperators = []
        self.letters = []
        
        if place_letters:
            self.place_random_letters(20)
    
    def place_random_letters(self, prob):
        """
        Places random letters to map
        @param prob: probability of letter
        """
        for x in range(self.size_x):
            for y in range(self.size_y):
                if random.randint(0,100)<prob:
                    l = string.uppercase[random.randint(0,len(string.uppercase)-1)]
                    Letter(self, Coords(x, y), l)
                
    
    @classmethod
    def from_list(cls, map_as_str_list):
        """
        Creates map object from string list
        @param map_as_str_list: string list that contains brainfuck operators
        @return: Map object
        """
        m = cls(max([len(line) for line in map_as_str_list]),len(map_as_str_list), place_letters = False)
        for y in range(len(map_as_str_list)):
            for x in range(len(map_as_str_list[y])):
                if map_as_str_list[y][x]!=' ':
                    BFOperator(m, Coords(x, y),\
                        None, map_as_str_list[y][x])
        return m
    
    def to_list(self):
        """
        Converts map to string list
        @return: String list that contains brainfuck operators
        """
        l = []
        
        for y in range(self.size_y):
            line = ""
            for x in range(self.size_x):
                op = self.get_bfoperator(Coords(x,y))
                if op is not None:
                    line += op.operator
                else:
                    line += " "
                
            l.append(line)
                
        return l
        
    def add_object(self, obj):
        """
        Adds object to map
        @param obj: object to add
        """
        self.map_objects.append(obj)
        if obj.__class__ is BFOperator:
            objs = self.bfoperators
        if obj.__class__ is Robot:
            objs = self.robots
        if obj.__class__ is Letter:
            objs = self.letters
        
        duplicate = False 
        for old_obj in objs:
            if old_obj.coord == obj.coord:
                duplicate = True
                objs.remove(old_obj)
        objs.append(obj)
        
    def get_objects(self, coord):
        """
        Returns all objects in specified coordinates
        @param coord: coordinates
        @return: list of game objects
        """
        return [obj for obj in self.map_objects if obj.coord == coord]
    
    def get_bfoperator(self, coord):
        """
        Returns one BFOperator object in specified coordinates
        @param coord: coordinates
        @return: game object
        """
        return self.__get_unique_obj_by_coord(self.bfoperators, coord)
    
    def get_robot(self, coord):
        """
        Returns one Robot object in specified coordinates
        @param coord: coordinates
        @return: game object
        """
        return self.__get_unique_obj_by_coord(self.robots, coord)

    def get_letter(self, coord):
        """
        Returns one Letter object in specified coordinates
        @param coord: coordinates
        @return: game object
        """
        return self.__get_unique_obj_by_coord(self.letters, coord)

    @staticmethod
    def __get_unique_obj_by_coord(l, coord):
        """
        Returns one object in specified coordinates
        @param coord: coordinates
        @return: game object
        """
        results = [obj for obj in l if obj.coord == coord]
        if len(results)==0:
            return None
        elif len(results)==1:
            return results[0]
        else:
            raise NonUniqueMapObjectsError


    def tick(self):
        for obj in self.map_objects:
            obj.tick()
        
import demonname
class Game(object):
    """
    Game
    """
    gametypes = {
        "demo":(demonname.get_small_demon,),
        "small":(demonname.get_small_demon,),
        "middle":(demonname.get_middle_demon,),
        "great":(demonname.get_great_demon,),
        }
    def __init__(self, gamemap, gametype="middle", victory_cb=None):
        """
        @param gamemap: Map instance
        @param gametype: name of game type
        @param victory_cb: function that calls on victory with player as arg
        """
        self.gamemap = gamemap
        self.players = []
        self.win_player = None
        
        self.gametype = self.gametypes[gametype]
        self.demon_name = self.gametype[0]().upper()
        self.victory_cb = victory_cb

    def add_player(self, player):
        """
        Adds player to game
        @param player: player object
        """
        self.players.append(player)
        player.game = self
   
    def __victory(self, list_of_outputs):
        result = ""
        for o in list_of_outputs:
            if o in self.demon_name:
                result += o
        return result==self.demon_name
            
    
    def tick(self):
        for player in self.players:
            player.tick()
            if self.__victory(player.outputs()):
                self.win_player = player
                if self.victory_cb is not None:
                    self.victory_cb(player)
        self.gamemap.tick()
        
        for robot in self.gamemap.robots:
            if robot.output!="" and robot.output not in self.demon_name:
                robot.trapped = True
        
        


if __name__=="__main__":
    map = Map(15,4)

    r = map.get_object_by_id('3')

