from collections import OrderedDict
import datetime
import sys
import os
import csv

from peewee import *

db = SqliteDatabase('inventory.db')


class Product(Model):
    product_id = AutoField()
    product_name = CharField(max_length=100, unique=True)
    product_quantity = IntegerField()
    product_price = IntegerField()
    date_updated = DateField()

    class Meta:
        database = db


def initialize():
    db.connect()
    db.create_tables([Product], safe=True)
    db.close()


def start():
    initialize()
    read_csv()
    clear()
    welcome()


def read_csv():
    """Read and Write CSV into Table"""
    with open('inventory.csv', newline='') as csvfile:
        productreader = csv.DictReader(csvfile)
        rows = list(productreader)
        for row in rows:
            row['product_price'] = int(row['product_price'].replace('$', '').replace('.', ''))
            row['product_quantity'] = int(row['product_quantity'])
            row['date_updated'] = (datetime.datetime.strptime(row['date_updated'], '%m/%d/%Y').date())
            try:
                Product.create(
                    product_name=row['product_name'],
                    product_quantity=row['product_quantity'],
                    product_price=row['product_price'],
                    date_updated=row['date_updated']
                ).save()
            except IntegrityError:
                updated = Product.get(product_name=row['product_name'])
                updated.product_name = row['product_name']
                updated.product_quantity = row['product_quantity']
                updated.product_price = row['product_price']
                updated.date_updated = row['date_updated']
                updated.save()


def menu_loop():
    """Main Menu"""
    start()
    selection = None
    while selection != 'e':
        for key, value in menu_list.items():
            print(f'   {key}) {value.__doc__}')
        print("Press 'e' to exit.\n")
        selection = input("What do you want to do?> ").lower().strip()
        if selection == 'e':
            print('Thanks for using this app!')
            break
        if selection not in menu_list and selection != 'e':
            print('Please choose a valid option!')
            continue
        elif selection in menu_list:
            clear()
            menu_list[selection]()


def backup_data():
    """Create a Backup CSV"""
    clear()
    backup_file = "inventory_backup.csv"
    field_titles = [
        'product_name',
        'product_price',
        'product quantity',
        'date_updated',
    ]

    with open(backup_file, 'w', newline='') as csvfile:
        backup_writer = csv.DictWriter(csvfile, fieldnames=field_titles)
        backup_writer.writeheader()
        products = Product.select()
        for product in products:
            backup_writer.writerow({
                'product_name': product.product_name,
                'product_quantity': product.product_quantity,
                'product_price': product.product_price,
                'date_updated': product.date_updated
            })

    if os.path.isfile(backup_file):
        clear()
        print("Your Backup CSV has been updated!")
    else:
        clear()
        print("Something went wrong, please try again")


def welcome():
    """Show Welcome Message"""
    message = "Welcome to Wilson's Inventory App!"
    print(message + "\n")
    print('=' * int(len(message)))


def add_product():
    """Add product"""
    new = Product()
    try:
        while True:
            try:
                new.product_name = input("What's this product called? ")
                if new.product_name == "":
                    raise ValueError("product must have a name!")
            except ValueError:
                print("That's not a valid name")
                continue
            else:
                break

        while True:
            try:
                new.product_quantity = int(input(f"How many {new.product_name} are there? "))
                if new.product_quantity < 0:
                    raise ValueError("You must add at least a quantity of 1!")
            except ValueError:
                print("That's not a valid amount!")
                continue
            else:
                break

        while True:
            try:
                new.product_price = float(input(f"How much does each {new.product_name} cost? $"))
                new.product_price = int(new.product_price * 100)
                break
            except ValueError:
                print("Sorry that's not a valid price!")
                continue

        new.date_updated = datetime.datetime.now().date()
        new.save()
        clear()
        print("product has been successfully added to inventory!")

    except IntegrityError:
        retrieve = Product.get(Product.product_name == new.product_name)
        retrieve.product_quantity = new.product_quantity
        retrieve.product_price = new.product_price
        retrieve.date_updated = new.date_updated
        retrieve.save()
        clear()
        print(f"{retrieve.product_name} has been updated!")


def show_product():
    """Show product Using ID Number"""

    while True:
        try:
            id_num = display_products(int(input("Please enter a valid product ID number: ")))
            if id_num != Product.product_id:
                raise ValueError
            break
        except ValueError:
            print("Please try again!")
            break


def display_products(id_num=None):
    """View All products"""

    all_items = Product.select().order_by(Product.product_id.asc())

    if id_num:
        all_items = Product.select().where(Product.product_id == id_num)

    for items in all_items:
        print(f"\n  ID Number: {items.product_id}")
        print(f" product name: {items.product_name}")
        print(f" product Quantity: {items.product_quantity}")
        print(f" product Price: {items.product_price}")
        print(f" Last Updated: {items.date_updated}\n\n")
        print(f" Press n for next entry or m to get to the menu")
        action = input("What would you like to do? ").lower().strip()
        if action == 'm':
            break
        elif action == 'n':
            clear()


menu_list = OrderedDict([('a', add_product),
                         ('b', backup_data),
                         ('s', show_product),
                         ('v', display_products)
                         ])


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


if __name__ == '__main__':
    menu_loop()
