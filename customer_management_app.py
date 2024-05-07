import sqlite3
import tkinter as tk
from tkinter import messagebox

global root
global paste_text
global listbox_customers
global entry_name
global entry_mobile
global text_notes
global entry_search
global selected_customer_name


def create_database():
    conn = sqlite3.connect('customers.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS customers(id INTEGER PRIMARY KEY, name TEXT, mobile TEXT,
     date TEXT, notes TEXT)''')
    conn.commit()
    conn.close()


def add_customer():
    name = entry_name.get().strip()
    mobile = entry_mobile.get().strip()
    if name and mobile:
        conn = sqlite3.connect('customers.db')
        c = conn.cursor()
        c.execute('''INSERT INTO customers (name, mobile) VALUES (?, ?)''', (name, mobile))
        conn.commit()
        conn.close()
        refresh_customer_list()
        entry_name.delete(0, tk.END)
        entry_mobile.delete(0, tk.END)
    else:
        messagebox.showerror("Error", "Please fill in the name and mobile number.")


def delete_selected_customer():
    global selected_customer_name

    selected_customer_index = listbox_customers.curselection()
    if selected_customer_index:
        selected_customer_info = listbox_customers.get(selected_customer_index)
        selected_customer_name = selected_customer_info.split(" - ")[0]
        confirm_delete = messagebox.askokcancel("Delete Confirmation",
                                                f"Are you sure you want to delete {selected_customer_name}? ")
        if confirm_delete:
            conn = sqlite3.connect('customers.db')
            c = conn.cursor()
            c.execute('''DELETE FROM customers WHERE name = ?''', (selected_customer_name,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", f"The customer {selected_customer_name} has been deleted successfully!")
            refresh_customer_list()
    else:
        messagebox.showerror("Error", "Select a customer to delete.")


def refresh_customer_list():
    listbox_customers.delete(0, tk.END)
    conn = sqlite3.connect('customers.db')
    c = conn.cursor()
    c.execute('''SELECT name FROM customers ORDER BY name ASC''')
    customers = c.fetchall()
    conn.close()
    if customers:
        for customer in customers:
            listbox_customers.insert(tk.END, customer[0])
    else:
        listbox_customers.insert(tk.END, "No records found.")


def select_customer(event=None):
    global selected_customer_name
    selected_customer_index = listbox_customers.curselection()
    if selected_customer_index:
        listbox_customers.selection_set(selected_customer_index[0])
        listbox_customers.see(selected_customer_index[0])

        selected_customer_name = listbox_customers.get(selected_customer_index[0])

        conn = sqlite3.connect('customers.db')
        c = conn.cursor()
        c.execute('''SELECT notes FROM customers WHERE name = ?''', (selected_customer_name,))
        customer_notes = c.fetchone()
        conn.close()

        if customer_notes and customer_notes[0]:
            text_notes.delete("1.0", tk.END)
            text_notes.insert(tk.END, customer_notes[0])
        else:
            text_notes.delete("1.0", tk.END)
            text_notes.insert(tk.END, "No notes found for this customer.")

        for i in range(listbox_customers.size()):
            listbox_customers.itemconfig(i, bg="white")
        listbox_customers.itemconfig(selected_customer_index[0], bg="#80B77C")
    else:
        conn = sqlite3.connect('customers.db')
        c = conn.cursor()
        c.execute('''SELECT name FROM customers ORDER BY name ASC''')
        customer_notes = c.fetchone()
        conn.close()


def on_listbox_double_click(event):
    select_customer()


def edit_customer():
    global selected_customer_name
    if selected_customer_name:
        conn = sqlite3.connect('customers.db')
        c = conn.cursor()
        c.execute('''SELECT * FROM customers WHERE name = ?''', (selected_customer_name,))
        customer_data = c.fetchone()
        conn.close()

        if customer_data:
            edit_window = tk.Toplevel(root)
            edit_window.title("Edit Customer")
            edit_window.geometry("300x200")

            label_edit_name = tk.Label(edit_window, font=("Helvetica", 10), text="Name:")
            label_edit_name.grid(row=0, column=0, padx=10, pady=10)
            entry_edit_name = tk.Entry(edit_window, font=("Helvetica", 10))
            entry_edit_name.grid(row=0, column=1, padx=10, pady=10)
            entry_edit_name.insert(0, customer_data[1])

            label_edit_mobile = tk.Label(edit_window, font=("Helvetica", 10), text="Mobile:")
            label_edit_mobile.grid(row=1, column=0, padx=10, pady=10)
            entry_edit_mobile = tk.Entry(edit_window, font=("Helvetica", 10))
            entry_edit_mobile.grid(row=1, column=1, padx=10, pady=10)
            entry_edit_mobile.insert(0, customer_data[2])

            btn_save_changes = tk.Button(edit_window, text="Save Changes", bg='#4682B4', fg='white',
                                         relief=tk.FLAT, command=lambda: save_changes(selected_customer_name,
                                                                                      entry_edit_name.get(),
                                                                                      entry_edit_mobile.get()))
            btn_save_changes.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

        else:
            messagebox.showerror("Error", "No data found for the selected customer.")
    else:
        messagebox.showerror("Error", "Select a customer to edit.")


def save_changes(customer_name, new_name, new_mobile):
    conn = sqlite3.connect('customers.db')
    c = conn.cursor()
    c.execute('''UPDATE customers SET name = ?, mobile = ? WHERE name = ?''', (new_name, new_mobile, customer_name))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Changes saved successfully!")
    refresh_customer_list()


def save_notes():
    global selected_customer_name
    if selected_customer_name:
        conn = sqlite3.connect('customers.db')
        c = conn.cursor()
        c.execute('''UPDATE customers SET notes = ? WHERE name = ?''',
                  (text_notes.get("1.0", tk.END).strip(), selected_customer_name))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Notes saved successfully!")
    else:
        messagebox.showerror("Error", "Select a customer to save notes.")


def filter_customers():
    search_query = entry_search.get().strip()
    if search_query:
        listbox_customers.delete(0, tk.END)
        conn = sqlite3.connect('customers.db')
        c = conn.cursor()
        c.execute('''SELECT name FROM customers WHERE name LIKE ? OR name LIKE ? OR name LIKE ? ORDER BY name ASC''',
                  (search_query + '%', search_query.capitalize() + '%', search_query.lower() + '%'))
        customers = c.fetchall()
        conn.close()
        if customers:
            for customer in customers:
                listbox_customers.insert(tk.END, customer[0])
        else:
            listbox_customers.insert(tk.END, "No results found.")
    else:
        refresh_customer_list()


def text_notes_on_click(event):
    if text_notes.get("1.0", "end-1c") == "No notes found for this customer.":
        text_notes.delete("1.0", tk.END)


def main():
    global root
    global paste_text
    global listbox_customers
    global entry_name
    global entry_mobile
    global text_notes
    global entry_search
    global selected_customer_name

    create_database()
    root = tk.Tk()
    root.title("Customer Management")
    root.configure(background='#f0f0f0')

    screen_width = 1280
    screen_height = 768

    root.geometry(f"{int(screen_width)}x{int(screen_height)}")

    label_name = tk.Label(root, text="Name:", font=("Helvetica", 12), bg='#f0f0f0')
    label_name.grid(row=0, column=0, padx=5, pady=5, sticky="E")
    entry_name = tk.Entry(root, font=("Helvetica", 12))
    entry_name.grid(row=0, column=1, padx=5, pady=5)

    label_mobile = tk.Label(root, text="Mobile:", font=("Helvetica", 12), bg='#f0f0f0')
    label_mobile.grid(row=1, column=0, padx=5, pady=5, sticky="E")
    entry_mobile = tk.Entry(root, font=("Helvetica", 12))
    entry_mobile.grid(row=1, column=1, padx=5, pady=5)

    btn_add = tk.Button(root, text="Add Customer", font=("Helvetica", 12), command=add_customer, bg='#4682B4',
                        fg='white', relief=tk.FLAT, borderwidth=0, padx=10, pady=5, border=5,
                        activebackground='#87CEFA')
    btn_add.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="WE")

    btn_delete = tk.Button(root, text="Delete Selected Customer", font=("Helvetica", 12),
                           command=delete_selected_customer, bg='#CE8D8A', fg='white', relief=tk.FLAT, borderwidth=0,
                           padx=10, pady=5, border=5, activebackground='#87CEFA')
    btn_delete.grid(row=8, column=0, columnspan=2, padx=5, pady=5, sticky="WE")

    btn_select = tk.Button(root, text="Select Customer", font=("Helvetica", 12), command=select_customer, bg='#4682B4',
                           fg='white', relief=tk.FLAT, borderwidth=0, padx=10, pady=5, border=5,
                           activebackground='#87CEFA')
    btn_select.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky="WE")

    btn_edit_customer = tk.Button(root, text="Edit Customer Details", font=("Helvetica", 12), command=edit_customer,
                                  bg='#80B77C', fg='white', relief=tk.FLAT, borderwidth=0, padx=10, pady=5, border=5,
                                  activebackground='#87CEFA')
    btn_edit_customer.grid(row=7, column=0, columnspan=2, padx=5, pady=5, sticky="WE")

    listbox_customers = tk.Listbox(root, height=20, width=30, font=("Helvetica", 12))
    listbox_customers.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="WE")
    scrollbar_customers = tk.Scrollbar(root, orient=tk.VERTICAL, command=listbox_customers.yview)
    scrollbar_customers.grid(row=5, column=2, sticky="NS")
    listbox_customers.config(yscrollcommand=scrollbar_customers.set)

    listbox_customers.bind("<Button-1>", select_customer)

    text_notes = tk.Text(root, height=int(screen_height * 0.04), width=int(screen_width * 0.07), font=("Helvetica", 12))
    text_notes.grid(row=0, column=3, rowspan=6, padx=5, pady=5, sticky="NS")

    btn_save_notes = tk.Button(root, text="Save Notes", width=1, font=("Helvetica", 12), command=save_notes,
                               bg='#4682B4', fg='white', relief=tk.FLAT, borderwidth=0, padx=5, pady=5, border=5,
                               activebackground='#87CEFA')
    btn_save_notes.grid(row=6, column=3, padx=200, pady=5, sticky="WE")

    label_search = tk.Label(root, text="Search Customer:", font=("Helvetica", 12), bg='#f0f0f0')
    label_search.grid(row=4, column=0, padx=5, pady=5, sticky="E")
    entry_search = tk.Entry(root, font=("Helvetica", 12))
    entry_search.grid(row=4, column=1, padx=5, pady=5)
    entry_search.bind('<KeyRelease>', lambda event: filter_customers())
    listbox_customers.bind('<Return>', lambda event: select_customer())
    entry_name.bind("<Return>", lambda event: entry_mobile.focus_set())
    entry_mobile.bind("<Return>", lambda event: add_customer())
    text_notes.bind("<Button-1>", text_notes_on_click)
    text_notes.bind("<Control-a>", lambda event: text_notes.tag_add(tk.SEL, "1.0", tk.END))
    text_notes.bind("<Control-c>", lambda event: text_notes.clipboard_append(text_notes.get(tk.SEL_FIRST, tk.SEL_LAST)))
    text_notes.bind("<Control-z>", lambda event: text_notes.edit_undo())
    refresh_customer_list()

    root.mainloop()


if __name__ == "__main__":
    main()
