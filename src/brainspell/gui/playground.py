from PyQt4.QtSvg import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import brainspell
import settings


class PieceSizedQGraphicsSvgItem(QGraphicsSvgItem):
    def __init__(self, filename=None, parent=None):
        if filename is not None:
            super(PieceSizedQGraphicsSvgItem, self).__init__(QLatin1String(filename), parent=parent)
        else:
            super(PieceSizedQGraphicsSvgItem, self).__init__(parent=parent)
        self.__last_direction = 0
    def paint(self, painter, option, widget):
        self.renderer().render(painter, self.boundingRect())
    def boundingRect(self):
        br = super(PieceSizedQGraphicsSvgItem, self).boundingRect()
        size = self.scene().piece_size
        br.setSize(QSizeF(size, size))
        return br

    def coords_to_qpointf(self, coord):
        x, y = coord.x*self.scene().piece_size, \
                 coord.y*self.scene().piece_size
        return QPointF(x,y)


    def move_to(self, coord):
        self.__animation_m = animation =  QPropertyAnimation(self, "pos")
        animation.setDuration(300);
        animation.setStartValue(self.pos());
        animation.setEndValue(self.coords_to_qpointf(coord))

        animation.start()

    def rotate_to(self, direction):
        self.setTransformOriginPoint(self.scene().piece_size/2.0, self.scene().piece_size/2.0)
        self.__animation_r = animation =  QPropertyAnimation(self, "rotation")
        animation.setDuration(300)
        
        circles = self.__last_direction/360
            
        
        if abs(self.__last_direction%360-direction.angle())>=270:
            angle = 360*(circles+1)+direction.angle()
        else:
            angle = 360*(circles) + direction.angle()
        animation.setEndValue(angle)

        animation.start()
        self.__last_direction = angle



class OperatorItem(PieceSizedQGraphicsSvgItem):
    def __init__(self, coords, operator_actions, parent=None):
        super(OperatorItem, self).__init__(None, parent=parent)
        self.operator_actions = operator_actions
        self.setPos(self.coords_to_qpointf(coords))
    def set_operator(self, operator):
        if operator is not None:
            if operator.player is not None:
                self.setSharedRenderer(operator.player.operator_svgs[operator.operator])
            else:
                self.setSharedRenderer(self.operator_actions[operator.operator].svg_renderer)
        else:
            self.setSharedRenderer(QSvgRenderer(self))


class PlaygroundPiece(QGraphicsItem):
    def __init__(self, game, coord, operator_actions, parent=None, scene=None):
        super(PlaygroundPiece, self).__init__(parent=parent, scene=scene)
        self.game, self.coord = game, coord
        self.active = False
        self.operator_actions = operator_actions
        self.__operator_item = OperatorItem(self.coord, self.operator_actions, self)
        self.setAcceptedMouseButtons(Qt.LeftButton)
        
    def paint(self, painter, option, widget):
        br = self.boundingRect()
        try:
            letter = self.game.gamemap.get_letter(self.coord).letter
        except AttributeError:
            letter = None
        if letter is not None:
            painter.drawText(br, letter)
        
    def update(self):
        try:
            op = self.game.gamemap.get_bfoperator(self.coord)
        except AttributeError:
            op = None

        self.__operator_item.set_operator(op)
        
    def boundingRect(self):
        penWidth = 1.0
        size = self.scene().piece_size
        x = self.coord.x*size
        y = self.coord.y*size
        x2 = x+size
        y2 = y+size

        return QRectF( x, y,\
                       size + penWidth, size + penWidth)
    
    def mousePressEvent(self, ev):
        self.scene().current_coord_change(self.coord)


class CursorItem(PieceSizedQGraphicsSvgItem):
    def __init__(self, game, parent=None):
        super(CursorItem, self).__init__(":/cursor.svg", parent=parent)


