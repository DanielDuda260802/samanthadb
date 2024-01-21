import sqlite3
import os
from cmd import Cmd

def format_db_name(name):
    if not name.endswith(".db"):
        name += ".db"
    return name

def create_or_connect_database(db_name):
    conn = sqlite3.connect(db_name)
    return conn

def print_table(rows, column_names):
    # Find the maximum width of each column
    widths = [len(col) for col in column_names]
    for row in rows:
        for i, col in enumerate(row):
            widths[i] = max(widths[i], len(str(col)))

    # Create a horizontal line
    horizontal_line = '+' + '+'.join(['-' * (width + 2) for width in widths]) + '+'

    # Print the top line
    print(horizontal_line)

    # Print the column headers
    header_row = '| ' + ' | '.join(f"{name:<{widths[i]}}" for i, name in enumerate(column_names)) + ' |'
    print(header_row)

    # Print the line after headers
    print(horizontal_line)

    # Print the rows
    for row in rows:
        print('| ' + ' | '.join(f"{str(col):<{widths[i]}}" for i, col in enumerate(row)) + ' |')

    # Print the bottom line
    print(horizontal_line)

def execute_sql(conn, sql):
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        if sql.strip().lower().startswith("select"):
            rows = cursor.fetchall()
            if not rows:
                print("No results found.")
            else:
                # Fetch the column names
                column_names = [description[0] for description in cursor.description]
                print_table(rows, column_names)
        else:
            conn.commit()
            print("Query executed successfully.")
    except sqlite3.OperationalError as e:
        print(f"Error executing query: error returned from database: {e}")

class DatabaseCLI(Cmd):
    intro = 'Welcome to the SamanthaDB CLI. Type help or ? to list commands.\n\nWhen connected to a database, use standard SQLite queries to interact with the database.'
    database_name = 'None'
    prompt = f'\nSamanthaDB[{database_name}]> '
    conn = None

    def do_use(self, arg):
        """ use [database_name]: Used to connect to a database (creates a database if it doesn't exist) """
        db_name = arg + '.db'

        if not os.path.exists(db_name):
            print(f"{db_name} does not exist.")
            return

        if db_name:
            self.database_name = db_name
            self.conn = create_or_connect_database(self.database_name)
            self.prompt = f'\nSamanthaDB[{self.database_name}]> '
            print(f"Database switched to '{self.database_name}'")
        else:
            print("Invalid database name.")

    def do_create(self, arg):
        """ create [database_name]: Creates a database (automatically connects to the database) """
        db_name = arg + '.db'
        if db_name:
            self.database_name = db_name
            self.conn = create_or_connect_database(db_name)
            self.prompt = f'\nSamanthaDB[{self.database_name}]> '
            print(f"Database '{db_name}' created.\nSuccessfully connected to {db_name}")
        else:
            print("Invalid database name.")

    def do_drop(self, arg):
        """ drop [database_name]: Closes connection to a database and deletes it from file system """
        db_name = arg + '.db'
        if db_name:
            if self.conn:
                self.conn.close()
                print("Closing database connection...")
            try:
                os.remove(db_name)
                print(f"Database '{db_name}' dropped successfully.")
            except OSError as e:
                print(f"Error dropping database '{db_name}': {e}")
            self.database_name = 'None'
            self.conn = None
            self.prompt = f'\nSamanthaDB[{self.database_name}]> '
        else:
            print("Invalid database name.")

    def do_show(self, arg):
        """ show [tables]: Shows all tables within a database """
        if arg.lower() == 'tables' and self.conn:
            execute_sql(self.conn, "SELECT name FROM sqlite_master WHERE type='table';")
        else:
            print("No database selected or invalid command.")

    def do_exit(self, arg):
        """ Closes connection to a database and exits the program """
        if self.conn:
            self.conn.close()
            print("Connection closed.")
        print("Goodbye!")
        return True

    def default(self, line):
        if self.conn:
            execute_sql(self.conn, line)
        else:
            print("No database selected or invalid command.")

if __name__ == '__main__':
    cli = DatabaseCLI()
    cli.cmdloop()
