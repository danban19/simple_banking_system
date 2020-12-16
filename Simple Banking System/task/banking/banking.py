import random
import sys
from datetime import datetime
import sqlite3

conn = sqlite3.connect('card.s3db')
cur = conn.cursor()
# cur.execute('CREATE TABLE card (id INTEGER, number TEXT, pin TEXT, balance INTEGER DEFAULT 0);')
conn.commit()
card_number = ''
pin = ''
id = 0
balance = 0

def greetings():
    print('1. Create an account')
    print('2. Log into account')
    print('0. Exit\n')
    mode = input()
    if mode == '1':
        create_account()
    elif mode == '2':
        account_login()
    elif mode == '0':
        print('Bye!')
        sys.exit()

def luhn_alghoritm():
    bin_number = '400000'
    account_identifier = ''.join(str(random.randint(0, 9)) for element in range(1, 10))
    elements_sum = 0
    card_number = bin_number + account_identifier
    for i, element in enumerate(card_number):
        if i % 2 == 0:
            if int(int(element) * 2) > 9:
                elements_sum += int(element) * 2 - 9
            else:
                elements_sum += int(element) * 2
        else:
            elements_sum += int(element)
    if elements_sum % 10 != 0:
        last_number = str(10 - elements_sum % 10)
    else:
        last_number = '0'
    card_number += last_number
    return(card_number)

def luhn_check(card_number):
    c = [int(x) for x in card_number[::-2]]
    u = [(2 * int(y)) // 10 + (2 * int(y)) % 10 for y in card_number[-2::-2]]
    return sum(c + u) % 10 == 0

def create_account():
    card_number = luhn_alghoritm()
    random.seed(datetime.now())
    pin = ''.join([str(element) for element in random.sample(range(9), 4)])
    id = str(random.randint(0, 9999))
    print('Your card has been created')
    print('Your card number:')
    print(card_number)
    print("Your card PIN:")
    print(pin)
    print('\n')
    cur.execute(f'INSERT INTO card (id, number, pin, balance) VALUES ({int(id)}, {card_number}, {pin}, 0)')
    conn.commit()
    greetings()

def account_login():
    input_card_number = input('Enter your card number:')
    input_pin = input('Enter your PIN:')
    if cur.execute(f'SELECT number FROM card WHERE number = {input_card_number};').fetchone() != None:
        database_card_number = cur.execute(f'SELECT number FROM card WHERE number={input_card_number};').fetchone()[0]
        database_pin = cur.execute(f'SELECT pin FROM card WHERE number={input_card_number};').fetchone()[0]
        if input_card_number == database_card_number and input_pin == database_pin:
            print("You have successfully logged in!")
            card_number = input_card_number
            account_management(card_number)
        else:
            print("Wrong card number or PIN!\n")
            greetings()
    else:
        print("Wrong card number or PIN!\n")
        greetings()

def account_management(card_number):
    print('1. Balance')
    print('2. Add income')
    print('3. Do transfer')
    print('4. Close account')
    print('5. Log out')
    print('0. Exit\n')
    account_management_mode = input()
    if account_management_mode == '1':
        account_management(card_number)
    elif account_management_mode == '2':
        old_income = int(cur.execute(f'SELECT balance FROM card WHERE number = {card_number};').fetchone()[0])
        income_to_add = int(input('Enter income:\n'))
        cur.execute(f'UPDATE card SET balance = {old_income + income_to_add} WHERE number = {card_number}')
        conn.commit()
        print('Income was added!')
        account_management(card_number)
    elif account_management_mode == '3':
        print('Transfer\n')
        card_number_to_transfer = input('Enter card number:\n')
        if not luhn_check(card_number_to_transfer):
            print('Probably you made a mistake in the card number. Please try again!')
            account_management(card_number)
        if card_number_to_transfer == card_number:
            print("You can't transfer money to the same account!")
            account_management(card_number)
        if not cur.execute(f'SELECT number FROM card WHERE number = {card_number_to_transfer};').fetchone():
            print('Such a card does not exist.')
            account_management(card_number)
        else:
            money_to_transfer = int(input('Enter how much money you want to transfer:\n'))
            print(cur.execute(f'SELECT balance FROM card WHERE number = {card_number};').fetchone()[0])
            if money_to_transfer > cur.execute(f'SELECT balance FROM card WHERE number = {card_number};').fetchone()[0]:
                print('Not enough money!')
                account_management(card_number)
            else:
                first_balance = int(cur.execute(f'SELECT balance FROM card WHERE number = {card_number};').fetchone()[0])
                second_balance = int(cur.execute(f'SELECT balance FROM card WHERE number = {card_number_to_transfer};').fetchone()[0])
                cur.execute(f'UPDATE card SET balance = {first_balance - money_to_transfer} WHERE number = {card_number};')
                cur.execute(f'UPDATE card SET balance = {second_balance + money_to_transfer} WHERE number = {card_number_to_transfer};')
                conn.commit()
                print('Success!')
                greetings()
    elif account_management_mode == '4':
        cur.execute(f'DELETE FROM card WHERE number = {card_number}')
        conn.commit()
        print('The account has been closed!\n')
        greetings()
    elif account_management_mode == '5':
        print('You have successfully logged out!\n')
        greetings()
    elif account_management_mode == '0':
        print('Bye')
        conn.commit()
        sys.exit()

greetings()