class RobotItem(PieceSizedQGraphicsSvgItem):
    def __init__(self, robot, parent=None):
            
        super(RobotItem, self).__init__(parent=parent)
        self.setSharedRenderer(robot.player.robot_svg)
        self.robot = robot
        self.__last_direction = self.robot.direction.angle()
        self.__was_trapped = False
        self.__flipped = False
    
    def tick(self, first=False):
        if first:
            self.setPos(self.coords_to_qpointf(self.robot.coord))
        else:
            self.rotate_to(self.robot.direction)
            self.move_to(self.robot.coord)
        if self.robot.trapped and not self.__was_trapped:
            self.__was_trapped = True
            
            self.__animation_trap = animation =  QPropertyAnimation(self, "scale")
            animation.setDuration(300)
            animation.setEndValue(0.7)
            animation.start()

            self.__trap = PieceSizedQGraphicsSvgItem(':/trap.svg', self)
            self.__trap.setTransformOriginPoint(self.scene().piece_size/2.0, self.scene().piece_size/2.0)
            self.__trap.setScale(1.4)
            
            
    def __flip(self):
        self.__flipped = not self.__flipped
        m = self.transform()
        if self.__flipped:
            m.translate(self.scene().piece_size, 0).scale(-1,1)
        else:
            m.translate(0, 0).scale(1,1)
        self.setTransform(m, True)

            
    def rotate_to(self, direction):
        if direction==brainspell.Direction('w'):
            direction=brainspell.Direction('e')
            if not self.__flipped:
                self.__flip()
        elif direction==brainspell.Direction('e') and self.__flipped:
            self.__flip()
        super(RobotItem, self).rotate_to(direction)


class PlaygroundScene(QGraphicsScene):
    def __init__(self, operator_actions, parent=None, game=None, piece_size=30, grid_color=QColor(130,130,130)):
        super(PlaygroundScene, self).__init__(parent=parent)
        self.piece_size=piece_size
        self.game = game
        self.operator_actions = operator_actions
        self.pieces = []
        
        for i in range(self.game.gamemap.size_x+1):
            self.addLine(i*self.piece_size, 0, i*self.piece_size, self.piece_size*self.game.gamemap.size_y, QPen(grid_color))
        for i in range(self.game.gamemap.size_y+1):
            self.addLine(0, i*self.piece_size, self.piece_size*self.game.gamemap.size_x, i*self.piece_size, QPen(grid_color))
        
        for x in range(self.game.gamemap.size_x):
            for y in range(self.game.gamemap.size_y):
                piece = PlaygroundPiece(self.game, brainspell.Coords(x,y), self.operator_actions, scene = self)
                self.pieces.append(piece)
        
        self.cursor_item = CursorItem(game=self.game)
        self.addItem(self.cursor_item)
        
        self.robots = {}
        
        for piece in self.pieces:
            piece.update()
        

        
    def current_coord_change(self, coord = None):
        if coord is not None:
            self.game.current_coord = coord.copy()
        self.cursor_item.move_to(self.game.current_coord)
    def current_dir_change(self):
        self.cursor_item.rotate_to(self.game.current_dir)
        
    def update_piece(self, coord):
        for piece in self.pieces:
            if piece.coord == coord:
                piece.update()
    
    def tick(self):
        for robot in self.robots.values():
            robot.tick()
            
        #FIXME DEBUG ONLY
        #for piece in self.pieces:
        #    piece.update()
        
    def add_robot(self, robot):
        self.robots[robot] = r = RobotItem(robot)
        self.addItem(r)
        r.tick(first=True)


class Playground(QGraphicsView):
    def __init__(self, operator_actions, parent=None, game=None):
        super(Playground, self).__init__(parent=parent)
        self.operator_actions = operator_actions
        self.game = game
        self.redraw_game()
        
    def update_piece(self, coord):
        self.scene.update_piece(coord)
        
    def tick(self):
        self.scene.tick()
    
    def redraw_game(self):
        if self.game is not None:
            self.scene = PlaygroundScene(parent=self, game=self.game, operator_actions=self.operator_actions, piece_size = settings.GRID_SIZE, grid_color=settings.GRID_COLOR)
            self.setScene(self.scene) 
            self.show()
    def add_robot(self, robot):
        self.scene.add_robot(robot)