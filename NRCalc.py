#GUI Reqs
from PyQt5 import QtGui, QtWidgets, QtCore, QtWebEngineWidgets
from PyQt5.QtWidgets import QMessageBox, QListWidgetItem, QTreeWidgetItem
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineSettings
#NR Data and functions
from Nightreign import Reference
from Nightreign import Enemy
from Nightreign import Utils
from Nightreign import Names
from Nightreign import Weapons
#Other
from pathlib import Path
from functools import partial
import pyperclip

class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.Functions = Utils.NightreignFunctions()
        self.setupUi(self)
        self.createMenus()
        # random shit for the wiki page
        profile = self.webEngineView.page().profile()
        profile.setHttpCacheType(profile.MemoryHttpCache)
        profile.setPersistentCookiesPolicy(profile.NoPersistentCookies)
        settings = self.webEngineView.settings()
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, False)
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, False)
        settings.setAttribute(QWebEngineSettings.FullScreenSupportEnabled, False)

    def createMenus(self):
        menubar = self.menuBar()
        fileMenu = menubar.addMenu("File")
        infomenu = menubar.addMenu("Info")

        infomenu.addAction("Entity IDs", lambda: self.showMessageBox("Entity IDs",
            "All enemies have NpcParamIds, which dictate a whole lot of things like stats and itemlots.<br>"
            f"This application already has all bosses and minibosses mapped, which is why they appear in the dropdown.<br><br>"
            f"If you want to get data on a basic enemy that is not listed, follow these steps:<br>"
            "1. Download <a href='https://github.com/vawser/Smithbox/releases'>Smithbox</a> and <a href='https://github.com/Nordgaren/UXM-Selective-Unpack/releases'>UXM</a><br>"
            "2. Unpack the game files with UXM by inputting your game install path<br>"
            "3. Open Smithbox and create a new project<br>"
            "4. Open the Map Editor tab, load the map you want by right clicking<br>"
            "5. Locate the enemy within the map, you can move around with WASD while holding right click on the viewport<br>"
            "6. Click on the enemy, navigate to the \"Properties\" tab on the right and copy the NpcParamId<br>"
            "7. Paste the ID into the field within this application and press enter<br>"))
        infomenu.addAction("Additional FP Cost", lambda: self.showMessageBox("Additional FP Cost",
            "An extra value for FP/Stamina consumption that can be used for follow-ups, continuous spells like Comet Azur, etc.<br>"))
        infomenu.addSeparator()
        infomenu.addAction("Credits", lambda: self.showMessageBox("Credits",
            "<a href='https://linktr.ee/aerolitesr'>Aero</a> - Me! :D<br><br>"))

        def createAction(name, func):
            action = QtWidgets.QAction(name, self)
            action.triggered.connect(func)
            return action
        
    def showMessageBox(self, title, message):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setTextFormat(QtCore.Qt.RichText)
        msg.setText(message)
        msg.exec_()

    def showError(self, text):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Error") 
        msg.setText(text) 
        msg.exec_() 
   
    def initDropdown(self):
        for index, i in enumerate(self.enemiesList):
            self.EnemyComboBox.addItem("") # add enough blank entries for all enemies
            self.EnemyComboBox.setItemText(index, QtCore.QCoreApplication.translate("Form", f"{i}")) # add all enemies to the combobox
        self.EnemyComboBox.setCurrentIndex(-1)

    def createUnselectableItem(self, text, itemType):
        item = itemType(text)
        item.setFlags(item.flags() & ~QtCore.Qt.ItemIsSelectable)
        return item

    def parseEnemy(self):
        enemy = self.enemyIdLineEdit.text()
        if not enemy or enemy == '': # if override field is empty
            try:
                enemy = self.EnemyComboBox.currentData() # fetch from dropdown
            except:
                return False
            
        try:
            if not isinstance(enemy, int):
                enemy = int(enemy)
        except:
            self.showError("Please select a valid enemy")
            self.enemyIdLineEdit.clear()
            return False
        
        return enemy

    def parseStats(self, enemy, mode, time, players, mutated):
        result = self.Functions.getStats(enemy=enemy, players=players, depth=mode, time=time, mutation=mutated)
        name = Names.Character.get(Enemy.NameIDs.get(enemy, None), Enemy.Stats[enemy]['Type'])
        self.StatsListWidget.addItem(self.createUnselectableItem(text=name+'\n', itemType=QListWidgetItem))

        for key, val in result.items():
            item = self.createUnselectableItem(text=f'{key} - {val}', itemType=QListWidgetItem)
            self.StatsListWidget.addItem(item)

    def parseDrops(self, enemy, mutated):
        data = self.Functions.getDrops(enemy=enemy, mutated=mutated)
        if not data:
            return
        
        self.populateDropsRoot(data)

    def populateDropsRoot(self, drops_dict):
        """Populate QTreeWidget with all drop slots from getDrops()."""

        for slot_name, items in drops_dict.items():
            slot_item = QtWidgets.QTreeWidgetItem([slot_name])
            slot_item.setFlags(slot_item.flags() & ~QtCore.Qt.ItemIsSelectable)
            slot_item.setForeground(0, QBrush(QColor("#ff9100")))
            self.DropsTreeWidget.addTopLevelItem(slot_item)

            blank_item = QtWidgets.QTreeWidgetItem([])
            blank_item.setFlags(blank_item.flags() & ~QtCore.Qt.ItemIsSelectable)
            self.DropsTreeWidget.addTopLevelItem(blank_item)

            self.populateDropsTree(items, slot_item)
            self.DropsTreeWidget.expandItem(slot_item)

    def populateDropsTree(self, data, parent=None):
        """Recursively populate QTreeWidget with nested item table data."""

        if isinstance(data, dict):
            for key, sublist in data.items():
                subheader = QtWidgets.QTreeWidgetItem([f"Lot {key}"])
                subheader.setFlags(subheader.flags() & ~QtCore.Qt.ItemIsSelectable)
                subheader.setForeground(0, QBrush(QColor("#00aaff")))
                if parent is None:
                    self.DropsTreeWidget.addTopLevelItem(subheader)
                else:
                    parent.addChild(subheader)
                self.populateDropsTree(sublist, subheader)
            return

        if not isinstance(data, (list, tuple)):
            return
        
        for item in data:
            name = item.get("Name", "Unknown")
            count = str(item.get("Count", ""))
            chance = float(item.get('Weight', 0.0))
            char = Reference.PlayerClass[item.get("Class", 0)]
            discovery = item.get("Discovery", '')

            try:
                color = Reference.RarityColor.get(item.get('Rarity'), "#000000")
            except KeyError:
                pass

            if chance > 0: # or chance == 0 # for debug
                temp_chance = f"{chance * 100:.2f}%"
                if temp_chance == "0.00%":
                    chance = f"{chance * 100:.3f}%"
                else:
                    chance = temp_chance # quick check for if chance is less than 0.01, in which case give an extra point of precision

                tree_item = QtWidgets.QTreeWidgetItem([name, chance, count, char, discovery])
                tree_item.setForeground(0, QBrush(QColor(color)))

                if name.startswith("Table "):
                    tree_item.setFlags(tree_item.flags() & ~QtCore.Qt.ItemIsSelectable)

                if parent is None: # for the "__ slot #_" entries
                    tree_item.setFlags(tree_item.flags() & ~QtCore.Qt.ItemIsSelectable)
                    self.DropsTreeWidget.addTopLevelItem(tree_item)

                    blank_item = QtWidgets.QTreeWidgetItem([])
                    blank_item.setFlags(blank_item.flags() & ~QtCore.Qt.ItemIsSelectable)
                    self.DropsTreeWidget.addTopLevelItem(blank_item)

                else:
                    tree_item.setData(0, QtCore.Qt.UserRole, item.get("Category"))
                    tree_item.setData(0, QtCore.Qt.UserRole+1, item.get("ItemID"))
                    parent.addChild(tree_item)

                children = item.get("Children", [])
                if children:
                    self.populateDropsTree(children, tree_item)

    def expandCollapseTree(self):
        if self.DataTabs.currentIndex() == 1:
            subject = self.DropsTreeWidget
        elif self.DataTabs.currentIndex() == 2:
            subject = self.ItemTreeView
        else:
            self.showError("Current tab has no trees to expand/collapse")
            return

        count = subject.topLevelItemCount()

        if count > 0:
            if any([subject.topLevelItem(i).isExpanded() for i in range(count)]):
                subject.collapseAll()
            else:
                subject.expandAll()

    def clear(self):
        self.DropsTreeWidget.clear()
        self.ItemTreeView.clear()
        self.StatsListWidget.clear()
    
    def parseItemInfo(self, category, itemid):
        if category == 2: # weapons
            self.setupItemTree() # clear and reset
            name = Names.Weapon[itemid]
            data = self.Functions.getWeaponInfo(itemid)

        elif category == 6: # custom weapons
            self.setupItemTree() # clear and reset
            WeaponData = Weapons.CustomWeapons[itemid]
            weaponId = WeaponData['Weapon']
            name = Names.Weapon[weaponId]
            table = WeaponData['Ash Table']
            AtchEffTables = WeaponData['Attach Effect Tables']
            MagicTables = WeaponData['Magic Tables']
            data = self.Functions.getWeaponInfo(weaponId, ash_table_override=table, effectTables=AtchEffTables, magicTables=MagicTables)

        elif category in ['Ash of War', 'Attach Effect', 'Magic']: # custom types
            data = self.Functions.getSkillInfo(category=category, itemId=itemid)
            self.writeExtraStats(data)
            return

        else:
            self.showError(f"Cannot load item of type: {Reference.ItemCategories[category]}\n\nTry \"Open Wiki\"")
            return

        self.ItemTreeView.addTopLevelItem(QtWidgets.QTreeWidgetItem([f"{name}"]))
        ashes = data.pop('Possible Ashes of War')
        effects = data.pop('Possible Effects')
        spells = data.pop('Possible Spells')

        self.populateItemStats(data)
        self.ItemTreeView.addTopLevelItem(self.createUnselectableItem(text=[], itemType=QTreeWidgetItem))

        self.populateItemChances(ashes, self.addItemSection("Possible Ashes of War"))
        self.populateItemChances(effects, self.addItemSection("Possible Effects"))
        self.populateItemChances(spells, self.addItemSection("Possible Spells"))

        self.ItemTreeView.resizeColumnToContents(0)
        self.ItemTreeView.resizeColumnToContents(1)

        # only swap tabs if successful
        self.DataTabs.setCurrentIndex(2)

    def loadItem(self):
        if self.DataTabs.currentIndex() == 1:
            selection = self.DropsTreeWidget.currentItem()
        elif self.DataTabs.currentIndex() == 2:
            selection = self.ItemTreeView.currentItem()
        else:
            self.showError("Current tab has no viewable items")
            return

        try:
            category = selection.data(0, QtCore.Qt.UserRole)
            itemid = selection.data(0, QtCore.Qt.UserRole + 1)
            print(category, itemid)

            if itemid and category:
                self.parseItemInfo(category, itemid)
                return
            raise AttributeError

        except AttributeError:
            self.showError("This item has no stored data")
            return

    def setupItemTree(self):
        self.ItemTreeView.clear()
        self.ItemTreeView.setColumnCount(1)
        self.ItemTreeView.setHeaderLabels(["Item", "Chance"])

    def addItemSection(self, title, color="#971a44"):
        header = QtWidgets.QTreeWidgetItem([title, ''])
        header.setFlags(header.flags() & ~QtCore.Qt.ItemIsSelectable)
        header.setForeground(0, QBrush(QColor(color)))
        self.ItemTreeView.addTopLevelItem(header)
        return header
    
    def populateItemChances(self, data, parent):
        if isinstance(data, dict):
            if 'ID' in data and 'Weight' in data:
                leaf = QtWidgets.QTreeWidgetItem([str(data['Name']), str(data['Weight'])])
                leaf.setData(0, QtCore.Qt.UserRole, data['Category'])
                leaf.setData(0, QtCore.Qt.UserRole+1, data['ID'])
                parent.addChild(leaf)
            else:
                for key, value in data.items():
                    subheader = QtWidgets.QTreeWidgetItem([str(key), ''])
                    subheader.setFlags(subheader.flags() & ~QtCore.Qt.ItemIsSelectable)
                    subheader.setForeground(0, QBrush(QColor("#971a44")))
                    parent.addChild(subheader)
                    self.populateItemChances(value, subheader)

        elif isinstance(data, (list, tuple)):
            for item in data:
                self.populateItemChances(item, parent)

    def populateItemStats(self, stats_dict):
        self.statRows = []

        for key, value in stats_dict.items():
            item = QtWidgets.QTreeWidgetItem([f"{key}: {value}", ''])
            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsSelectable)

            self.ItemTreeView.addTopLevelItem(item)
            self.statRows.append(item)

    def writeExtraStats(self, data):
        items = list(data.items())
        row_count = self.ItemTreeView.topLevelItemCount()

        for row in range(row_count-1):
            item = self.ItemTreeView.topLevelItem(row+1)

            if row < len(items):
                key, val = items[row]
                item.setText(1, f"            {key}: {val}") # added tabs to make it more "right-aligned"
            else:
                item.setText(1, "")

    def openWiki(self):
        if self.DataTabs.currentIndex() == 1:
            selection = self.DropsTreeWidget.currentItem()
            if selection:
                selection = selection.text(0)
        elif self.DataTabs.currentIndex() == 2:
            selection = self.ItemTreeView.currentItem()
            if selection:
                selection = selection.text(0)
        else:
            self.showError("Current tab has no accepted items")
            return

        if selection:
            URL = QUrl(f"https://eldenringnightreign.wiki.fextralife.com/{selection.replace(" ", '+')}")
            self.DataTabs.setCurrentIndex(3)
            self.webEngineView.setUrl(URL)
        else:
            self.showError(f'Requested item: [{selection}] is not a valid URL')

    def update(self, mutated=None):
        self.clear()
        
        enemy = self.parseEnemy()
        if not enemy:
            return
        
        if mutated is None:
            mutated = bool(self.checkBox.isChecked())

        mode = self.GameModeComboBox.currentIndex()
        time = self.timeComboBox.currentIndex()+1
        players = self.comboBox.currentIndex()+1

        self.parseDrops(enemy, mutated) 
        self.parseStats(enemy, mode, time, players, mutated)
    
    def setupUi(self, Form):
        self.enemiesList = Enemy.Stats.keys()
        Form.setObjectName("Form")
        Form.setFixedSize(660, 590)
        Form.setWindowTitle("Nightreign Calculator")

        # day 1/2
        self.timeComboBox = QtWidgets.QComboBox(Form)
        self.timeComboBox.setGeometry(QtCore.QRect(70, 110, 111, 22))
        self.timeComboBox.setObjectName("timeComboBox")
        self.timeComboBox.activated[str].connect(self.update)
        self.timeComboBox.addItem("Day 1")
        self.timeComboBox.addItem("Day 2")

        # id entry
        self.enemyIdLineEdit = QtWidgets.QLineEdit(Form)
        self.enemyIdLineEdit.setGeometry(QtCore.QRect(70, 50, 211, 20))
        self.enemyIdLineEdit.setToolTip("")
        self.enemyIdLineEdit.setPlaceholderText("*Optional")
        self.enemyIdLineEdit.setObjectName("enemyIdLineEdit")
        self.enemyIdLineEdit.returnPressed.connect(self.update)

        # enemy list (I actually used this)
        self.EnemyComboBox = QtWidgets.QComboBox(Form)
        self.EnemyComboBox.setGeometry(QtCore.QRect(70, 23, 481, 22))
        self.EnemyComboBox.setToolTip("List of common bosses and minibosses")
        self.EnemyComboBox.setEditable(True)
        self.EnemyComboBox.setObjectName("EnemyComboBox")
        self.EnemyComboBox.activated[str].connect(self.update)
        # setup list of named enemies
        for name, id in Enemy.PremadeEnemyList.items():
            self.EnemyComboBox.addItem(name, id)

        # labels
        self.EnemyLabel = QtWidgets.QLabel("Enemy:", Form)
        self.EnemyLabel.setGeometry(QtCore.QRect(20, 23, 41, 21))
        self.EnemyLabel.setToolTip("List of common bosses and minibosses")
        self.EnemyLabel.setObjectName("EnemyLabel")

        self.EntityIDLabel = QtWidgets.QLabel("Entity ID:", Form)
        self.EntityIDLabel.setGeometry(QtCore.QRect(20, 50, 51, 21))
        self.EntityIDLabel.setToolTip("Optional override for enemies not listed above")
        self.EntityIDLabel.setObjectName("EntityIDLabel")

        self.NGLabel = QtWidgets.QLabel("Mode:", Form)
        self.NGLabel.setGeometry(QtCore.QRect(20, 80, 51, 21))
        self.NGLabel.setToolTip("NG+ Scaling for calculations")
        self.NGLabel.setObjectName("NGLabel")

        self.TimeLabel = QtWidgets.QLabel("Time:", Form)
        self.TimeLabel.setGeometry(QtCore.QRect(20, 110, 51, 21))
        self.TimeLabel.setToolTip("Game Time")
        self.TimeLabel.setObjectName("TimeLabel")

        # random lines for ui
        self.line = QtWidgets.QFrame(Form)
        self.line.setGeometry(QtCore.QRect(176, 80, 16, 61))
        self.line.setFrameShadow(QtWidgets.QFrame.Plain)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setObjectName("line")

        self.line_2 = QtWidgets.QFrame(Form)
        self.line_2.setGeometry(QtCore.QRect(20, 130, 621, 21))
        self.line_2.setFrameShadow(QtWidgets.QFrame.Plain)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setObjectName("line_2")

        self.line_3 = QtWidgets.QFrame(Form)
        self.line_3.setGeometry(QtCore.QRect(280, 50, 20, 91))
        self.line_3.setFrameShadow(QtWidgets.QFrame.Plain)
        self.line_3.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_3.setObjectName("line_3")

        # game mode
        self.GameModeComboBox = QtWidgets.QComboBox(Form)
        self.GameModeComboBox.setGeometry(QtCore.QRect(70, 80, 111, 22))
        self.GameModeComboBox.setToolTip("Current Game Mode")
        self.GameModeComboBox.setObjectName("GameModeComboBox")
        self.GameModeComboBox.addItems(["Normal", "Depth 1", "Depth 2", "Depth 3", "Depth 4", "Depth 5"])
        self.GameModeComboBox.activated[str].connect(self.update)

        # tabs system
        self.DataTabs = QtWidgets.QTabWidget(Form)
        self.DataTabs.setGeometry(QtCore.QRect(20, 150, 621, 430))
        self.DataTabs.setToolTipDuration(-1)
        self.DataTabs.setObjectName("DataTabs")

        # stats tab
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        tab_layout = QtWidgets.QVBoxLayout(self.tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        self.StatsListWidget = QtWidgets.QListWidget(self.tab)
        self.StatsListWidget.setObjectName("StatsListWidget")
        tab_layout.addWidget(self.StatsListWidget)
        self.DataTabs.addTab(self.tab, "Stats")

        # drops tab
        self.tab_2 = QtWidgets.QWidget()
        drops_layout = QtWidgets.QVBoxLayout(self.tab_2)
        drops_layout.setContentsMargins(0, 0, 0, 0)
        self.DropsTreeWidget = QtWidgets.QTreeWidget()
        self.DropsTreeWidget.setHeaderLabels(["Item / Table", "Chance", "Count", "Class", "Item Discovery"])
        self.DropsTreeWidget.setColumnWidth(0, 250)
        self.DropsTreeWidget.setColumnWidth(1, 75)
        self.DropsTreeWidget.setColumnWidth(2, 50)
        self.DropsTreeWidget.setColumnWidth(3, 100)
        self.DropsTreeWidget.setColumnWidth(4, 50)
        drops_layout.addWidget(self.DropsTreeWidget)
        self.DataTabs.addTab(self.tab_2, "Drops")

        # item tab
        self.tab_3 = QtWidgets.QWidget()
        item_layout = QtWidgets.QVBoxLayout(self.tab_3)
        item_layout.setContentsMargins(0, 0, 0, 0)
        self.ItemTreeView = QtWidgets.QTreeWidget()
        self.ItemTreeView.setHeaderHidden(True)
        item_layout.addWidget(self.ItemTreeView)
        self.DataTabs.addTab(self.tab_3, "Item")

        # wiki tab
        self.tab_4 = QtWidgets.QWidget()
        self.tab_4.setObjectName("tab_4")
        self.webEngineView = QtWebEngineWidgets.QWebEngineView(self.tab_4)
        self.webEngineView.setGeometry(QtCore.QRect(0, 0, 621, 430))
        self.webEngineView.setUrl(QtCore.QUrl("about:blank"))
        self.webEngineView.setObjectName("webEngineView")
        self.DataTabs.addTab(self.tab_4, "Wiki")

        # buttons (too lazy to rename them)
        self.pushButton = QtWidgets.QPushButton("Expand/Collapse", Form)
        self.pushButton.setGeometry(QtCore.QRect(300, 100, 121, 31))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.expandCollapseTree)

        self.pushButton_2 = QtWidgets.QPushButton("Clear Data", Form)
        self.pushButton_2.setGeometry(QtCore.QRect(300, 60, 121, 31))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.clicked.connect(self.clear)

        self.pushButton_3 = QtWidgets.QPushButton("Load Selected Item", Form)
        self.pushButton_3.setGeometry(QtCore.QRect(430, 100, 121, 31))
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_3.clicked.connect(self.loadItem)

        self.pushButton_4 = QtWidgets.QPushButton("Open Wiki", Form)
        self.pushButton_4.setGeometry(QtCore.QRect(430, 60, 121, 31))
        self.pushButton_4.setObjectName("pushButton_4")
        self.pushButton_4.clicked.connect(self.openWiki)

        # meme image
        global basepath
        label = QtWidgets.QLabel(self)
        label.setGeometry(QtCore.QRect(555, 23, 85, 111))
        pixmap = QtGui.QPixmap(str(basepath / "lacie.png"))
        label.setPixmap(pixmap.scaled(label.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        label.setAlignment(QtCore.Qt.AlignCenter)

        # player count
        self.comboBox = QtWidgets.QComboBox(Form)
        self.comboBox.setGeometry(QtCore.QRect(190, 80, 91, 22))
        self.comboBox.setObjectName("comboBox")
        self.comboBox.activated[str].connect(self.update)
        self.comboBox.addItems(["Solo", "Duos", "Trios"])

        # mutation
        self.checkBox = QtWidgets.QCheckBox("Is Mutated", Form)
        self.checkBox.setGeometry(QtCore.QRect(200, 110, 81, 21))
        self.checkBox.setChecked(False)
        self.checkBox.toggled[bool].connect(lambda state: self.update(mutated=state))

        # initial states
        self.EnemyComboBox.setCurrentIndex(-1)
        self.DataTabs.setCurrentIndex(0)

        QtCore.QMetaObject.connectSlotsByName(Form)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    basepath = Path(sys.argv[0]).parent
    app.setWindowIcon(QtGui.QIcon(str(basepath / 'calc.ico')))
    ui = Window()
    ui.show()
    sys.exit(app.exec_())

# pyinstaller main.py --noconsole --icon=calc.ico --add-data "calc.ico;." --add-data "lacie.png;."