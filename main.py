import sys
import random
import sqlite3
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMainWindow, QLCDNumber, QSlider, QStackedWidget, QPushButton, QLabel, QTextEdit, QTextBrowser, QButtonGroup, QRadioButton, QCheckBox
from PyQt5.QtCore import QTimer
from pynput.mouse import Listener



# Create or connect to DB
connect_db = sqlite3.connect('test/ui_test_results.db')

# Create Cursor object
cursor_object = connect_db.cursor()

# Create ui test table if it does not exist
table = """ CREATE TABLE if not exists UITest (
            test_id INTEGER NOT NULL,
            test_age TEXT NOT NULL,
            test_gender TEXT NOT NULL,
            test_device TEXT NOT NULL,
            test_1_task_id TEXT NOT NULL,
            test_1_UI_id TEXT NOT NULL,
            test_1_time TEXT NOT NULL,
            test_1_clicks TEXT NOT NULL,
            test_2_task_id TEXT NOT NULL,
            test_2_UI_id TEXT NOT NULL,
            test_2_time TEXT NOT NULL,
            test_2_clicks TEXT NOT NULL,
            test_3_task_id TEXT NOT NULL,
            test_3_UI_id TEXT NOT NULL,
            test_3_time TEXT NOT NULL,
            test_3_clicks TEXT NOT NULL,
            test_4_task_id TEXT NOT NULL,
            test_4_UI_id TEXT NOT NULL,
            test_4_time TEXT NOT NULL,
            test_4_clicks TEXT NOT NULL,
            test_5_task_id TEXT NOT NULL,
            test_5_UI_id TEXT NOT NULL,
            test_5_time TEXT NOT NULL,
            test_5_clicks TEXT NOT NULL,
            PRIMARY KEY("test_id" AUTOINCREMENT)); """

cursor_object.execute(table)

# Commit changes
connect_db.commit()

# Close connection
connect_db.close()


