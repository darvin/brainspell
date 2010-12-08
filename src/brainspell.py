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
    directions = ['n', 'w', 's', 'e']
    def __init__(self, dir_str):
        if dir_str not in self.directions:
            raise WrongDirectionName
        if dir_str in self.directions:
            self.__dir = self.directions.index(dir_str)
        else:
            raise AssertionError
    
        
    def turn_right(self):
        self.__dir -= 1
        if self.__dir < 0:
            self.__dir = len(self.directions)-1
        return self
    
    def turn_left(self):
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
        
    



class Coords(object):
    __offset_dir = {
        Direction('n'): lambda x, y, o: (x, y-o),
        Direction('s'): lambda x, y, o: (x, y+o),
        Direction('w'): lambda x, y, o: (x-o, y),
        Direction('e'): lambda x, y, o: (x+o, y),
        }
    def __init__(self, x, y):
        self.x, self.y = x,y
        
    def __eq__(self, other):
        return self.x==other.x and self.y==other.y
    
    def get_offset(self, direction, offset=1):
        return Coords(*self.__offset_dir[direction](self.x, self.y, offset))
    
    def move(self, direction, offset=1):
        #new = self.get_offset(direction, offset)
        (self.x, self.y) = (self.__offset_dir[direction](self.x, self.y, offset))
    def __unicode__(self):
        return u"Coords: %d,%d" % (self.x, self.y)
         



class MapObject(object):
    def __init__(self, world, coord):
        self.__coord = coord
        self.world = world
        self.world.add_object(self)
        
        print self.world.get_bfoperator(self.coord)
    coord = property(lambda self: self.__coord)
    
        
        
        
        
        
    def tick(self):
        pass
        
class Player(object):
    __casts = {
        "create_robot": 20,
        "run": 30,
        "stop": 25,
    }
    def __init__(self, name, game):
        self.game = game
        self.game.players.append(self)
        self.name = name
        self.robots = []
        
        self.max_mana = 200
        self.mana_regeneration = 1
        self.mana = self.max_mana

    def cast(self, cast, *args):
        print cast
        if cast is 'run':
            for robot in self.robots:
                robot.run()
        if cast is 'stop':
            for robot in self.robots:
                robot.stop()
        if cast is 'create_robot':
            robot = Robot(world=self.game.gamemap, coords=args[0], player=self,\
                          direction=args[1])
        if cast in self.__casts:
            self.mana -= self.__casts[cast]
    
    def place_operator(self, operator, coords):
        op = BFOperator(world=self.game.gamemap, coords=coords, player=self, op_text=operator)

    def tick(self):
        if self.mana < self.max_mana:
            self.mana += self.mana_regeneration
    
    def get_casts(self):
        """
        Returns all availably casts and mana cost as dict
        """
        return self.__casts

class Memory(object):
    def __init__(self):
        self.__pointer = 0
        self.__memory = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

    def inc(self):
        self.__memory[self.__pointer] += 1

    def dec(self):
        self.__memory[self.__pointer] -= 1

    def inc_ptr(self):
        self.__pointer += 1

    def dec_ptr(self):
        self.__pointer -= 1
    
    def current(self):
        return  self.__memory[self.__pointer] 
    
    def get_memory(self):
        res = [el for el in self.__memory]
        return (res, self.__pointer)

class WrongBFOperatorTextError(Exception):
    pass

class BFOperator(MapObject):

    valid_operators = "/\\,.<>+-[] "
    
    def __init__(self, world, coords, player, op_text):
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
    
    def __init__(self, world, coords, letter_text):
        super(Letter, self).__init__(world, coords)
        numerology.alpha_to_int(letter_text)
        if len(letter_text)==1:
            self.letter = letter_text
        else:
            raise WrongBFOperatorTextError
            
        
class Robot(MapObject):
    def __init__(self, world, coords, player, direction=Direction('n')):
        super(Robot, self).__init__(world, coords)
        self.player = player
        self.player.robots.append(self)
        self.direction = direction
        self.memory = Memory()

        self.__operators_func = { 
            "\\": lambda op: None,
            r"/": lambda op: None,
            "+": lambda op: self.memory.inc(),
            "-": lambda op: self.memory.dec(),
            ">": lambda op: self.memory.inc_ptr(),
            "<": lambda op: self.memory.dec_ptr(),
            ".": lambda op: self.putchar(),
            "[": lambda op: self.begin_cycle(op),
            "]": lambda op: self.end_cycle(op),
        }
        self.__cycle_stack = []
        
        self.__running = False
        self.output = ""
    
    def putchar(self):
        self.output += numerology.int_to_alpha(self.memory.current())

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
        self.__running = True
        
    def stop(self):
        self.__running = False


    def execute(self, operator):
        print operator.operator, operator.coord.__unicode__(), self.direction.__unicode__()
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
    def __init__(self, size_x, size_y, place_letters = True):
        self.size_x, self.size_y = size_x, size_y
        self.map_objects = []
        self.robots = []
        self.bfoperators = []
        self.letters = []
        
        if place_letters:
            self.place_random_letters(20)
    
    def place_random_letters(self, prob):
        for x in range(self.size_x):
            for y in range(self.size_y):
                if random.randint(0,100)<prob:
                    l = string.uppercase[random.randint(0,len(string.uppercase)-1)]
                    Letter(self, Coords(x, y), l)
                
    
    @classmethod
    def from_list(cls, map_as_str_list):
        print map_as_str_list
        m = cls(max([len(line) for line in map_as_str_list]),len(map_as_str_list), place_letters = False)
        for y in range(len(map_as_str_list)):
            for x in range(len(map_as_str_list[y])):
                if map_as_str_list[y][x]!=' ':
                    BFOperator(m, Coords(x, y),\
                        None, map_as_str_list[y][x])
        return m
    
    def to_list(self):
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
        self.map_objects.append(obj)
        if obj.__class__ is BFOperator:
            objs = self.bfoperators
        if obj.__class__ is Robot:
            objs = self.robots
        if obj.__class__ is Letter:
            objs = self.letters
        
        for old_obj in objs:
            if old_obj.coord == obj.coord:
                objs.remove(old_obj)
        objs.append(obj)
        
    def get_objects(self, coord):
        return [obj for obj in self.map_objects if obj.coord == coord]
    
    def get_bfoperator(self, coord):
        print len(self.bfoperators)
        return self.__get_unique_obj_by_coord(self.bfoperators, coord)
    
    def get_robot(self, coord):
        return self.__get_unique_obj_by_coord(self.robots, coord)

    def get_letter(self, coord):
        return self.__get_unique_obj_by_coord(self.letters, coord)

    @staticmethod
    def __get_unique_obj_by_coord(l, coord):
        results = [obj for obj in l if obj.coord == coord]
        print len(l), len(results)
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
    gametypes = {
        "demo":(demonname.get_small_demon,),
        "small":(demonname.get_small_demon,),
        "middle":(demonname.get_middle_demon,),
        "great":(demonname.get_great_demon,),
        }
    def __init__(self, gamemap, gametype="middle"):
        
        self.gamemap = gamemap
        self.players = []
        
        self.gametype = self.gametypes[gametype]
        self.demon_name = self.gametype[0]()

    def add_player(self, player):
        self.players.append(player)
        player.game = self
    
    def tick(self):
        for player in self.players:
            player.tick()
        self.gamemap.tick()
        


if __name__=="__main__":
    map = Map(15,4)

    r = map.get_object_by_id('3')

