import random

suits = ('Hearts','Diamonds','Spades','Clubs')
ranks = ('Two','Three','Four','Five','Six','Seven','Eight','Nine','Ten','Jack','Queen','King','Ace')
values = {'Two':2, 'Three':3, 'Four':4, 'Five':5, 'Six':6, 'Seven':7, 'Eight':8,
          'Nine':9, 'Ten':10, 'Jack':10, 'Queen':10, 'King':10, 'Ace':11}


# CARD class
class Card:

    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        self.value = values[rank]

    def __str__(self):
        return f"{self.rank} of {self.suit}"


#DECK class
class Deck:

    def __init__(self):
        self.all_cards = []

        for suit in suits:
            for rank in ranks:
                createdCard = Card(suit, rank)
                self.all_cards.append(createdCard)

    def shuffle(self):
        random.shuffle(self.all_cards)

    def deal_card(self):
        return self.all_cards.pop()


#PLAYER class

class Player:

    '''
    #keep track of player's hand-card they have
    #allow player to hit (draw a card)
    #allow player to stand (end their turn)
    #keep track of player's money - betting system
    #show the player's current hand
    '''

    def __init__(self):
        self.hand = []
        self.chips = Chip()
        self.standing = False

    def hit(self,deck):
        card = deck.deal_card()
        self.hand.append(card)

    def stand(self):
        self.standing = True

    def show_hand(self):
        print("\nYour hand:")
        for card in self.hand:
            print(card)

    def calculate_hand_value(self):
        total_value = 0
        ace_count = 0

        for card in self.hand:
            total_value += card.value
            if card.rank == "Ace":
                ace_count += 1

        while total_value > 21 and ace_count > 0:
            total_value -= 10
            ace_count -= 1

        return total_value


#CHIP class
class Chip:
    def __init__(self):
        self.balance = self.load_balance()
        self.bet = 0  # Start with no bet placed

    def load_balance(self):
        """Loads balance from file or starts at 100 if no file exists."""
        try:
            with open("chips.txt", "r") as f:
                return int(f.read().strip())
        except FileNotFoundError:
            return 100  # Default balance if file is missing

    def save_balance(self):
        """Saves current balance to file."""
        with open("chips.txt", "w") as f:
            f.write(str(self.balance))

    def place_bet(self):
        """Prompt the user to enter a bet and validate it."""
        while True:
            try:
                amount = int(input(f"Enter your bet amount (Balance: {self.balance}): "))
                if amount > self.balance:
                    print("Not enough balance! Enter a lower amount.")
                elif amount <= 0:
                    print("Bet amount must be greater than zero.")
                else:
                    self.balance -= amount
                    self.save_balance()  # Save new balance after betting
                    self.bet = amount  # Store the bet amount
                    return
            except ValueError:
                print("Invalid input! Please enter a valid number.")

    def win_bet(self):
        self.balance += self.bet * 2
        self.save_balance()  # Save after winning

    def lose_bet(self):
        self.balance -= self.bet
        self.save_balance()  # Save after losing

    def check_balance(self):
        """Checks if the balance is 0 and allows the user to top up."""
        if self.balance == 0:
            while True:
                try:
                    top_up = int(input("Your balance is 0! Enter an amount to top up: "))
                    if top_up > 0:
                        self.balance += top_up
                        print(f"Your new balance is {self.balance}")
                        break
                    else:
                        print("Amount must be greater than zero!")
                except ValueError:
                    print("Invalid input! Enter a valid number.")

    def __str__(self):
        return f"My balance now is: {self.balance}"


def dealer_turn(deck, dealer_hand):
    """Handles the dealer's turn and returns the final total."""
    dealer_total = sum(card.value for card in dealer_hand)
    ace_count = sum(1 for card in dealer_hand if card.rank == "Ace")

    while dealer_total > 21 and ace_count:
        dealer_total -= 10
        ace_count -= 1

    while dealer_total < 17:
        new_card = deck.deal_card()
        dealer_hand.append(new_card)
        dealer_total += new_card.value
        if new_card.rank == "Ace":
            ace_count += 1

        # Recalculate for aces
        while dealer_total > 21 and ace_count:
            dealer_total -= 10
            ace_count -= 1

    print("\nDealer's final hand:")
    for card in dealer_hand:
        print(card)
    print(f"Dealer's total: {dealer_total}")

    return dealer_total


def play_round(playerChip):
    """Plays one round of Blackjack."""
    global game_on  # You need to ensure `game_on` is correctly referenced

    # Check if balance is 0 and allow top-up
    playerChip.check_balance()

    # Betting
    playerChip.place_bet()  # ✅ Fixed: No argument needed

    new_deck = Deck()
    new_deck.shuffle()

    player_one = Player()  # Create a player instance
    dealer_hand = [new_deck.deal_card(), new_deck.deal_card()]

    player_one.hit(new_deck)
    player_one.hit(new_deck)

    player_one.show_hand()
    total = player_one.calculate_hand_value()

    if total == 21:
        print("Blackjack! You win!")
        playerChip.win_bet()
        return

    print("\nDealer's Visible Card:")
    print(dealer_hand[0])
    print("XXXXXXXXXXXXXXX")
    print(f"\nYour current total point is: {total}")

    # Player's turn
    while total < 21:
        choice = input("\nChoose to Hit or Stand (H/S): ").strip().lower()
        if choice == "h":
            player_one.hit(new_deck)
            player_one.show_hand()
            total = player_one.calculate_hand_value()
            print(f"\nYour current total point is: {total}")
            if total > 21:
                print("Bust! You lose this round.")
                playerChip.save_balance()  # Save balance after a loss
                return
        elif choice == "s":
            break

    # Dealer's turn
    dealer_total = dealer_turn(new_deck, dealer_hand)

    # Determine winner
    if dealer_total > 21 or total > dealer_total:
        print("You win!")
        playerChip.win_bet()
    elif dealer_total == total:
        print("It's a draw!")
        playerChip.balance += playerChip.bet  # Refund bet
    else:
        print("Dealer wins!")
        playerChip.win_bet()

    # Save balance after each round
    playerChip.save_balance()


# Main game loop

game_on = True
playerChip = Chip()  # Create a single Chip instance

while game_on:
    if playerChip.balance == 0:  # Check if balance is empty before placing a bet
        print("Your balance is 0. You need to add more chips to continue playing.")
        try:
            add_amount = int(input("Enter amount to top up: "))
            if add_amount > 0:
                playerChip.balance += add_amount
                playerChip.save_balance()
                print(f"Balance updated: {playerChip.balance}")
            else:
                print("Invalid amount! Please enter a positive number.")
                continue  # Retry top-up
        except ValueError:
            print("Invalid input! Please enter a number.")
            continue

    play_round(playerChip)

    print(f"Your current balance: {playerChip.balance}")
    again = input("\nDo you want to play again? (Y/N): ").strip().lower()
    if again != "y":
        game_on = False
        print("Thanks for playing!")



