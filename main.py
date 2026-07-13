import os, json, difflib

class Inventory:
    def __init__(self):

        self.running = True

        appdata = os.getenv("APPDATA")

        if appdata is None:
            appdata = os.path.expanduser("~")

        self.path = os.path.join(appdata, "Inventaire")
        self.file = os.path.join(self.path, "inventaire.json")

        if not os.path.exists(self.path):
            os.makedirs(self.path)

        if not os.path.exists(self.file):

            with open(self.file, "w") as f:
                json.dump([], f)

        with open(self.file, "r") as f:
            try:
                self.data = json.load(f)
            except json.JSONDecodeError:
                print("Error: The inventory file is corrupted. Starting with an empty inventory.")
                self.data = []

        print("Welcome to the inventory management program.\n Type 'help' for a list of commands.")

    def run(self) -> None:
        while self.running:

            user_input = input("> ").lower()

            if not user_input:
                continue
            
            if user_input in {"exit", "e"}:

                self.running = False
                print("Saving and exiting the program.")
                self.update()

            elif user_input in {"delete", "d"}:
                confirm = input("are you sure you want to delete the inventory file? This action cannot be undone. (y/n)").lower()

                if confirm != "y":
                    print("Deletion cancelled.")
                    continue

                try:
                    os.remove(self.file)
                    os.rmdir(self.path)
                except:
                    print("Failed to delete the inventory file. Please check your permissions.")
                    
                else:
                    print("Inventory file deleted. Exiting the program.")
                    self.running = False

            elif user_input[0] in "+-":
                try:
                    value_str, item = user_input.split(maxsplit=1)
                except ValueError:
                    print(f"Invalid command format. Please use the format: {user_input[0]}<number> <item_name>")
                    continue

                value = self.convert(value_str)
                if not isinstance(value, (int, float)):
                    print(f"Invalid quantity: {value_str}. Please enter a valid number.")
                    continue

                obj = self.find_item(item)
                if not obj:
                    print(f"Error: Item '{item}' not found.")
                    continue

                new_quantity = obj["quantity"] + value

                if new_quantity >= 0:
                    obj["quantity"] = new_quantity
                    self.update()
                    print(f"Item '{item}' updated. New quantity: {new_quantity}")
                else:
                    print("Error: Quantity cannot be negative.")

            elif user_input.startswith("n "):
                
                command = user_input[2:].strip().split(",")
                try:
                    self.add_item(False, (command[0], command[1], command[2]))
                except:
                    print("Invalid command format. Please use the format: n item_name,tags,quantity")

            elif user_input == "new":
                self.add_item(True)

            elif user_input == "edit":

                item_name = input(">Enter the item name to edit: ")

                obj = self.find_item(item_name)

                if not obj:
                    print(f"Error: Item '{item_name}' not found.")
                    continue

                new_tags = input(">Enter the new item tags (slash-separated): ")
                obj["tags"] = new_tags.lower()
                self.update()

            elif user_input.startswith("e "):
                command = user_input[2:].strip().split(",")
                try:
                    item_name = command[0]
                    new_tags = command[1]
                except IndexError:
                    print("Invalid command format. Please use the format: e item_name,new_tags")
                    continue

                obj = self.find_item(item_name)

                if not obj:
                    print(f"Error: Item '{item_name}' not found.")
                    continue

                obj["tags"] = new_tags
                self.update()

            elif user_input == "remove":

                item_name = input(">Enter the item name to remove: ")

                obj = self.find_item(item_name)
                if not obj:
                    print(f"Error: Item '{item_name}' not found.")
                    continue

                self.data.remove(obj)
                self.update()

            elif user_input.startswith("r "):

                command = user_input[1:].strip()
                if not command:
                    print("Invalid command format. Please use the format: r item_name")
                    continue

                obj = self.find_item(command)
                if not obj:
                    print(f"Error: Item '{command}' not found.")
                    continue

                self.data.remove(obj)
                self.update()
            
            elif user_input in {"help", "h"}:
                print("Help:")
                print("  help - Show this help message *")
                print("  new - Add a new item *")
                print("  edit - Edit an existing item tags *")
                print("  remove - Remove an existing item *")
                print("  exit - Exit the program")
                print("  +<number> <item_name> - Increase the quantity of an item")
                print("  -<number> <item_name> - Decrease the quantity of an item")
                print("  <item_name/tags> - Search for an item by name or tag")
                print("  all - Show all items")
                print("  delete - Delete the inventory file (cannot be undone)")
                print("  all command with an asterisk (*) can be used with the first letter only using a comma-separated list of values instead of interactive input, for example: n item_name,tags,quantity")

            elif user_input in {"a", "all"}:

                for obj in self.data:
                    print(f"Item: {obj['name']}, Tags: {obj['tags']}, Quantity: {obj['quantity']}")

            else:
                for obj in self.data:
                    if user_input in obj["name"] or user_input in obj["tags"]:
                        print(f"Item: {obj['name']}, Tags: {obj['tags']}, Quantity: {obj['quantity']}")

    def add_item(self, detailed: bool = False, item: tuple|None = None) -> None:
        """add an item to the inventory, either in detailed mode or with a tuple of values"""

        if detailed:
            name = input(">Enter the item name: ")

            if any(obj["name"] == name for obj in self.data):
                print("Item already exists.")
                return

            tags = input(">Enter the item tags (slash-separated): ")
            quantity = self.convert(input(">Enter the item quantity: "))

            if not isinstance(quantity, (int, float)):
                print(f"Invalid quantity: {quantity}. Please enter a valid number.")
                return
            
            self.data.append({"name": name.lower(), "tags": tags.lower(), "quantity": quantity})

        else:

            if item is None or len(item) != 3:
                print("Invalid item data. Please provide 3 parameters: name,tags,quantity).")
                return
            elif any(obj["name"] == item[0] for obj in self.data):
                print("Item already exists.")
                return
            quantity = self.convert(item[2])

            if not isinstance(quantity, (int, float)):
                print(f"Invalid quantity: {item[2]}. Please enter a valid number.")
                return
            
            self.data.append({"name": item[0].lower(), "tags": item[1].lower(), "quantity": quantity})

        self.update()

    def convert(self, value: str) -> int|float|str:
        """convert a string to an int, float, or return the string if conversion fails."""
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            return value

    def update(self) -> None:
        """update the json file with the current inventory data."""
        with open(self.file, "w") as f:
            json.dump(self.data, f, indent=4)

    def find_item(self, name: str) -> dict|None:
        """find an item by name using fuzzy matching."""
        items = {obj["name"]: obj for obj in self.data}
        match = difflib.get_close_matches(name, items.keys(), n=1, cutoff=0.6)

        if not match:
            return None

        return items[match[0]]

if __name__ == "__main__":
    app = Inventory()
    app.run()