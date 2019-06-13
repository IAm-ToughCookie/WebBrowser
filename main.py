import sys
import os
import json

from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                             QLineEdit, QTabWidget, QTabBar, QFrame, QStackedLayout, QComboBox)
from PyQt5.QtGui import QIcon, QWindow, QImage
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *


# noinspection PyUnusedLocal
class AddressBar(QLineEdit):
    def __init__(self):
        super().__init__()
        self.setText("Enter URL or search query")

    def mouse_press_event(self, e):
        self.selectAll()


# noinspection PyArgumentList,PyAttributeOutsideInit,PyCallByClass,PyUnresolvedReferences,PyUnresolvedReferences
class App(QFrame):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AS-Browser")
        self.create_app()
        self.resize(1366, 768)

    # noinspection PyAttributeOutsideInit
    def create_app(self):
        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Create Tabs
        self.tabbar = QTabBar(movable=True, tabsClosable=True)
        self.tabbar.tabCloseRequested.connect(self.close_tab)
        self.tabbar.tabBarClicked.connect(self.switch_tab)
        self.tabbar.setDrawBase(False)

        self.tabbar.setCurrentIndex(0)

        # Keep track of tabs
        self.tab_count = 0
        self.tabs = []

        # Create Address Bar
        self.toolbar = QWidget()
        self.toolbar_layout = QHBoxLayout()
        self.addressbar = AddressBar()
        self.add_tab_button = QPushButton("+")

        # Connect AdressBar + button Signals
        self.addressbar.returnPressed.connect(self.browse_to)
        self.add_tab_button.clicked.connect(self.add_tab)

        # Set toolbar buttons
        self.back_button = QPushButton("<")
        self.back_button.clicked.connect(self.go_back)

        self.forward_button = QPushButton(">")
        self.forward_button.clicked.connect(self.go_forward)

        self.reload_button = QPushButton("R")
        self.reload_button.clicked.connect(self.reload_page)

        # Build toolbar
        self.toolbar.setLayout(self.toolbar_layout)
        self.toolbar_layout.addWidget(self.back_button)
        self.toolbar_layout.addWidget(self.reload_button)
        self.toolbar_layout.addWidget(self.forward_button)
        self.toolbar_layout.addWidget(self.addressbar)
        self.toolbar_layout.addWidget(self.add_tab_button)

        # Set main view
        self.container = QWidget()
        self.container.layout = QStackedLayout()
        self.container.setLayout(self.container.layout)

        self.layout.addWidget(self.tabbar)
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.container)

        self.setLayout(self.layout)

        self.add_tab()

        self.show()

    def close_tab(self, i):
        self.tabbar.removeTab(i)

    # noinspection PyCallByClass
    def add_tab(self):
        i = self.tab_count

        self.tabs.append(QWidget())
        self.tabs[i].layout = QVBoxLayout()
        self.tabs[i].setObjectName("tab" + str(i))
        self.tabs[i].layout.setContentsMargins(0, 0, 0, 0)

        # Open webView
        self.tabs[i].content = QWebEngineView()
        self.tabs[i].content.load(QUrl.fromUserInput("http://google.com"))

        self.tabs[i].content.titleChanged.connect(lambda: self.set_tab_content(i, "title"))
        self.tabs[i].content.iconChanged.connect(lambda: self.set_tab_content(i, "icon"))

        # Add webView to tabs layout
        self.tabs[i].layout.addWidget(self.tabs[i].content)

        # Set top level tab from [] to layout
        self.tabs[i].setLayout(self.tabs[i].layout)

        # Add tab to top level stackedWidget
        self.container.layout.addWidget(self.tabs[i])
        self.container.layout.setCurrentWidget(self.tabs[i])

        # Create tab on tabbar, representing this tab,
        # set tabData to tab# so it knows what self.tabs# it needs to control
        self.tabbar.addTab("New Tab")
        self.tabbar.setTabData(i, {"object": "tab" + str(i), "initial": i})

        '''
            self.tabs[i].objectName = tab1
            self.tabbar.tabData(i)["object"] = tab1
        '''

        self.tabbar.setCurrentIndex(i)

        # +=1
        self.tab_count += 1

    def switch_tab(self, i):
        tab_data = self.tabbar.tabData(i)["object"]
        tab_content = self.findChild(QWidget, tab_data)
        self.container.layout.setCurrentWidget(tab_content)

    def browse_to(self):
        text = self.addressbar.text()

        i = self.tabbar.currentIndex()
        tab = self.tabbar.tabData(i)["object"]
        wv = self.findChild(QWidget, tab).content

        if "http" not in text:
            if "." not in text:
                url = "https://www.google.com/#q=" + text
            else:
                url = "https://" + text
        else:
            url = text

        wv.load(QUrl.fromUserInput(url))

    def set_tab_content(self, i, type):
        tab_name = self.tabs[i].objectName()

        count = 0
        running = True

        while running:
            tab_data_name = self.tabbar.tabData(count)

            if count >= 99:
                running = False

            if tab_name == tab_data_name["object"]:
                if type == "title":
                    new_title = self.findChild(QWidget, tab_name).content.title()
                    self.tabbar.setTabText(count, new_title)
                    running = False
                elif type == "icon":
                    new_icon = self.findChild(QWidget, tab_name).content.icon()
                    self.tabbar.setTabIcon(count, new_icon)
                    running = False
            else:
                print(count)
                count += 1

    def go_back(self):
        active_index = self.tabbar.currentIndex()
        tab_name = self.tabbar.tabData(active_index)["object"]
        tab_content = self.findChild(QWidget, tab_name).content

        tab_content.back()

    def go_forward(self):
        active_index = self.tabbar.currentIndex()
        tab_name = self.tabbar.tabData(active_index)["object"]
        tab_content = self.findChild(QWidget, tab_name).content

        tab_content.forward()

    def reload_page(self):
        active_index = self.tabbar.currentIndex()
        tab_name = self.tabbar.tabData(active_index)["object"]
        tab_content = self.findChild(QWidget, tab_name).content

        tab_content.reload()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()

    sys.exit(app.exec())
