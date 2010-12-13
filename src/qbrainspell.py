#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
import copy
import functools
import PyQt4
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtSvg import *
import brainspell
import numerology
import images_rc
from utils import odict


GRID_COLOR = QColor(111,111,111)
GRID_SIZE = 30.0

PLAYER_COLORS = [
    (QColor(12,66,12), "devil",),
    (QColor(120,61,12), "angel",),
    (QColor(110,12,34), "cyborg",),
    (QColor(12,66,12), "geisha",),
    (QColor(12,66,12), "wall",),
    (QColor(12,66,12), "pirate",),
]



def layout_clear(layout):
    while True:
            child = layout.takeAt(0)
            if child is not None:
                w = child.widget()
                if child.layout() is not None:
                    layout_clear(child.layout())
                if w is not None:
                    w.hide()
                del w
                del child
            else:
                break
        


class NewGameDialog(QDialog):
    def __init__(self, parent=None):
        super(NewGameDialog, self).__init__(parent=parent)
        self.setModal(True)
        formlayout = QFormLayout()
        self.setLayout(formlayout)
        
        self.size_x = QSpinBox()
        self.size_x.setValue(30)
        self.size_y = QSpinBox()
        self.size_y.setValue(20)
        self.players = QSpinBox()
        self.players.setValue(1)
        self.letter_prob = QSpinBox()
        self.letter_prob.setValue(20)
        formlayout.addRow(u"Size X:", self.size_x)
        formlayout.addRow(u"Size Y:", self.size_y)
        formlayout.addRow(u"Number of players:", self.players)
        formlayout.addRow(u"Probability of letters:", self.letter_prob)
        
        buttonbox = QDialogButtonBox(QDialogButtonBox.Ok| QDialogButtonBox.Cancel)
        buttonbox.rejected.connect(self.reject)
        buttonbox.accepted.connect(self.accept)
        formlayout.addRow(buttonbox)

        
class NumerologyLabel(QWidget):
    def __init__(self, text="", parent=None, game=None):
        super(NumerologyLabel, self).__init__(parent=parent)
        
        self.hlayout = QHBoxLayout()
        self.setLayout(self.hlayout)
        self.setText(text)
    def setText(self, text):
        
        layout_clear(self.hlayout) 
        for c in text:
            letter = QLabel(c)
            number = QLabel("%d"%numerology.alpha_to_int(c))
            layout = QVBoxLayout()
            layout.addWidget(letter)
            layout.addWidget(number)
            self.layout().addLayout(layout)
            
        
    def highlight_letter(self, index):
        c = self.layout().itemAt(index)
        if c is not None:
            l = c.layout()
            w = l.itemAt(0).widget()
            w.setStyleSheet("color: green")

    
        
class DemonName(QWidget):
    def __init__(self, parent=None, game=None):
        super(DemonName, self).__init__(parent=parent)
        self.game=game
        self.demon_name = NumerologyLabel()
        alphabet = NumerologyLabel([numerology.int_to_alpha(i) for i in range(numerology.MIN_NUMBER, numerology.MAX_NUMBER)])
        vlayout = QVBoxLayout()
        vlayout.addWidget(alphabet)
        vlayout.addWidget(self.demon_name)
        self.setLayout(vlayout)
        
            
    def set_name(self, name):
        self.demon_name.setText(name)
        
    def tick(self):
        for index in self.game.current_player.get_correct_indexes():
            self.demon_name.highlight_letter(index)
    
        

    def redraw_game(self):
        self.set_name(self.game.demon_name)
   
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
        animation.setDuration(300);
        
        
        if abs(self.__last_direction%360-direction.angle())==270:
            angle = 360*(self.__last_direction/360+1)+direction.angle()
        
        else:
            angle = 360*(self.__last_direction/360) + direction.angle()
            
        animation.setEndValue(angle)

        animation.start()
        
        self.__last_direction = angle
            

 
