from termcolor import colored

def print_cool_colors(option):
    if option == 1:
        print(colored("Hey, I am your AI assistant that can answer any questions you have about anything you've said today.", "red"))
        print(colored("Please give me a few seconds to get set up...", "blue"))

        # function that starts the QA

    elif option == 2:
        print(colored("Here are all the data that we have about you", "green"))
        print(colored("Please give me a few seconds to get set up...", "blue"))

        # function that queries through the whole database and fetches_all

    elif option == 3:
        print(colored("Option 3: Recording Started", "yellow"))
        print(colored("Please give me a few seconds to get set up...", "blue"))

        #function to the start the whole recording proccess

    else:
        print(colored("Invalid option, input numbers only from 1-3.", "red"))

def main():
    print("Welcome to your second brain! This program runs throughout, here are your current options")
    print(colored("Option 1: Ask questions to your brain database right now:", "red"))
    print(colored("Option 2: See your brain database", "green"))
    print(colored("Option 3: Start Recording", "yellow"))
    # print(colored("Option 4: Blue", "blue"))

    try:
        user_input = int(input("Enter your choice: "))
        print_cool_colors(user_input)
    except ValueError:
        print(colored("Invalid option. Please enter a number between 1 and 4.", "red"))

if __name__ == "__main__":
    main()
