from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.list import OneLineListItem, MDList
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
import sqlite3
from datetime import datetime

KV = '''
ScreenManager:
    MainScreen:
    AttendanceRecordsScreen:

<MainScreen>:
    name: 'main'

    MDBoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 10
        md_bg_color: 1, 1, 1, 1

        MDLabel:
            text: "Attendance System"
            font_style: "H4"
            halign: "center"
            theme_text_color: "Primary"  

        MDTextField:
            id: lrn_input
            hint_text: "Enter LRN"
            mode: "rectangle"
            text_validate_unfocus: False

        MDRaisedButton:
            text: "Mark Attendance"
            md_bg_color: 0, 0.6, 0, 1
            on_press: app.mark_attendance()

        MDLabel:
            id: message_label
            text: ""
            halign: "center"
            theme_text_color: "Primary"

        MDRaisedButton:
            text: "View Attendance"
            md_bg_color: 0, 0.6, 0.6, 1
            on_press: app.view_attendance()

        MDRaisedButton:
            text: "Delete All Records"
            md_bg_color: 0.8, 0, 0, 1
            on_press: app.confirm_delete()

<AttendanceRecordsScreen>:
    name: 'records'

    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: 1, 1, 1, 1
        padding: 10
        spacing: 10

        MDLabel:
            text: "Attendance Records"
            font_style: "H5"
            halign: "center"
            theme_text_color: "Primary"

        MDTextField:
            id: search_input
            hint_text: "Search LRN"
            mode: "rectangle"
            on_text: app.search_attendance(self.text)

        MDScrollView:
            MDList:
                id: records_list

        MDRaisedButton:
            text: "Back"
            md_bg_color: 0.8, 0, 0, 1
            on_press: app.go_back()
'''

class MainScreen(Screen):
    pass

class AttendanceRecordsScreen(Screen):
    pass

class AttendanceApp(MDApp):
    def build(self):
        self.conn = sqlite3.connect("attendance.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS attendance (
                            id INTEGER PRIMARY KEY, 
                            lrn TEXT, 
                            timestamp TEXT)''')
        self.conn.commit()

        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(AttendanceRecordsScreen(name='records'))
        return Builder.load_string(KV)

    def mark_attendance(self):
        screen = self.root.get_screen('main')
        lrn = screen.ids.lrn_input.text.strip().upper()
        if lrn:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute("INSERT INTO attendance (lrn, timestamp) VALUES (?, ?)", (lrn, timestamp))
            self.conn.commit()
            self.show_dialog("Success", f"Attendance recorded for LRN: {lrn}")
            screen.ids.lrn_input.text = ""
        else:
            self.show_dialog("Error", "Please enter a valid LRN")

    def view_attendance(self):
        screen = self.root.get_screen('records')
        records_list = screen.ids.records_list
        records_list.clear_widgets()

        self.cursor.execute("SELECT * FROM attendance")
        records = self.cursor.fetchall()

        if records:
            for record in records:
                item = OneLineListItem(text=f"LRN: {record[1]} | {record[2]}")
                records_list.add_widget(item)
        else:
            records_list.add_widget(OneLineListItem(text="No attendance records found"))
        self.root.current = 'records'

    def search_attendance(self, query):
        screen = self.root.get_screen('records')
        records_list = screen.ids.records_list
        records_list.clear_widgets()
        
        self.cursor.execute("SELECT * FROM attendance WHERE lrn LIKE ?", (f"%{query}%",))
        records = self.cursor.fetchall()
        
        if records:
            for record in records:
                item = OneLineListItem(text=f"LRN: {record[1]} | {record[2]}")
                records_list.add_widget(item)
        else:
            records_list.add_widget(OneLineListItem(text="No matching records found"))

    def confirm_delete(self):
        self.dialog = MDDialog(
            title="Confirm Delete",
            text="Are you sure you want to delete all attendance records?",
            buttons=[
                MDRaisedButton(text="Cancel", on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="Delete", on_release=lambda x: self.delete_all_records()),
            ],
        )
        self.dialog.open()

    def delete_all_records(self):
        self.cursor.execute("DELETE FROM attendance")
        self.conn.commit()
        self.dialog.dismiss()
        self.show_dialog("Success", "All attendance records deleted")

    def go_back(self):
        self.root.current = 'main'

    def show_dialog(self, title, message):
        dialog = MDDialog(title=title, text=message, buttons=[MDRaisedButton(text="OK", on_release=lambda x: dialog.dismiss())])
        dialog.open()

    def on_stop(self):
        self.conn.close()

if __name__ == "__main__":
    AttendanceApp().run()
