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
import images_rc
from utils import odict

PLAYER_COLORS = [
    QColor(12,66,12),
    QColor(120,61,12),
    QColor(110,12,34),
    QColor(12,66,12),
    QColor(12,66,12),
    QColor(12,66,12),
]


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
        formlayout.addRow(u"Size X:", self.size_x)
        formlayout.addRow(u"Size Y:", self.size_y)
        formlayout.addRow(u"Number of players:", self.players)
        
        buttonbox = QDialogButtonBox(QDialogButtonBox.Ok| QDialogButtonBox.Cancel)
        buttonbox.rejected.connect(self.reject)
        buttonbox.accepted.connect(self.accept)
        formlayout.addRow(buttonbox)

        
class DemonName(QLabel):
    def __init__(self, parent=None, game=None):
        super(DemonName, self).__init__(parent=parent)
        self.game=game
     
    def set_name(self, name):
        self.setText(u"Current demon: "+name)
        
    def tick(self):
        pass

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
        animation.setStartValue(self.__last_direction);
        animation.setEndValue(direction.angle())

        animation.start()
        
        self.__last_direction = direction.angle()
            

 
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
            
              
class PlaygroundScene(QGraphicsScene):
    piece_size = 50.0
    def __init__(self, operator_actions, parent=None, game=None):
        super(PlaygroundScene, self).__init__(parent=parent)
        self.game = game
        self.operator_actions = operator_actions
        self.pieces = []
        
        for i in range(self.game.gamemap.size_x+1):
            self.addLine(i*self.piece_size, 0, i*self.piece_size, self.piece_size*self.game.gamemap.size_y)
        for i in range(self.game.gamemap.size_y+1):
            self.addLine(0, i*self.piece_size, self.piece_size*self.game.gamemap.size_x, i*self.piece_size)
        
        for x in range(self.game.gamemap.size_x):
            for y in range(self.game.gamemap.size_y):
                piece = PlaygroundPiece(self.game, brainspell.Coords(x,y), self.operator_actions, scene = self)
                self.pieces.append(piece)
        
        self.cursor_item = CursorItem(game=self.game)
        self.addItem(self.cursor_item)
        
        self.robots = {}
        
        for piece in self.pieces:
            piece.update()
        

        
    def current_coord_change(self, coord):
        self.cursor_item.move_to(coord)
        self.game.current_coord = brainspell.Coords(coord.x, coord.y)
        
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
 
class RobotWidget(QWidget):
    def __init__(self, robot, parent=None):
        super(RobotWidget, self).__init__(parent)
        self.robot = robot
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.memory = QLabel()
        self.debug = QLabel()
        layout.addWidget(self.memory)
        layout.addWidget(self.debug)
        
    def redraw_game(self):
        pass
    
    def tick(self):
        m, p = self.robot.memory.get_memory()
        m_st = ""
        for elem, i in zip(m, range(len(m))):
            if i==p:
                m_st += "<b>%d</b>"%elem
            else:
                m_st += "%d"%elem
                
            
        self.memory.setText(m_st)
        
        self.debug.setText(self.robot.coord.__unicode__()+" "+\
                           self.robot.direction.__unicode__())


           
           
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
       
        #fixme!
        while True:
            child = self.vblayout.takeAt(0)
            if child is not None:
                w = child.widget()
                if w is not None:
                    w.hide()
                del w
                del child
            else:
                break
        
        
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
           ( ">", (u"Next register", "greaterthan", None)),
           ( "<", (u"Previous register", "lessthan", None)),
           ( "+", (u"Increase", "plus", None)),
           ( "-", (u"Decrease", "minus", None)),
           ( "[", (u"Begin cycle", "leftbracket", None)),
           ( "]", (u"End cycle", "rightbracket", None)),
           ( ".", (u"Output current register", "dot", None)),
           ( ",", (u"Input to current register", "comma", None)),
           ( "/", (u"Rotate robot clockwise", "clockwise", None)),
           ( "\\", (u"Rotate robot anticlockwise", "anticlockwise", None)),
        ))

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
        for operator, (optitle, opiconname, func) in self.__operators.items():
            oa = QAction(QIcon(":/"+opiconname+".svg"),optitle, self)
               
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
            self.create_game(brainspell.Map(d.size_x.value(), d.size_y.value()), d.players.value(), "middle")
            
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
        self.game = brainspell.Game(gamemap, gametype)
        for i in range(players_num):
            pl = brainspell.Player(u"Player #%d"%i, self.game)
            pl.qcolor = PLAYER_COLORS[i]
        self.game.current_player = self.game.players[0]
        self.game.current_coord = brainspell.Coords(0,0)
        self.game.current_dir = brainspell.Direction('e')
        
        for i, player in enumerate(self.game.players):
            player.operator_svgs = {}
            player.robot_svg = QSvgRenderer(":/robot.svg")# PLAYER_COLORS[i])

            for operator, (optitle, opiconname, func) in self.__operators.items():
                #FIXME!!!
                qi = QSvgRenderer(":/"+opiconname+".svg")# PLAYER_COLORS[i])
                player.operator_svgs[operator] = qi
       
    def place_operator(self, operator):
        self.game.current_player.place_operator(operator, self.game.current_coord)
        self.playground.update_piece(self.game.current_coord)
        #self.move_current_coord(self.game.current_dir)
    
    def move_current_coord(self, direction):
        oldcoord = brainspell.Coords(self.game.current_coord.x , self.game.current_coord.y)
        self.game.current_coord.move(direction)
        self.playground.scene.current_coord_change(oldcoord, self.game.current_coord)
        
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
    
   
if __name__=="__main__":
    app = QApplication(sys.argv)
    w = MainForm()
    w.show()

    sys.exit(app.exec_())