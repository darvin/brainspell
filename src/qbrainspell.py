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
    def set_name(self, name):
        self.setText(u"Current demon: "+name)

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
        painter.drawText(QPointF(x,y2), "8")
        
        
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
        
    def redraw_game(self):
        if self.game is not None:
            self.scene = PlaygroundScene(parent=self, game=self.game)
            self.setScene(self.scene) 
            self.show()
            
            
        
class MainForm(QMainWindow):
    def __init__(self):
        super(MainForm, self).__init__()
        self.resize(800,600)
        self.setWindowTitle('QBrainSpell')
        
        new_game_action = QAction(u"New game", self)
        new_game_action.triggered.connect(self.new_game)
        exit_action = QAction(u"Exit", self)
        exit_action.triggered.connect(self.close)
        menubar = self.menuBar()
        file_menu = menubar.addMenu(u"&Game")
        file_menu.addAction(new_game_action)
        file_menu.addAction(exit_action)
        
        layout = QVBoxLayout()
        widg = QWidget()
        widg.setLayout(layout)
        self.setCentralWidget(widg)
        self.demon_name = DemonName()
        self.playground = Playground()
        layout.addWidget(self.demon_name)
        layout.addWidget(self.playground)
    
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
        self.demon_name.set_name(self.game.demon_name)
        self.playground.game = self.game
        self.playground.redraw_game()
        

if __name__=="__main__":
    app = QApplication(sys.argv)
    w = MainForm()
    w.show()

    sys.exit(app.exec_())