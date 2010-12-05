#!/usr/bin/env python
#-*- coding:cp1251 -*-

import sys
import PyQt4
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import brainspell


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

class PlaygroundPiece(QGraphicsItem):
    def __init__(self, game, coord, parent=None, scene=None):
        super(PlaygroundPiece, self).__init__(parent=parent, scene=scene)
        self.game, self.coord = game, coord
        self.active = False
        self.setAcceptedMouseButtons(Qt.LeftButton)
        
    def paint(self, painter, option, widget):
        size = self.scene().piece_size
        x = self.coord.x*size
        y = self.coord.y*size
        x2 = x+size
        y2 = y+size
        #painter.drawRoundedRect(x,y, x2,y2, 5, 5)
        try:
            painter.drawText(QPointF(x,y2), self.game.gamemap.get_bfoperator(self.coord).operator)
        except AttributeError:
            pass
        #painter.drawText(QPointF(x,y2), "8")
        
        
    def boundingRect(self):
        penWidth = 1.0
        size = self.scene().piece_size
        x = self.coord.x*size
        y = self.coord.y*size
        x2 = x+size
        y2 = y+size

        return QRectF( x, y,\
                       x2 + penWidth, y2 + penWidth)
    
        
class PlaygroundScene(QGraphicsScene):
    piece_size = 30.0
    def __init__(self, parent=None, game=None):
        super(PlaygroundScene, self).__init__(parent=parent)
        self.game = game
        self.pieces = []
        
        for i in range(self.game.gamemap.size_x+1):
            self.addLine(i*self.piece_size, 0, i*self.piece_size, self.piece_size*self.game.gamemap.size_y)
        for i in range(self.game.gamemap.size_y+1):
            self.addLine(0, i*self.piece_size, self.piece_size*self.game.gamemap.size_x, i*self.piece_size)
        
        for x in range(self.game.gamemap.size_x):
            for y in range(self.game.gamemap.size_y):
                piece = PlaygroundPiece(self.game, brainspell.Coords(x,y))
                self.pieces.append(piece)
                self.addItem(piece)
                
            
    def mousePressEvent(self, ev):
        print self.mouseGrabberItem()
        print self
        
class Playground(QGraphicsView):
    def __init__(self, parent=None, game=None):
        super(Playground, self).__init__(parent=parent)
        self.game = game
        self.redraw_game()
        
    def tick(self):
        pass
    
    def redraw_game(self):
        if self.game is not None:
            self.scene = PlaygroundScene(parent=self, game=self.game)
            self.setScene(self.scene) 
            self.show()
            
            
class PlayerWidget(QWidget):
    def __init__(self, player, parent=None):
        super(PlayerWidget, self).__init__(parent)
        self.player = player
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.name_label = QLabel()
        self.mana_bar = QProgressBar()
        layout.addWidget(self.name_label)
        layout.addWidget(self.mana_bar)
        
    def redraw_game(self):
        print "hi player"
        self.name_label.setText(self.player.name)
    
    def tick(self):
        self.mana_bar.setValue(self.player.mana)


class RobotWidget(QWidget):
    def __init__(self, player, parent=None):
        super(RobotWidget, self).__init__(parent)
        self.robot = robot
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.memory = QLabel()
        layout.addWidget(self.memory)
        
    def redraw_game(self):
        print "hi robo"
        pass
    
    def tick(self):
        self.memory.setText(self.robot.memory.get_memory())


class SideDock(QDockWidget):
    def __init__(self, name, parent=None, game=None):
        super(SideDock, self).__init__(name, parent)
        self.game = game
        self.layout = QVBoxLayout()
        self.players = []
        self.robots = {}
    
    def redraw_game(self):
        for player in self.game.players:
            player_w = PlayerWidget(player)
            self.players.append(player_w)
            self.robots[player.name] = []
            self.layout.addWidget(player_w)
            for robot in player.robots:
               robot_widget = RobotWidget(robot)
               self.robots[player.name].append(robot_widget)
               self.layout.addWidget(robot_widget)
        
        for player in self.players:
            player.redraw_game()
        for playername, robots in self.robots.items():
            for robot in robots:
                robot.redraw_game()
    
       
               
            
        
    def tick(self):
        for player in self.players:
            player.tick()
        for playername, robots in self.robots.items():
            for robot in robots:
                robot.tick()
    
    
class MainForm(QMainWindow):
    def __init__(self):
        super(MainForm, self).__init__()
        self.resize(800,600)
        self.setWindowTitle('QBrainSpell')
        
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
        self.playground = Playground()
        self.sidebar = SideDock(u"Information", self)
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
    
    def new_game(self):
        d = NewGameDialog(self)
        d.exec_()
        if d.result()==QDialog.Accepted:
            self.create_game(d.size_x.value(), d.size_y.value(), d.players.value(), "middle")
            
            self.redraw_game()
            
    def create_game(self, x, y, players_num, gametype):
        gamemap = brainspell.Map(x,y)
        self.game = brainspell.Game(gamemap, gametype)
        for i in range(players_num):
            pl = brainspell.Player(u"Player #%d"%i, self.game)
        
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
            self.game = brainspell.Game(gamemap, "middle")
            pl = brainspell.Player(u"Player #1", self.game)
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
        else:
            self.play_pause_action.setText(u"Play")
    
        
if __name__=="__main__":
    app = QApplication(sys.argv)
    w = MainForm()
    w.show()

    sys.exit(app.exec_())