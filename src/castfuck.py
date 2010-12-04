import StringIO


def find_key(dic, val):
    """return the key of dictionary dic given the value"""
    for k, v in dic.items():
        if v == val:
            return k



class Coords(object):
    def __init__(self, x, y):
        self.x, self.y = x,y

class GameObject(object):
    def __init__(self, world, coords):
        self.world = world
        self.coords = coords

class Player(GameObject):
    def __init__(self, world, coords, name):
        super(Player, self).__init__(world, Coords(-1,-1))
        self.name = name
        self.robots = []

    def cast(self, cast):
        if cast is 'run':
            for robot in self.robots:
                robot.run()
        if cast is 'stop':
            for robot in self.robots:
                robot.stop()



class Direction(object):
    directions = ['n', 'w', 's', 'e']
    def __init__(self, dir_str):
        if dir_str in self.directions:
            self.__dir = dir_str
        else:
            raise AssertionError

class Memory(object):
    def __init__(self, pointer, memory):
        self.__pointer = pointer
        self.__memory = memory.split('.')

    def inc(self):
        self.__memory[self.__pointer] += 1

    def dec(self):
        self.__memory[self.__pointer] -= 1

    def inc_ptr(self):
        self.__pointer += 1

    def dec_ptr(self):
        self.__pointer -= 1


class Robot(GameObject):
    def __init__(self, world, coords, player_id, direction, pointer, memory):
        super(Robot, self).__init__(world, coords)
        self.player = self.world.get_object_by_id(player_id)
        self.player.robots.append(self)
        self.direction = Direction(direction)
        self.memory = Memory(pointer, memory)

        self.commands = { 
            "/": lambda: self.direction.turn_right,
            "\\": lambda: self.direction.turn_left,
            "+": self.memory.inc,
            "-": self.memory.dec,
            ">": self.memory.inc_ptr,
            "<": self.memory.dec_ptr,

        }


    def execute(self, command):
        self.commands[command]()


GAME_OBJECTS = {
    "player": Player,
    "robot":Robot,
}

def get_game_object_type_name(o):
    return find_key(GAME_OBJECTS, o.__class__)

VALID_COMMANDS = "/\\,.<>+-[] "

class Map(object):
    def __init__(self, size_x, size_y):
        self.size_x, self.size_y = size_x, size_y
        self.__map = []
        self.__game_objects = {}

    def from_str(self, str):
        f =  StringIO.StringIO(str)
        for line in f:
            if line=="%%\n":
                break
            else:
                self.create_game_object(*line.rstrip().lstrip().split(':'))
        for line in f:
            mapline = []
            for char in line:
                if char=="\n":
                    break
                elif char in VALID_COMMANDS:
                    mapline.append(char)
                else:
                    print "Wrong character input! '" +char +"'"
                    raise AssertionError
            self.__map.append(mapline)


    def create_game_object(self, index, obj_type, coords, args):
        self.__game_objects[index] = GAME_OBJECTS[obj_type](self,\
                                                            Coords(*coords.split(',')), *args.split(','))

    def get_object_by_id(self, obj_id):
        return self.__game_objects[obj_id]

    def get_id_of_object(self, obj):
        return find_key(self.__game_objects, obj)


if __name__=="__main__":
    map = Map(15,4)

    r = map.get_object_by_id('3')

