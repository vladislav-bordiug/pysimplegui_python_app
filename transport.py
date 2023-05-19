import sqlite3
import PySimpleGUI as sg
class Transport:
    def __init__(self):
        self.connection = sqlite3.connect('transport.db')
        self.cursor = self.connection.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS transports(id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, load_capacity REAL, length REAL, width REAL, height REAL, availability TEXT)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS orders(phone TEXT, name TEXT, weight REAL, length REAL, width REAL, height REAL, transport INTEGER)")
        self.connection.commit()
    def add_transport(self, type, load_capacity, length, width, height):
        self.cursor.execute(f"INSERT into transports(type,load_capacity,length,width,height,availability) VALUES(?,?,?,?,?,?);", (type, load_capacity, length, width, height, 'YES'))
        self.connection.commit()
    def delete_transport(self,id):
        self.cursor.execute(f"DELETE from transports where id = ?;", (id,))
        self.cursor.execute(f"DELETE from orders where transport = ?;", (id,))
        self.connection.commit()
    def set_not_available_transport(self,id):
        self.cursor.execute(f"UPDATE transports set availability = 'NO' where id = ?;", (id,))
        self.connection.commit()
    def add_order(self, phone, name, weight, length, width, height, transport):
        self.cursor.execute(f"INSERT into orders VALUES(?,?,?,?,?,?,?);", (phone, name, weight, length, width, height, transport))
        self.connection.commit()
    def get_available_transports(self):
        self.cursor.execute("SELECT * FROM transports where availability='YES'")
        res = self.cursor.fetchall()
        return res
    def get_not_available_transports(self):
        self.cursor.execute("SELECT * FROM transports where availability='NO'")
        res = self.cursor.fetchall()
        return res
    def get_transport_by_id(self, id):
        self.cursor.execute(f"SELECT * FROM transports where id =?;", (id,))
        res = self.cursor.fetchone()
        return res
    def get_available_order_transports(self, weight, length, width, height):
        self.cursor.execute(f"SELECT * FROM transports where ? <= load_capacity AND ? <= length AND ? <= width AND ? <= height AND availability='YES';", (weight, length, width, height))
        res = self.cursor.fetchall()
        return res
    def get_orders(self):
        self.cursor.execute("SELECT * FROM orders")
        res = self.cursor.fetchall()
        return res
class NotFloat(Exception):
    def print(self):
        sg.Popup("Error", 'The entered data is incorrect', keep_on_top=True)
class NotChosen(Exception):
    def print(self):
        sg.Popup("Error", "You have not chosen transport", keep_on_top=True)
class NotSuitable(Exception):
    def print(self):
        sg.Popup("Error", "This transport does not fit the specified dimensions", keep_on_top=True)