class OperatorItem(PieceSizedQGraphicsSvgItem):
    def __init__(self, coords, operator_actions, parent=None):
        super(OperatorItem, self).__init__(None, parent=parent)
        self.operator_actions = operator_actions
        self.setPos(self.coords_to_qpointf(coords))
    def set_operator(self, operator):
        if operator.player is not None:
            self.setSharedRenderer(operator.player.operator_svgs[operator.operator])
        else:
            self.setSharedRenderer(self.operator_actions[operator.operator].svg_renderer)
        
      
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

        if op is not None:
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
    
    def tick(self, first=False):
        if first:
            self.setPos(self.coords_to_qpointf(self.robot.coord))
        else:
            self.rotate_to(self.robot.direction)
            self.move_to(self.robot.coord)
            
    #def rotate_to(self, direction)
            
              
class PlaygroundScene(QGraphicsScene):
    piece_size = GRID_SIZE
    def __init__(self, operator_actions, parent=None, game=None):
        super(PlaygroundScene, self).__init__(parent=parent)
        self.game = game
        self.operator_actions = operator_actions
        self.pieces = []
        
        for i in range(self.game.gamemap.size_x+1):
            self.addLine(i*self.piece_size, 0, i*self.piece_size, self.piece_size*self.game.gamemap.size_y, QPen(GRID_COLOR))
        for i in range(self.game.gamemap.size_y+1):
            self.addLine(0, i*self.piece_size, self.piece_size*self.game.gamemap.size_x, i*self.piece_size, QPen(GRID_COLOR))
        
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
            self.scene = PlaygroundScene(parent=self, game=self.game, operator_actions=self.operator_actions)
            self.setScene(self.scene) 
            self.show()
    def add_robot(self, robot):
        self.scene.add_robot(robot)

class SvgRobotWidget(QSvgWidget):
    __size = 70
    def sizeHint(self):
        return QSize(self.__size,self.__size)
    

class RobotWidget(QWidget):
    def __init__(self, robot, parent=None):
        super(RobotWidget, self).__init__(parent)
        self.robot = robot
        
        layout = QVBoxLayout()
        self.memory = QLabel()
        self.output = NumerologyLabel()
        self.debug = QLabel()
        layout.addWidget(self.memory)
        layout.addWidget(self.debug)
        layout.addWidget(self.output)
        
        robot_picture = SvgRobotWidget(":/robots/"+PLAYER_COLORS[robot.player.color_number][1]+".svg")
        
        robot_picture.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        hlayout = QHBoxLayout()
        hlayout.addWidget(robot_picture)
        hlayout.addLayout(layout)
        self.setLayout(hlayout)
        
    def redraw_game(self):
        pass
    
    def tick(self):
        m, p = self.robot.memory.get_memory()
        m_st = ""
        for elem, i in zip(m, range(len(m))):
            if i==p:
                m_st += "<b>%d</b> "%elem
            else:
                m_st += "%d "%elem
                
            
        self.memory.setText(m_st)
        self.output.setText(self.robot.output)
        if not self.robot.trapped:
            for i in range(len(self.robot.output)):
                self.output.highlight_letter(i)
        
        self.debug.setText(self.robot.coord.__unicode__()+" "+\
                           self.robot.direction.__unicode__() + " "+unicode (self.robot.trapped))


           
           
class ManaBar(QProgressBar):
    def text(self):
        return "%d" % self.value()

class PlayerWidget(QWidget):
    def __init__(self, player, parent=None):
        super(PlayerWidget, self).__init__(parent)
        self.player = player
        self.vblayout = layout = QVBoxLayout()
        self.setLayout(layout)
        self.name_label = QLabel()
        self.mana_bar = ManaBar()
        layout.addWidget(self.name_label)
        layout.addWidget(self.mana_bar)
        self.robots = []
        pal = QPalette()
        pal.setColor(QPalette.Window, self.player.qcolor)
        pal.setColor(QPalette.WindowText, Qt.white)
        self.setPalette(pal)
        self.setAutoFillBackground(True)
        
    def redraw_game(self):
        self.mana_bar.setMaximum(self.player.max_mana)
        self.name_label.setText(self.player.name)
        for robot in self.player.robots:
            self.add_robot(robot)
                        
    def add_robot(self, robot):
        r = RobotWidget(robot)
        self.vblayout.addWidget(r)
        self.robots.append(r)
        r.redraw_game()
        

    
    def tick(self):
        for robot in self.player.robots:
            new = True
            for robot_w in self.robots:
                if robot_w.robot == robot:
                    new = False
            if new:
                self.add_robot(robot)
                
        for robot in self.robots:
            robot.tick()
        
        self.mana_bar.setValue(self.player.mana)




