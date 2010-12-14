from PyQt4.QtCore import *
from PyQt4.QtSvg import *
from PyQt4.QtGui import *

from brainspell import numerology
from settings import PLAYER_COLORS


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




class NumerologyLabel(QWidget):
    def __init__(self, text="", parent=None, game=None):
        super(NumerologyLabel, self).__init__(parent=parent)
        
        self.hlayout = QHBoxLayout()
        self.setLayout(self.hlayout)
        self.__last_text = None
        self.setText(text)
        
    def setText(self, text):
        if self.__last_text!=text:
            layout_clear(self.hlayout) 
            for c in text:
                letter = QLabel(c)
                number = QLabel("%d"%numerology.alpha_to_int(c))
                layout = QVBoxLayout()
                layout.addWidget(letter)
                layout.addWidget(number)
                self.layout().addLayout(layout)
            
        self.__last_text = text
            
        
    def highlight_letter(self, index):
        c = self.layout().itemAt(index)
        if c is not None:
            l = c.layout()
            w = l.itemAt(0).widget()
            w.setStyleSheet("color: green")




class DemonNameDock(QDockWidget):
    def __init__(self, parent, game=None):
        super(DemonNameDock, self).__init__(u"Demon name", parent=parent)
        self.setObjectName("demon_name_dock")
        self.game=game
        self.demon_name = NumerologyLabel()
        self.setWidget(self.demon_name)

    def set_name(self, name):
        self.demon_name.setText(name)

    def tick(self):
        for index in self.game.current_player.get_correct_indexes():
            self.demon_name.highlight_letter(index)

    def redraw_game(self):
        self.set_name(self.game.demon_name)


class AlphabetDock(QDockWidget):
    def __init__(self, parent, game=None):
        super(AlphabetDock, self).__init__(u"Alphabet", parent=parent)
        self.setObjectName("alphabet_dock")
        self.game=game
        alphabet = NumerologyLabel([numerology.int_to_alpha(i) for i in range(numerology.MIN_NUMBER, numerology.MAX_NUMBER)])
        self.setWidget(alphabet)


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
    def __init__(self, cast_actions, operator_actions, parent=None, game=None):
        super(SideDock, self).__init__(u"Information", parent)
        self.setObjectName('side_dock')
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


