import h5py
import os
import pyperclip
from cryptography.fernet import Fernet
from getpass import getpass
from time import sleep

DS_NAME = 'prov|usr|psw'
HDF5_PATH = 'PATH/TO.HDF5_FILE'
KEY_PATH = 'PATH/TO/secret.key' # this contains the key to password encryption/decryption
PASSWORD_TO_ACCESS_SCRIPT = "pass"

def generate_key():
    """
    Generates a key and save it into a file - only once executed
    """
    key = Fernet.generate_key()
    with open(KEY_PATH, "wb") as key_file:
        key_file.write(key)

def load_key():
    """
    Loads the key named `secret.key` from the current directory.
    """
    return open(KEY_PATH, "rb").read()


def encrypt(str_):
    """
    Encodes and encrypts a string
    """
    message = str_.encode('ascii', 'ignore')

    key = load_key()
    fernet = Fernet(key)

    encrypted_message = fernet.encrypt(message)

    return encrypted_message

def decrypt(str_encoded):
    """
    Decrypts and decodes an encoded string.
    """
    key = load_key()
    fernet = Fernet(key)

    decrypted_message = fernet.decrypt(str_encoded)
    decoded_message = decrypted_message.decode('utf-8')

    return decoded_message


def append_one():
    provider_to_add = input("Provider name (account type): ")
    user_to_add = input("Username: ")
    pass_to_add = input("Password: ")

    triple_strings = (provider_to_add, user_to_add, pass_to_add)

    with h5py.File(HDF5_PATH, mode='a') as hf:
        hf[DS_NAME].resize((hf[DS_NAME].shape[0] + 1), axis=0)

        data_to_append = ["", "", ""]
        data_to_append[0] = triple_strings[0].encode('ascii', 'ignore')
        data_to_append[1] = encrypt(triple_strings[1])
        data_to_append[2] = encrypt(triple_strings[2])

        # print(data_to_append)
        hf[DS_NAME][-1] = data_to_append
        # hf[DS_NAME][-1] = [n.encode("ascii", "ignore") for n in triple_strings]
    print("Added %s values to database." % str(triple_strings))
    sleep(3)

def create_dataset():
    with h5py.File(HDF5_PATH, 'w') as hf:
        dset = hf.create_dataset(DS_NAME, (0, 3), maxshape=(None, 3), dtype='S1000', chunks=True)
    print("Database created.")

def delete_last_one():
    delete_ans = input("You sure you want to delete last added element? ")
    if delete_ans in ['Y', 'y']:
        with h5py.File(HDF5_PATH, mode='a') as hf:
            hf[DS_NAME].resize((hf[DS_NAME].shape[0] - 1, 3))
        print("Deleted.")
        sleep(2)

def find_by_prov_and_user():
    provider = input("Provider: ")
    user = input("User: ")

    found = False
    with h5py.File(HDF5_PATH, mode='a') as hf:
        dset = hf[DS_NAME]
        for i in range(dset.shape[0]):
            if dset[i][0] == provider.encode("ascii", "ignore") and decrypt(dset[i][1]) == user:
                print("\n" + provider + ":")
                print("user = " + decrypt(dset[i][1]))
                print("password = *********")

                pyperclip.copy(decrypt(dset[i][2]))
                print("Password copied to clipboard (if multiple found, copied the last one). ")
                reveal_ans = input("Reveal? ")
                if reveal_ans in ['Y', 'y']:
                    print(decrypt(dset[i][2]))

                found = True

    if not found:
        print("Sorry, couldn't find. Check the spelling, or try something else.")

    input()

def list_all():
    with h5py.File(HDF5_PATH, mode='a') as hf:
        dset = hf[DS_NAME]
        for row in dset:
            print(row[0].decode('utf-8') + ":")
            print("username = " + decrypt(row[1]))
            print("password = " + decrypt(row[2]))
            print("\n")
    input()

def change_password():
    provider = input("Provider: ")
    user = input("User: ")

    found = False
    with h5py.File(HDF5_PATH, mode='a') as hf:
        dset = hf[DS_NAME]
        for i in range(dset.shape[0]):
            if dset[i][0] == provider.encode("ascii", "ignore") and decrypt(dset[i][1]) == user:
                print("\n" + provider + ":")
                print("user = " + decrypt(dset[i][1]))
                print("password = *********")

                reveal_ans = input("Reveal old password? ")
                if reveal_ans in ['Y', 'y']:
                    print(decrypt(dset[i][2]))

                new_password = input("Input new password: ")
                dset[i][2] = encrypt(new_password)

                print("Password changed.")
                found = True

    if not found:
        print("Sorry, couldn't find. Check the spelling, or try something else.")

    sleep(3)

# TODO: maybe sort the database alphabetically
# TODO: maybe change password

def main():
    print("Hi. Are you @ephraim?")
    ephraim_password = getpass("")

    if ephraim_password == PASSWORD_TO_ACCESS_SCRIPT:
        while True:
            os.system('cls')
            print("###### ACCOUNTS MANAGER ######")
            print("Add new account")
            print("Search password")
            print("Delete last account added")
            print("List all accounts")
            print("Change password")
            print("##############################\n")

            answer = input("Choose one: ")
            if answer in ['a', 'A']:
                append_one()

            elif answer in ['S', 's']:
                # TODO: validation system other than password
                find_by_prov_and_user()

            elif answer in ['D', 'd']:
                delete_last_one()

            elif answer in ['L', 'l']:
                # TODO: validation system other than password
                list_all()

            elif answer in ['C', 'c']:
                # TODO: validation system other than password
                change_password()

            elif answer in ['RED', 'red']:
                # TODO: validation system other than password
                red_code_ans = input("Red code activated. You sure you want to delete all data and create a new database? ")

                if red_code_ans in ["Y", "y"]:
                    create_dataset()

            elif answer in ['X', 'x', 'q', 'Q']:
                quit_ans = input("You sure you want to quit? ")
                if quit_ans in ["Y", "y"]:
                    break
    else:
        print("Sorry, bye.")


if __name__ == '__main__':
    main()


# TODO: put this in secret (dependencies_) directory, and only work with exe.

# def main1():
    # create_dataset()
    # append_one(("yahoo", "user1", "pass1"))
    # append_one(("gmail", "user2", "pass2"))
    # append_one(("epc", "user3", "pass3"))
    # append_one(("league", "user4", "pax"))
    # list_all()