class Interface:
    def __init__(self):
        self.t = Transport()
        headings = ['ID','Type ','Load capacity, t','Length, m','Width, m','Height, m','Availability']
        self.data=[]
        headings_orders = ['Phone number','Name','Weight', 'Length', 'Width', 'Height','Transport ID']
        layout = [
            [sg.Button('Show transport'), sg.Checkbox('Available'), sg.Checkbox('Not available'),sg.Checkbox('Sort')],
            [sg.Button('Add transport'), sg.Button('Delete transport'), sg.Button('Add order')],
            [sg.Text('Transports:')],
            [sg.Table(self.data,headings=headings, justification='left', key='-TABLE-')],
            [sg.Text('Orders:')],
            [sg.Table(self.t.get_orders(), headings=headings_orders, justification='left', key='-ORDERS-')],
            [sg.Exit()]
        ]
        self.window = sg.Window('Transports', layout)
    def make_add_win(self):
        layout_add = [
            [sg.Text('Type'), sg.InputText()],
            [sg.Text('Load capacity, t'), sg.InputText()],
            [sg.Text('Length, m'), sg.InputText()],
            [sg.Text('Width, m'), sg.InputText()],
            [sg.Text('Height, m'), sg.InputText()],
            [sg.Submit(), sg.Exit()]
        ]
        return sg.Window('Add transport', layout_add)
    def make_order_win(self):
        headings = ['ID','Type ', 'Load capacity, t', 'Length, m', 'Width, m', 'Height, m']
        self.data = []
        layout_add = [
            [sg.Text('Your phone number'), sg.InputText()],
            [sg.Text('Your name'), sg.InputText()],
            [sg.Text('Weight, t'), sg.InputText()],
            [sg.Text('Length, m'), sg.InputText()],
            [sg.Text('Width, m'), sg.InputText()],
            [sg.Text('Height, m'), sg.InputText()],
            [sg.Button('Show suitable transport')],
            [sg.Text('Choose transport:')],
            [sg.Table(self.data, headings=headings, justification='left', key='-TABLE-ORDER-')],
            [sg.Submit(), sg.Exit()]
        ]
        return sg.Window('Add order', layout_add)
    def update(self,values):
        self.data=[]
        if values[0]:
            self.data += self.t.get_available_transports()
        if values[1]:
            self.data += self.t.get_not_available_transports()
        self.data.sort(key=lambda x: x[0])
        if values[2]:
            self.data.sort(key = lambda x: x[2])
        self.window.Element('-TABLE-').update(self.data)
        self.window.Element('-ORDERS-').update(self.t.get_orders())
    def launch(self):
        while True:
            event, values = self.window.read()
            if event in (None, 'Exit'):
                break
            if event == 'Show transport':
                self.update(values)
            if event == 'Add transport':
                window_add = self.make_add_win()
                is_opened = True
                while is_opened:
                    event_add, values_add = window_add.read()
                    if event_add in (None, 'Exit'):
                        is_opened = False
                    if event_add == 'Submit':
                        type = values_add[0]
                        load_capacity = values_add[1]
                        length = values_add[2]
                        width = values_add[3]
                        height = values_add[4]
                        try:
                            if not load_capacity.replace(".", "").isnumeric() or not length.replace(".", "").isnumeric() or not width.replace(".", "").isnumeric() or not height.replace(".", "").isnumeric():
                                raise NotFloat()
                            load = float(load_capacity)
                            l = float(length)
                            w = float(width)
                            h = float(height)
                        except NotFloat as nf:
                            nf.print()
                        else:
                            self.t.add_transport(type, load, l, w, h)
                            self.update(values)
                            sg.Popup("Successful!", 'Transport was added', keep_on_top=True)
                            is_opened = False
                window_add.close()
            if event == 'Delete transport':
                del_values = [self.data[i][0] for i in values['-TABLE-']]
                if del_values != []:
                    for i in del_values:
                        self.t.delete_transport(i)
                    self.update(values)
                    sg.Popup("Successful!", 'Transport was deleted', keep_on_top=True)
                else:
                    sg.Popup("Not deleted", 'Choose what you want to delete', keep_on_top=True)
            if event == 'Add order':
                window_order = self.make_order_win()
                opened = True
                d = []
                while opened:
                    event_order, values_order = window_order.read()
                    if event_order in (None, 'Exit'):
                        opened = False
                    if event_order == 'Show suitable transport':
                        weigh = values_order[2]
                        lengt = values_order[3]
                        widt = values_order[4]
                        heigh = values_order[5]
                        try:
                            if not weigh.replace(".", "").isnumeric() or not lengt.replace(".","").isnumeric() or not widt.replace(".", "").isnumeric() or not heigh.replace(".", "").isnumeric():
                                raise NotFloat()
                            we = float(weigh)
                            l = float(lengt)
                            w = float(widt)
                            h = float(heigh)
                        except NotFloat as nf:
                            nf.print()
                        else:
                            d = self.t.get_available_order_transports(we,l,w,h)
                            window_order.Element('-TABLE-ORDER-').update(d)
                    if event_order == 'Submit':
                        try:
                            if values_order['-TABLE-ORDER-'] == []:
                                raise NotChosen()
                        except NotChosen as nc:
                            nc.print()
                        else:
                            chosen = values_order['-TABLE-ORDER-'][0]
                            id = d[chosen][0]
                            weigh = values_order[2]
                            lengt = values_order[3]
                            widt = values_order[4]
                            heigh = values_order[5]
                            try:
                                if not weigh.replace(".", "").isnumeric() or not lengt.replace(".","").isnumeric() or not widt.replace(".", "").isnumeric() or not heigh.replace(".", "").isnumeric() or weigh[0]=='-' or lengt[0]=='-' or widt[0]=='-' or heigh[0]=='-':
                                    raise NotFloat()
                                we = float(weigh)
                                l = float(lengt)
                                w = float(widt)
                                h = float(heigh)
                            except NotFloat as nf:
                                nf.print()
                            else:
                                try:
                                    d = self.t.get_available_order_transports(we,l,w,h)
                                    if self.t.get_transport_by_id(id) not in d:
                                        raise NotSuitable()
                                except NotSuitable as ns:
                                    window_order.Element('-TABLE-ORDER-').update(d)
                                    ns.print()
                                else:
                                    self.t.add_order(values_order[0], values_order[1], we, l, w, h, id)
                                    self.t.set_not_available_transport(id)
                                    sg.Popup("Successful!", 'Order was added', keep_on_top=True)
                                    opened = False
                window_order.close()
                self.update(values)
        self.window.close()