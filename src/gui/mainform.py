#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
import functools

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtSvg import *

import brainspell
import images_rc
from utils import odict
from widgets import *
from playground import *



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


class MainForm(QMainWindow):
       
    def __init__(self):
        self.__casts = odict({
            "run": (u"Run robots", None),
            "stop": (u"Stop robots", None),
            "create_robot": (u"Create robot", self.create_robot),
        })
        
        self.__operators = odict.from_tuple((
           ( ">", (u"Next register", "greaterthan", None, (Qt.Key_Greater, Qt.Key_Period) )),
           ( "<", (u"Previous register", "lessthan", None, (Qt.Key_Less, Qt.Key_Comma) )),
           ( "+", (u"Increase", "plus", None, (Qt.Key_Plus,Qt.Key_Equal) )),
           ( "-", (u"Decrease", "minus", None, (Qt.Key_Minus,Qt.Key_Underscore) )),
           ( "[", (u"Begin cycle", "leftbracket", None, (Qt.Key_BracketLeft,) )),
           ( "]", (u"End cycle", "rightbracket", None, (Qt.Key_BracketRight,) )),
           ( ".", (u"Output current register", "dot", None, (Qt.Key_O,) )),
           ( ",", (u"Input to current register", "comma", None, (Qt.Key_I,) )),
           ( "(", (u"Rotate robot clockwise", "clockwise", None, (Qt.Key_9, Qt.Key_ParenLeft) )),
           ( ")", (u"Rotate robot anticlockwise", "anticlockwise", None, (Qt.Key_0, Qt.Key_ParenLeft) )),
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
        view_menu = menubar.addMenu(u"&View")
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
        
        self.demon_name = DemonNameDock(self)
        self.demon_name.setAllowedAreas(Qt.TopDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, self.demon_name)
        demon_name_action = self.demon_name.toggleViewAction()
        
        self.playground = Playground(operator_actions = self.operator_actions)
        self.sidebar = SideDock(self.cast_actions, self.operator_actions, self)
        self.sidebar.setAllowedAreas(Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, self.sidebar)
        sidebar_action = self.sidebar.toggleViewAction()
        
        self.alphabet = AlphabetDock(self)
        self.alphabet.setAllowedAreas(Qt.TopDockWidgetArea)
        self.addDockWidget(Qt.TopDockWidgetArea, self.alphabet)
        alphabet_action = self.alphabet.toggleViewAction()
        
        view_menu.addAction(sidebar_action)
        view_menu.addAction(demon_name_action)
        view_menu.addAction(alphabet_action)
        
        layout.addWidget(self.playground)
        
        toolbar = self.addToolBar("main")
        toolbar.addAction(new_game_action)
        toolbar.addAction(play_pause_action)
        toolbar.addAction(step_action)
               
        self.demo()

        settings = QSettings()
        self.restoreGeometry(settings.value("geometry").toByteArray());
        self.restoreState(settings.value("windowState").toByteArray());
    
    def new_game(self):
        d = NewGameDialog(self)
        d.exec_()
        if d.result()==QDialog.Accepted:
            self.create_game(brainspell.Map(d.size_x.value(), d.size_y.value(), d.letter_prob.value()), d.players.value(), "middle")
            
            self.redraw_game()
            
    def demo(self):
        demo_map = [\
r"+++(",\
r"   +",\
r"   +",\
r".++(",\
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
        if operator=="(":
            newdir.turn_right()
            self.move_current_coord(newdir)
        elif operator==")":
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
        
        
    def delete_current_operator(self):
        self.game.current_player.place_operator(None, self.game.current_coord)
        self.playground.update_piece(self.game.current_coord)
        
    def keyPressEvent(self, e):
        for act in self.operator_actions.values():
            if e.key() in act.key:
                act.trigger()
        
        if e.key() in (Qt.Key_Backspace, Qt.Key_Delete):
            self.delete_current_operator()
 
    def closeEvent(self, event):
        settings = QSettings()
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())

        super(MainForm,self).closeEvent(event)

   

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("qBrainSpell")
    app.setOrganizationName("SergeyKlimov")
    app.setOrganizationDomain("darvin.github.com")
    w = MainForm()
    w.show()

    sys.exit(app.exec_())
                
if __name__=="__main__":
    main()
   
