import sys
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QFormLayout, QGridLayout, QLabel, QLineEdit, QScrollArea, QCheckBox, QPushButton, QListWidget, QPlainTextEdit
from pymongo import MongoClient

# fields and labels to filter
fields = ['data.info.channel_cn', 'data.info.area']
labels = ['类型', '地区']
# configurations
n_records_per_page = 20
n_checkboxes_per_line = 10


class YyetsWidget(QWidget):
    def __init__(self, collections):
        super().__init__()
        self.collections = collections

        # init current and total page number
        self.page = 0
        self.page_num = 0

        # create and set main layout
        layout = QGridLayout()
        self.setLayout(layout)
        # set window size and title
        self.setMinimumSize(QtCore.QSize(2500, 1500))
        self.setWindowTitle('YYeTs搜索器')

        self.filters = {}
        # create each filter
        for i, (field, label) in enumerate(zip(fields, labels)):
            # create filter label
            filter_label = QLabel(label)
            filter_label.setAlignment(QtCore.Qt.AlignCenter)
            layout.addWidget(filter_label, i * 2, 0, 1, 6)

            # create checkboxes
            checkboxes = []
            filter_layout = QGridLayout()
            filter_values = ['全部'] + self.collections.find().distinct(field)
            for j, value in enumerate(filter_values):
                checkbox = QCheckBox(value)
                checkboxes.append(checkbox)
                filter_layout.addWidget(checkbox, j // n_checkboxes_per_line, j % n_checkboxes_per_line)
                if j == 0:
                    checkbox.setChecked(True)
            self.filters[field] = checkboxes

            # create filter widget
            filter_widget = QWidget()
            filter_widget.setLayout(filter_layout)
            scroll_area = QScrollArea()
            scroll_area.setWidget(filter_widget)
            scroll_area.setWidgetResizable(True)
            layout.addWidget(scroll_area, i * 2 + 1, 0, 1, 6)
            layout.setRowStretch(i * 2 + 1, 1)
        i = i * 2 + 3

        # create keyword label, edit and search button
        keyword_label = QLabel('关键词：')
        keyword_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(keyword_label, i, 0)
        self.keyword_edit = QLineEdit()
        self.keyword_edit.returnPressed.connect(self.search_button_clicked)
        layout.addWidget(self.keyword_edit, i, 1, 1, 4)
        search_button = QPushButton('搜索')
        search_button.clicked.connect(self.search_button_clicked)
        layout.addWidget(search_button, i, 5)
        i += 1

        # create labels of all levels
        record_label = QLabel('剧名')
        season_label = QLabel('季')
        format_label = QLabel('格式')
        episode_label = QLabel('集')
        way_label = QLabel('来源')
        address_label = QLabel('下载地址')
        record_label.setAlignment(QtCore.Qt.AlignCenter)
        season_label.setAlignment(QtCore.Qt.AlignCenter)
        format_label.setAlignment(QtCore.Qt.AlignCenter)
        episode_label.setAlignment(QtCore.Qt.AlignCenter)
        way_label.setAlignment(QtCore.Qt.AlignCenter)
        address_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(record_label, i, 0)
        layout.addWidget(season_label, i, 1)
        layout.addWidget(format_label, i, 2)
        layout.addWidget(episode_label, i, 3)
        layout.addWidget(way_label, i, 4)
        layout.addWidget(address_label, i, 5)
        i += 1

        # create lists of all levels
        self.record_list = QListWidget()
        self.season_list = QListWidget()
        self.format_list = QListWidget()
        self.episode_list = QListWidget()
        self.way_list = QListWidget()
        self.record_list.currentRowChanged.connect(self.record_list_current_row_changed)
        self.season_list.currentRowChanged.connect(self.season_list_current_row_changed)
        self.format_list.currentRowChanged.connect(self.format_list_current_row_changed)
        self.episode_list.currentRowChanged.connect(self.episode_list_current_row_changed)
        self.way_list.currentRowChanged.connect(self.way_list_current_row_changed)
        layout.addWidget(self.record_list, i, 0, 2, 1)
        layout.addWidget(self.season_list, i, 1)
        layout.addWidget(self.format_list, i, 2)
        layout.addWidget(self.episode_list, i, 3)
        layout.addWidget(self.way_list, i, 4)
        # create download address edit
        self.address_edit = QPlainTextEdit()
        self.address_edit.setReadOnly(True)
        self.address_edit.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        layout.addWidget(self.address_edit, i, 5, 2, 1)
        layout.setRowStretch(i, 4)
        i += 1

        # create info form
        self.cnname_edit = QLineEdit()
        self.enname_edit = QLineEdit()
        self.aliasname_edit = QLineEdit()
        self.channel_cn_edit = QLineEdit()
        self.area_edit = QLineEdit()
        self.cnname_edit.setReadOnly(True)
        self.enname_edit.setReadOnly(True)
        self.aliasname_edit.setReadOnly(True)
        self.channel_cn_edit.setReadOnly(True)
        self.area_edit.setReadOnly(True)
        info_layout = QFormLayout()
        info_layout.addRow(QLabel('中文名：'), self.cnname_edit)
        info_layout.addRow(QLabel('英文名：'), self.enname_edit)
        info_layout.addRow(QLabel('别名：'), self.aliasname_edit)
        info_layout.addRow(QLabel('类型：'), self.channel_cn_edit)
        info_layout.addRow(QLabel('地区：'), self.area_edit)
        info_widget = QWidget()
        info_widget.setLayout(info_layout)
        layout.addWidget(info_widget, i, 1, 1, 4)
        layout.setRowStretch(i, 4)
        i += 1

        # create current page number edit and total page number label
        self.page_edit = QLineEdit()
        self.page_edit.setAlignment(QtCore.Qt.AlignRight)
        self.page_edit.setMaximumWidth(100)
        self.page_edit.returnPressed.connect(self.page_edit_return_pressed)
        self.page_label = QLabel('/0')
        page_layout = QHBoxLayout()
        page_layout.addStretch()
        page_layout.addWidget(self.page_edit)
        page_layout.addWidget(self.page_label)
        page_layout.addStretch()
        page_widget = QWidget()
        page_widget.setLayout(page_layout)
        layout.addWidget(page_widget, i, 0)

        # create previous and next page button
        prev_button = QPushButton('上一页')
        next_button = QPushButton('下一页')
        prev_button.clicked.connect(self.prev_button_clicked)
        next_button.clicked.connect(self.next_button_clicked)
        layout.addWidget(prev_button, i, 1)
        layout.addWidget(next_button, i, 2)

        # create show season addresses checkbox and copy button
        self.show_season_checkbox = QCheckBox('显示一季的下载地址')
        layout.addWidget(self.show_season_checkbox, i, 3, 1, 2)
        copy_button = QPushButton('复制')
        copy_button.clicked.connect(self.copy_button_clicked)
        layout.addWidget(copy_button, i, 5)

        # set column stretches
        layout.setColumnStretch(0, 3)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 1)
        layout.setColumnStretch(3, 1)
        layout.setColumnStretch(4, 1)
        layout.setColumnStretch(5, 3)

    def refresh(self):
        """refresh and show current page
        """
        self.record_list.clear()
        self.cnname_edit.setText('')
        self.enname_edit.setText('')
        self.aliasname_edit.setText('')
        self.channel_cn_edit.setText('')
        self.area_edit.setText('')
        self.page_edit.setText(str(self.page + 1))

        self.records = list(self.collections.find(self.condition).skip(self.page * n_records_per_page).limit(n_records_per_page))
        for record in self.records:
            self.record_list.addItem(record['data']['info']['cnname'])

    def search_button_clicked(self):
        """search records by filters and keywords
        """
        # construct filter condition
        filter_condition = {}
        for field in fields:
            # if 'all' checked, no filter
            if self.filters[field][0].checkState() == QtCore.Qt.Checked:
                continue

            # collect checked filter values
            checked_values = []
            for checkbox in self.filters[field][1:]:
                if checkbox.checkState() == QtCore.Qt.Checked:
                    checked_values.append(checkbox.text())
            filter_condition[field] = {'$in': checked_values}

        # construct and combine keyword condition
        keyword = self.keyword_edit.text()
        if keyword:
            keyword_condition = {
                '$or': [
                    {'data.info.cnname': {'$regex': keyword}},
                    {'data.info.enname': {'$regex': keyword}},
                    {'data.info.aliasname': {'$regex': keyword}}
                ]
            }
            self.condition = {
                '$and': [filter_condition, keyword_condition]
            }
        else:
            self.condition = filter_condition

        # get total record count
        count = self.collections.count_documents(self.condition)
        # calculate and show total page number
        self.page_num = (count - 1) // n_records_per_page + 1
        self.page_label.setText(f'/{self.page_num}')
        # set current page number to 0
        self.page = 0
        # refresh
        self.refresh()

    def record_list_current_row_changed(self, current_row):
        """selected a record, show seasons
        """
        self.season_list.clear()
        if current_row == -1:
            return

        self.record_index = current_row
        data = self.records[self.record_index]['data']
        for season in data['list']:
            self.season_list.addItem(season['season_cn'])

        # show record info
        self.cnname_edit.setText(data['info']['cnname'])
        self.enname_edit.setText(data['info']['enname'])
        self.aliasname_edit.setText(data['info']['aliasname'])
        self.channel_cn_edit.setText(data['info']['channel_cn'])
        self.area_edit.setText(data['info']['area'])
        self.cnname_edit.setCursorPosition(0)
        self.enname_edit.setCursorPosition(0)
        self.aliasname_edit.setCursorPosition(0)
        self.channel_cn_edit.setCursorPosition(0)
        self.area_edit.setCursorPosition(0)

    def season_list_current_row_changed(self, current_row):
        """selected a season, show formats
        """
        self.format_list.clear()
        if current_row == -1:
            return

        self.season_index = current_row
        for format in self.records[self.record_index]['data']['list'][self.season_index]['formats']:
            self.format_list.addItem(format)

    def format_list_current_row_changed(self, current_row):
        """selected a format, show episodes
        """
        self.episode_list.clear()
        if current_row == -1:
            return

        self.format = self.format_list.currentItem().text()
        for episode in self.records[self.record_index]['data']['list'][self.season_index]['items'][self.format]:
            self.episode_list.addItem(episode['episode'])

    def episode_list_current_row_changed(self, current_row):
        """selected an episode, show download ways
        """
        self.way_list.clear()
        if current_row == -1:
            return

        self.episode_index = current_row
        for file in self.records[self.record_index]['data']['list'][self.season_index]['items'][self.format][self.episode_index]['files']:
            self.way_list.addItem(file['way_cn'])

    def way_list_current_row_changed(self, current_row):
        """selected a download way, show download address(es)
        """
        self.address_edit.setPlainText('')
        if current_row == -1:
            return

        # if show season checkbox checked, show addresses of whole season
        if self.show_season_checkbox.isChecked():
            way = self.way_list.currentItem().text()
            address = ''
            for episode in self.records[self.record_index]['data']['list'][self.season_index]['items'][self.format]:
                for file in episode['files']:
                    if file['way_cn'] == way:
                        address += file['address'] + '\n'
                        break
                else:
                    address += '\n'
        # else only show address of selected episode
        else:
            way_index = current_row
            address = self.records[self.record_index]['data']['list'][self.season_index]['items'][self.format][self.episode_index]['files'][way_index]['address']
        self.address_edit.setPlainText(address)

    def copy_button_clicked(self):
        """copy download address
        """
        clipboard = QApplication.clipboard()
        clipboard.setText(self.address_edit.toPlainText())

    def page_edit_return_pressed(self):
        """jump to specific page
        """
        try:
            page = int(self.page_edit.text()) - 1
            if page >= 0 and page < self.page_num:
                self.page = page
                self.refresh()
        except:
            self.page_edit.setText(str(self.page + 1))

    def prev_button_clicked(self):
        """show previous page
        """
        if self.page > 0:
            self.page -= 1
            self.refresh()

    def next_button_clicked(self):
        """show next page
        """
        if self.page < self.page_num - 1:
            self.page += 1
            self.refresh()


if __name__ == '__main__':
    # connect database and get collections
    client = MongoClient()
    db = client['zimuzu']
    collections = db['yyets']

    # show window and run application
    app = QApplication(sys.argv)
    win = YyetsWidget(collections)
    win.show()
    app.exec_()

    # close database
    client.close()