class CastsWidget(QWidget):
    def __init__(self, player, cast_actions, parent=None):
        super(CastsWidget, self).__init__(parent)
        self.player = player
        self.cast_actions = cast_actions
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.casts = {}
        
    def redraw_game(self):
        avail_casts = self.player.get_casts()
        for castname, castcost in avail_casts.items():
            button = QPushButton(self.cast_actions[castname].text())
            button.clicked.connect(self.cast_actions[castname].triggered)
            self.casts[castname] = (button, castcost)
            self.layout().addWidget(button)
            
    def tick(self):
        for castname, (button, castcost) in self.casts.items():
            button.setEnabled((castcost<=self.player.mana))
            self.cast_actions[castname].setEnabled((castcost<=self.player.mana))






class SideDock(QDockWidget):
    def __init__(self, name, cast_actions, operator_actions, parent=None, game=None):
        super(SideDock, self).__init__(name, parent)
        self.game = game
        self.cast_actions, self.operator_actions = cast_actions, operator_actions
        w = QWidget()
        self.vblayout = QVBoxLayout()
        w.setLayout(self.vblayout)
        self.setWidget(w)
        self.players = []
    
    def redraw_game(self):
        self.players = []
        layout_clear(self.vblayout)
        #fixme!
                
        for player in self.game.players:
            player_w = PlayerWidget(player)
            self.players.append(player_w)
            self.vblayout.addWidget(player_w)

        self.vblayout.addItem(QSpacerItem(20, 20, \
                    QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        self.casts = CastsWidget(parent=self, player=self.game.current_player, cast_actions=self.cast_actions)
        self.vblayout.addWidget(self.casts)
        
        
        for player in self.players:
            player.redraw_game()

        self.casts.redraw_game()
        
        oper_toolbar = QToolBar()
        self.vblayout.addWidget(oper_toolbar)
        for operator, oa in self.operator_actions.items():
            oper_toolbar.addAction(oa)
            
       
               
            
        
    def tick(self):
        for player in self.players:
            player.tick()
                
        self.casts.tick()
    
    


class MainForm(QMainWindow):
       
    def __init__(self):
        self.__casts = odict({
            "run": (u"Run robots", None),
            "stop": (u"Stop robots", None),
            "create_robot": (u"Create robot", self.create_robot),
        })
        
        self.__operators = odict.from_tuple((
           ( ">", (u"Next register", "greaterthan", None, Qt.Key_Greater)),
           ( "<", (u"Previous register", "lessthan", None, Qt.Key_Less)),
           ( "+", (u"Increase", "plus", None, Qt.Key_Plus)),
           ( "-", (u"Decrease", "minus", None, Qt.Key_Minus)),
           ( "[", (u"Begin cycle", "leftbracket", None, Qt.Key_BracketLeft)),
           ( "]", (u"End cycle", "rightbracket", None, Qt.Key_BracketRight)),
           ( ".", (u"Output current register", "dot", None, Qt.Key_O)),
           ( ",", (u"Input to current register", "comma", None, Qt.Key_I)),
           ( "/", (u"Rotate robot clockwise", "clockwise", None, Qt.Key_Slash)),
           ( "\\", (u"Rotate robot anticlockwise", "anticlockwise", None, Qt.Key_Backslash)),
        ))
        
        self.__directions = {
            "n": (u"North", Qt.Key_Up),
            "e": (u"East", Qt.Key_Right),
            "w": (u"West", Qt.Key_Left),
            "s": (u"South", Qt.Key_Down),
        }

        super(MainForm, self).__init__()
        self.resize(800,600)
        self.setWindowTitle('QBrainSpell')
        
        self.tick_timer = QTimer(self)
        self.tick_timer.timeout.connect(self.tick)
        
        new_game_action = QAction(u"New game", self)
        new_game_action.triggered.connect(self.new_game)
        exit_action = QAction(u"Exit", self)
        exit_action.triggered.connect(self.close)
        import_action = QAction(u"Import", self)
        import_action.triggered.connect(self.import_)
        export_action = QAction(u"Export", self)
        export_action.triggered.connect(self.export)

        self.play_pause_action = play_pause_action = QAction(u"Play", self)
        play_pause_action.setCheckable(True)
        play_pause_action.toggled.connect(self.play_pause)
        step_action = QAction(u"Step", self)
        step_action.triggered.connect(self.step)

        menubar = self.menuBar()
        file_menu = menubar.addMenu(u"&Game")
        operators_menu = menubar.addMenu(u"&Operators")
        casts_menu = menubar.addMenu(u"&Casts")
        help_menu = menubar.addMenu(u"&Help")
        
        self.move_actions = {}
        for d, (name, key) in self.__directions.items():
            direction = brainspell.Direction(d)
            act = self.move_actions[direction] = QAction(name, self)
            act.setShortcut(QKeySequence(key))
            act.triggered.connect(functools.partial(self.move_current_coord, direction))
            self.addAction(act)
            
            
 
        self.cast_actions = odict()
        for cast, (casttitle, func) in self.__casts.items():
            ca = QAction(casttitle, self)
            if func is None:
                ca.triggered.connect(functools.partial(self.cast,cast))
            else:
                ca.triggered.connect(func)
            self.cast_actions[cast] = ca
            casts_menu.addAction(ca)
         
        self.operator_actions = odict()
        for operator, (optitle, opiconname, func, key) in self.__operators.items():
            oa = QAction(QIcon(":/"+opiconname+".svg"),optitle, self)
            oa.key = key
            oa.svg_renderer = QSvgRenderer(":/"+opiconname+".svg")
            if func is None:
                oa.triggered.connect(functools.partial(self.place_operator, operator))
            else:
                oa.triggered.connect(func)
            self.operator_actions[operator] = oa
            operators_menu.addAction(oa)
        
        file_menu.addAction(new_game_action)
        file_menu.addAction(play_pause_action)
        file_menu.addAction(step_action)
        file_menu.addAction(import_action)
        file_menu.addAction(export_action)
        file_menu.addAction(exit_action)
        
        layout = QVBoxLayout()
        widg = QWidget()
        widg.setLayout(layout)
        self.setCentralWidget(widg)
        self.demon_name = DemonName()
        self.playground = Playground(operator_actions = self.operator_actions)
        self.sidebar = SideDock(u"Information", self.cast_actions, self.operator_actions, self)
        self.sidebar.setAllowedAreas(Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, self.sidebar)
        sidebar_action = self.sidebar.toggleViewAction()
        
        layout.addWidget(self.demon_name)
        layout.addWidget(self.playground)
        
        toolbar = self.addToolBar("main")
        toolbar.addAction(new_game_action)
        toolbar.addAction(sidebar_action)
        toolbar.addAction(play_pause_action)
        toolbar.addAction(step_action)
               
        self.demo()
    
    def new_game(self):
        d = NewGameDialog(self)
        d.exec_()
        if d.result()==QDialog.Accepted:
            self.create_game(brainspell.Map(d.size_x.value(), d.size_y.value(), d.letter_prob.value()), d.players.value(), "middle")
            
            self.redraw_game()
            
    def demo(self):
        demo_map = [\
r"+++/",\
r"   +",\
r"   +",\
r".++/",\
                   ]
        gamemap = brainspell.Map.from_list(demo_map)
        self.create_game(gamemap, 1, "great")
       
        self.redraw_game()
        self.play_pause(True)
            
    def create_game(self, gamemap, players_num, gametype):
        self.game = brainspell.Game(gamemap, gametype, self.player_win)
        for i in range(players_num):
            pl = brainspell.Player(u"Player #%d"%i, self.game)
            pl.qcolor = PLAYER_COLORS[i][0]
        self.game.current_player = self.game.players[0]
        self.game.current_coord = brainspell.Coords(0,0)
        self.game.current_dir = brainspell.Direction('e')
        
        for i, player in enumerate(self.game.players):
            player.color_number = i
            player.operator_svgs = {}
            player.robot_svg = QSvgRenderer(":/robots/"+PLAYER_COLORS[i][1]+".svg")
            player.robot_svg

            for operator, (optitle, opiconname, func, key) in self.__operators.items():
                #FIXME!!!
                qi = QSvgRenderer(":/"+opiconname+".svg")# PLAYER_COLORS[i])
                player.operator_svgs[operator] = qi
    
                
    def place_operator(self, operator):
        self.game.current_player.place_operator(operator, self.game.current_coord)
        self.playground.update_piece(self.game.current_coord)
        newdir = self.game.current_dir.copy()
        if operator=="/":
            newdir.turn_right()
            self.move_current_coord(newdir)
        elif operator=="\\":
            newdir.turn_left()
            self.move_current_coord(newdir)
        self.move_current_coord(newdir)
    
    def move_current_coord(self, direction):
        if self.game.current_dir==direction:
            if self.game.current_coord.get_offset(direction).is_valid(\
                  self.game.gamemap):
                self.game.current_coord.move(direction)
                self.playground.scene.current_coord_change()
        else:
            self.game.current_dir = direction.copy()
            self.playground.scene.current_dir_change()
        
    def cast(self, cast):
        self.game.current_player.cast(cast)
        
        
    def redraw_game(self):
        self.demon_name.game = self.game
        self.sidebar.game = self.game
        self.playground.game = self.game
        self.demon_name.redraw_game()
        self.sidebar.redraw_game()
        self.playground.redraw_game()
        
    def tick(self):
        self.game.tick()
        self.demon_name.tick()
        self.playground.tick()
        self.sidebar.tick()
    
    def step(self):
        self.play_pause(play=False)
        self.tick()
    
    def import_(self):
        file_name = QFileDialog.getOpenFileName(\
            self, u"Import text file", directory=".",\
            filter = u"BrainSpell and BrainFuck (*.bs *.bf *.b)")
        if file_name:
            f = open(file_name)
            map_list = [line.rstrip() for line in f.readlines()]
            f.close()
            gamemap = brainspell.Map.from_list(map_list)
            self.create_game(gamemap, 1, "middle")
            self.redraw_game()
            
        
    def export(self):
        file_name = QFileDialog.getSaveFileName(\
            self, u"Export as text file", directory=".",\
            filter = u"BrainSpell and BrainFuck (*.bs *.bf *.b)")
        if file_name:
            f = open(file_name, "w")
            map_list = self.game.gamemap.to_list()
            f.writelines([line+"\n" for line in map_list])
            f.close()
    
        
    def play_pause(self, play):
        self.play_pause_action.setChecked(play)
        if play:
            self.play_pause_action.setText(u"Pause")
            self.tick_timer.start(1000)
            
        else:
            self.play_pause_action.setText(u"Play")
            self.tick_timer.stop()
    def create_robot(self):
        r = self.game.current_player.cast("create_robot", self.game.current_coord, self.game.current_dir)
        self.playground.add_robot(r)
    
    def player_win(self, player):
        mb = QMessageBox(self)
        mb.setText(u"Player %s wins!"%player.name)
        export = mb.addButton(u"Export game map", QMessageBox.ActionRole)
        new_game = mb.addButton(u"Start new game", QMessageBox.DestructiveRole)
        new_game.clicked.connect(self.new_game)
        export.clicked.connect(lambda: self.export() and self.new_game())
        mb.setDefaultButton(new_game)
        mb.exec_()
        
    def keyPressEvent(self, e):
        for act in self.operator_actions.values():
            if act.key == e.key():
                act.trigger()
    

def main():
    app = QApplication(sys.argv)
    w = MainForm()
    w.show()

    sys.exit(app.exec_())
                
if __name__=="__main__":
    main()
   