# Class contain UI test code
class UI(QMainWindow):

    def __init__(self):
        super(UI, self).__init__()

        # Class variables
        # Counter variables
        self.cnt = 40
        self.click_counter = 0
        # Answer and task variable, and ui index list for randomiser
        self.current_answer = 0
        self.current_task = 0
        self.ui_index = [2, 3, 4, 5, 6]
        # Variable to hold answer time that will be recorded in DB
        self.answer_time = 0
        # List to hold all information to be added to DB
        self.db_list = []
        # Variable used to record id of with emergency button is pressed
        self.current_emg_button = 0
        # Records last DB entry ID to be returned to user
        self.user_id = 0

        # Timer setup
        self.timer = QTimer()
        self.timer.timeout.connect(self.lcd_number)

        # Set mouse logger
        self.listener = Listener(on_click=self.on_click)
        self.listener.start()

        # Load the ui file
        uic.loadUi("Test User Interfaces.ui", self)

        # Define class wide widgets
        self.ui_switch = self.findChild(QStackedWidget, "ui_stack")
        self.ui_task_readout = self.findChild(QLabel, "task_text")
        self.ui_answer_box = self.findChild(QTextEdit, "answer_input")
        self.ui_answer_submit_button = self.findChild(QPushButton, "submit_button")
        # Class button connects
        self.ui_answer_submit_button.clicked.connect(self.check_answer)
        # Class timer display connect
        self.countdown = self.findChild(QLCDNumber, "timer_display")

        # Define start screen widgets
        self.start_button = self.findChild(QPushButton, "start_button")
        # Start screen connect
        self.start_button.clicked.connect(lambda: self.ui_switch.setCurrentIndex(8))

        # Define end screen widgets
        self.end_id_label = self.findChild(QLabel, "id_label")

        # Define question screen widgets
        self.ux_start_button = self.findChild(QPushButton, "ux_start_button")
        self.warning_label = self.findChild(QLabel, "warning_label")
        # Age question buttons
        self.radio_age_1 = self.findChild(QRadioButton, "age_1_button")
        self.radio_age_2 = self.findChild(QRadioButton, "age_2_button")
        self.radio_age_3 = self.findChild(QRadioButton, "age_3_button")
        self.radio_age_4 = self.findChild(QRadioButton, "age_4_button")
        self.radio_age_5 = self.findChild(QRadioButton, "age_5_button")
        # Gender question buttons
        self.radio_gender_1 = self.findChild(QRadioButton, "gender_1_button")
        self.radio_gender_2 = self.findChild(QRadioButton, "gender_2_button")
        self.radio_gender_3 = self.findChild(QRadioButton, "gender_3_button")
        self.radio_gender_4 = self.findChild(QRadioButton, "gender_4_button")
        # Device question buttons
        self.check_device_1 = self.findChild(QCheckBox, "device_check_1")
        self.check_device_2 = self.findChild(QCheckBox, "device_check_2")
        self.check_device_3 = self.findChild(QCheckBox, "device_check_3")
        self.check_device_4 = self.findChild(QCheckBox, "device_check_4")
        # Start question connect
        self.ux_start_button.clicked.connect(self.ux_start_button_clicked)

        # Define pending screen widgets
        self.continue_button = self.findChild(QPushButton, "next_test_button")
        # Pending screen connect
        self.continue_button.clicked.connect(self.next_test)

        # Define tile ui widgets
        self.news_slider = self.findChild(QSlider, "news_slider")
        self.news_stack = self.findChild(QStackedWidget, "news_stack")
        self.emg_chat_slider = self.findChild(QSlider, "emg_chat_slider")
        self.emg_chat_stack = self.findChild(QStackedWidget, "emg_chat_stack")
        self.emg_rpt_slider = self.findChild(QSlider, "emg_rpt_slider")
        self.emg_rpt_stack = self.findChild(QStackedWidget, "emg_rpt_stack")
        self.hzd_slider = self.findChild(QSlider, "hzd_slider")
        self.hzd_stack = self.findChild(QStackedWidget, "hzd_stack")
        self.faq_slider = self.findChild(QSlider, "faq_slider")
        self.faq_stack = self.findChild(QStackedWidget, "faq_stack")
        self.tile_emg_chat_input = self.findChild(QTextEdit, "chat_tile_input")
        self.tile_emg_chat_output = self.findChild(QTextBrowser, "chat_tile_response_terminal")
        self.tile_emg_chat_button = self.findChild(QPushButton, "chat_tile_submit_button")
        # Define tile ui connect
        self.tile_emg_chat_button.clicked.connect(self.emergency_chat)
        self.news_slider.valueChanged.connect(lambda: self.move_tile_stack(self.news_slider.value(), self.news_stack))
        self.emg_chat_slider.valueChanged.connect(lambda: self.move_tile_stack(self.emg_chat_slider.value(), self.emg_chat_stack))
        self.emg_rpt_slider.valueChanged.connect(lambda: self.move_tile_stack(self.emg_rpt_slider.value(), self.emg_rpt_stack))
        self.hzd_slider.valueChanged.connect(lambda: self.move_tile_stack(self.hzd_slider.value(), self.hzd_stack))
        self.faq_slider.valueChanged.connect(lambda: self.move_tile_stack(self.faq_slider.value(), self.faq_stack))

        # Define tab ui widgets
        self.tab_emg_chat_input = self.findChild(QTextEdit, "chat_tab_input")
        self.tab_emg_chat_output = self.findChild(QTextBrowser, "chat_tab_response_terminal_5")
        self.tab_emg_chat_button = self.findChild(QPushButton, "chat_tab_submit_button_5")
        # Define tab ui connects
        self.tab_emg_chat_button.clicked.connect(self.emergency_chat)

        # Define scroll ui widgets
        self.scroll_emg_chat_input = self.findChild(QTextEdit, "chat_scroll_input")
        self.scroll_emg_chat_output = self.findChild(QTextBrowser, "chat_scroll_response_terminal")
        self.scroll_emg_chat_button = self.findChild(QPushButton, "chat_scroll_submit_button")
        # Define scroll ui connect
        self.scroll_emg_chat_button.clicked.connect(self.emergency_chat)

        # Define list ui widgets
        self.list_emg_chat_input = self.findChild(QTextEdit, "chat_list_input")
        self.list_emg_chat_output = self.findChild(QTextBrowser, "chat_list_response_terminal")
        self.list_emg_chat_button = self.findChild(QPushButton, "chat_list_submit_button")
        # Define list ui connect
        self.list_emg_chat_button.clicked.connect(self.emergency_chat)

        # Define right bar ui widgets
        self.rht_stack = self.findChild(QStackedWidget, "rht_bar_stack")
        self.rht_home_button = self.findChild(QPushButton, "home_button")
        self.rht_news_button = self.findChild(QPushButton, "news_button")
        self.rht_hzd_button = self.findChild(QPushButton, "hzd_symbol_button")
        self.rht_emg_chat_select_button = self.findChild(QPushButton, "emg_chat_button")
        self.rht_emg_rpt_button = self.findChild(QPushButton, "emg_rsp_button")
        self.rht_faq_button = self.findChild(QPushButton, "faq_button")
        self.rht_emg_chat_input = self.findChild(QTextEdit, "chat_rht_input")
        self.rht_emg_chat_output = self.findChild(QTextBrowser, "chat_rht_response_terminal")
        self.rht_emg_chat_button = self.findChild(QPushButton, "chat_rht_submit_button")
        # Define right bar connect
        self.rht_home_button.clicked.connect(lambda: self.rht_stack.setCurrentIndex(0))
        self.rht_news_button.clicked.connect(lambda: self.rht_stack.setCurrentIndex(1))
        self.rht_hzd_button.clicked.connect(lambda: self.rht_stack.setCurrentIndex(2))
        self.rht_emg_chat_select_button.clicked.connect(lambda: self.rht_stack.setCurrentIndex(3))
        self.rht_emg_rpt_button.clicked.connect(lambda: self.rht_stack.setCurrentIndex(4))
        self.rht_faq_button.clicked.connect(lambda: self.rht_stack.setCurrentIndex(5))
        self.rht_emg_chat_button.clicked.connect(self.emergency_chat)

        # Set starting UI displayed
        self.ui_switch.setCurrentIndex(0)

        # Button Group for emg_buttons allowing single function
        self.emg_button_check = QButtonGroup()
        self.emg_button_check.addButton(self.tab_emg_chat_button, 1)
        self.emg_button_check.addButton(self.scroll_emg_chat_button, 2)
        self.emg_button_check.addButton(self.tile_emg_chat_button, 3)
        self.emg_button_check.addButton(self.list_emg_chat_button, 4)
        self.emg_button_check.addButton(self.rht_emg_chat_button, 5)
        self.emg_button_check.buttonPressed.connect(self.emg_button_pressed)

        # Question age radio button group
        self.age_radio_button = QButtonGroup()
        self.age_radio_button.addButton(self.radio_age_1, 1)
        self.age_radio_button.addButton(self.radio_age_2, 2)
        self.age_radio_button.addButton(self.radio_age_3, 3)
        self.age_radio_button.addButton(self.radio_age_4, 4)
        self.age_radio_button.addButton(self.radio_age_5, 5)

        # Question gender radio button group
        self.gender_radio_button = QButtonGroup()
        self.gender_radio_button.addButton(self.radio_gender_1, 1)
        self.gender_radio_button.addButton(self.radio_gender_2, 2)
        self.gender_radio_button.addButton(self.radio_gender_3, 3)
        self.gender_radio_button.addButton(self.radio_gender_4, 4)

        # Question device checkbox group
        self.device_check_Box = QButtonGroup()
        self.device_check_Box.addButton(self.check_device_1, 1)
        self.device_check_Box.addButton(self.check_device_2, 2)
        self.device_check_Box.addButton(self.check_device_3, 3)
        self.device_check_Box.addButton(self.check_device_4, 4)
        self.device_check_Box.setExclusive(False)

        # Question Variables
        q_a = "Enter article number of weather effecting Bonn"
        q_b = "Enter the answer number of the caution symbol"
        q_c = "Enter the number to contact the fire department in Germany"
        q_d = "Enter the response code for Hurricane"
        q_e = "Enter the year the application was created"

        # Setting Task Dictionary to link task id to question and answer
        self.task_dict = {1: [q_a, "3"], 2: [q_b, "4"], 3: [q_c, "110"], 4: [q_d, "99"], 5: [q_e, "2023"]}

    # Allows test to be started after question screen, and ensure each question is answered
    def ux_start_button_clicked(self):
        # Checks all questions are answered
        if self.device_check_Box.checkedButton() is not None and self.age_radio_button.checkedButton() is not None and self.gender_radio_button.checkedButton() is not None:

            # Adds selected gender to list to be added to DB
            gen_string = ''.join(btn.text() for btn in self.gender_radio_button.buttons() if btn.isChecked() is True)
            self.db_list.append(gen_string)

            # Adds selected age to list to be added to DB
            age_string = ''.join(btn.text() for btn in self.age_radio_button.buttons() if btn.isChecked() is True)
            self.db_list.append(age_string)

            # Adds selected age to list to be added to DB
            device_string = ' '.join(btn.text() for btn in self.device_check_Box.buttons() if btn.isChecked() is True)
            self.db_list.append(device_string)

            self.first_test()

        # Alt method to check ticked option
        # for btn in self.gender_radio_button.buttons():
        #       if btn.isChecked() is True:
        #       self.db_list.append(btn.text())

        else:
            self.warning_label.setText("All questions must be answered before you can begin")

    # Function to begin the first test of the set of 5
    def first_test(self):
        self.click_counter = 0
        # Update timer
        self.countdown.display(self.cnt)
        # Start timer
        self.timer.start(1000)
        self.ui_randomiser()

    # Function to begin ever test after the first
    def next_test(self):
        if len(self.ui_index) > 0:
            # Set timer
            self.cnt = 40
            # Reset click counter
            self.click_counter = 0
            # Reset answer holder
            self.answer_time = 0
            # Update timer
            self.countdown.display(self.cnt)
            # Start timer
            self.timer.start(1000)
            # Selects random task and UI
            self.ui_randomiser()
        else:
            # Takes to end screen
            self.ui_switch.setCurrentIndex(1)

    # Function to record mouse clicks in Ux test
    def on_click(self, x, y, button, pressed):
        if pressed:
            self.click_counter = self.click_counter + 1

    # Allows each stack in tile UI to be navigated
    def move_tile_stack(self, value, stack_ref):
        stack_ref.setCurrentIndex(5)
        if value == 0:
            stack_ref.setCurrentIndex(0)
        elif value == 1:
            stack_ref.setCurrentIndex(1)
        elif value == 2:
            stack_ref.setCurrentIndex(2)
        elif value == 3:
            stack_ref.setCurrentIndex(3)
        elif value == 4:
            stack_ref.setCurrentIndex(4)
        elif value == 5:
            stack_ref.setCurrentIndex(5)

    # Function to randomise tasks and presented UI test
    def ui_randomiser(self):
        if len(self.ui_index) > 0:
            # Random task select
            new_task = random.choice(list(self.task_dict.items()))
            self.current_task = new_task
            # Save current task to db list
            self.db_list.append(self.current_task[0])
            # Remove task from task list
            self.task_dict.pop(new_task[0])
            # Display task to UI
            self.ui_task_readout.setText(new_task[1][0])
            # Random UI select
            new_ui = random.choice(self.ui_index)
            # Save current task to db list
            self.db_list.append(new_ui)
            # Remove UI from task list
            self.ui_index.remove(new_ui)
            # Navigate to UI
            self.ui_switch.setCurrentIndex(new_ui)
        else:
            # Go to end screen as fault condition
            self.ui_switch.setCurrentIndex(7)

    # Add all information in database list to SQLite DB
    def add_to_db(self):
        # Connect to DB
        connect_db = sqlite3.connect('test/ui_test_results.db')
        # Create Cursor object
        cursor_object = connect_db.cursor()
        # Cursor insert to table

        cursor_object.execute("INSERT INTO UITest (test_age, test_gender, test_device, test_1_task_id, test_1_UI_id, test_1_time, test_1_clicks, "
                              "test_2_task_id, test_2_UI_id, test_2_time, test_2_clicks, test_3_task_id, test_3_UI_id, "
                              "test_3_time, test_3_clicks, test_4_task_id, test_4_UI_id, test_4_time, test_4_clicks, test_5_task_id, test_5_UI_id, test_5_time, test_5_clicks) "
                              "VALUES(?, ?, ?, ?, ? , ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                              (self.db_list[0], self.db_list[1], self.db_list[2], self.db_list[3], self.db_list[4], self.db_list[5], self.db_list[6], self.db_list[7], self.db_list[8],
                               self.db_list[9], self.db_list[10], self.db_list[11], self.db_list[12], self.db_list[13], self.db_list[14],
                               self.db_list[15], self.db_list[16], self.db_list[17], self.db_list[18], self.db_list[19], self.db_list[20], self.db_list[21], self.db_list[22]))
        # Commit changes
        connect_db.commit()
        # Record user ID
        self.user_id = cursor_object.lastrowid
        # Close connection
        connect_db.close()

    # Function to control timer, and present its display. Also used to set end conditions of each test
    def lcd_number(self):
        # If user has run out of time
        if self.cnt == 0:
            self.timer.stop()
            self.ui_task_readout.setText("Awaiting Task")
            # Add results to db list
            self.db_list.append(self.answer_time)
            self.db_list.append(self.click_counter)
            # If all UI tests completed
            if len(self.ui_index) == 0:
                self.ui_task_readout.setText("Test Complete")
                self.ui_switch.setCurrentIndex(7)
                self.add_to_db()
                self.end_id_label.setText(str(self.user_id))
            # Else clear task box and go to pending screen
            else:
                self.ui_answer_box.clear()
                self.ui_switch.setCurrentIndex(1)
            # self.add_to_db(self.cnt,self.click_counter)
        else:
            # Decrement counter
            self.cnt = self.cnt-1
            # Display The Time
            self.countdown.display(self.cnt)

    # Confirms if USer has entered correct answer for given task
    def check_answer(self):
        # Checks not all answers have been answered, not strictly needed
        if len(self.db_list) != 0:
            # Checks input answer against task answer in answer dictionary
            if self.ui_answer_box.toPlainText() == self.current_task[1][1]:  # type: ignore
                # Save correct answer time to list
                self.answer_time = self.cnt
                self.cnt = 0

    # Records which Ui emergency chat button was pressed
    def emg_button_pressed(self, btn_id):
        self.current_emg_button = self.emg_button_check.id(btn_id)

    # Function to allow emergency chat screen to return response code, when emergency code is input
    def emergency_chat(self):
        chat_input = 0
        chat_output = 0

        # Confirms which UI needs emergency chat function
        if self.current_emg_button == 1:
            chat_input = self.tab_emg_chat_input.toPlainText()
            chat_output = self.tab_emg_chat_output
        elif self.current_emg_button == 2:
            chat_input = self.scroll_emg_chat_input.toPlainText()
            chat_output = self.scroll_emg_chat_output
        elif self.current_emg_button == 3:
            chat_input = self.tile_emg_chat_input.toPlainText()
            chat_output = self.tile_emg_chat_output
        elif self.current_emg_button == 4:
            chat_input = self.list_emg_chat_input.toPlainText()
            chat_output = self.list_emg_chat_output
        elif self.current_emg_button == 5:
            chat_input = self.rht_emg_chat_input.toPlainText()
            chat_output = self.rht_emg_chat_output

        # Determines inputs to return for each emergency code
        if chat_input == "111":
            chat_output.setText("77")
        elif chat_input == "222":
            chat_output.setText("88")
        elif chat_input == "333":
            chat_output.setText("99")
        elif chat_input == "444":
            chat_output.setText("1010")
        elif chat_input == "555":
            chat_output.setText("1111")


# Displays the UI
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    UIWindow = UI()
    UIWindow.show()
    sys.exit(app.exec_())
