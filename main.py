import os, json

class Inventory:
    def __init__(self):

        self.running = True
        self.data = []

        appdata = os.getenv("APPDATA")

        if appdata is None:
            appdata = os.path.expanduser("~")

        self.path = os.path.join(appdata, "Inventaire")
        self.file = os.path.join(self.path, "default.json")
        self.params = os.path.join(self.path, "params.json")

        os.makedirs(self.path, exist_ok=True)

        if not os.path.exists(self.file):
            with open(self.file, "w", encoding="utf-8") as f:
                json.dump([], f)

        if not os.path.exists(self.params):
            with open(self.params, "w", encoding="utf-8") as f:
                json.dump({"loading": "default.json"}, f)
        
        else:
            try:
                with open(self.params, "r", encoding="utf-8") as f:
                    params = json.load(f)
                    self.file = os.path.join(self.path, params.get("loading", "default.json"))

            except json.JSONDecodeError:
                print("Error: The params file is corrupted. Using default inventory file.")
                self.file = os.path.join(self.path, "default.json")

        try: 
            with open(self.file, "r", encoding="utf-8") as f:
                self.data = json.load(f)

            if not isinstance(self.data, list):
                print("Error: The inventory file is invalid. Starting with an empty inventory.")
                self.data = []

        except json.JSONDecodeError:
            print("Error: The inventory file is corrupted. Starting with an empty inventory.")
            self.data = []
        
        except FileNotFoundError:
            print("Error: File not found. Starting with an empty inventory.")
            self.data = []

        print(f"Welcome to the inventory management program.\nType 'help' for a list of commands.\nCurrent inventory file: {os.path.basename(self.file)}")

    def run(self) -> None:
        while self.running:

            user_input = input("> ")

            if not user_input:
                continue
            
            if user_input in {"quit", "q"}:

                self.running = False
                print("Saving and exiting the program.")
                self.update(self.file)

            elif user_input == "delete":

                for obj in os.listdir(self.path):
                    if obj.endswith(".json") and obj not in {"default.json", "params.json"}:
                        print(f"  {obj}")

                name = input(">Enter the name of the inventory file to delete: ")
                self.delete_file(name)
                
            elif user_input.startswith("d "):
                command = user_input[2:].strip()

                if command in {"all", "a"}:
                    confirm = input("are you sure you want to delete every app file? This action cannot be undone. (y/n)").lower()

                    if confirm != "y":
                        continue

                    sure = input("are you really sure ? This action cannot be undone. (y/n)").lower()

                    if sure != "y":
                        continue

                    try:
                        for obj in os.listdir(self.path):
                            os.remove(os.path.join(self.path, obj))

                        print(">Files succesfully deleted, exiting the app...")
                        self.running = False

                    except PermissionError:
                        print("Error: couldn't delete evert file, check your permission")

                elif command:
                    self.delete_file(command)

            elif user_input[0] in "+-":
                try:
                    value_str, item = user_input.split(maxsplit=1)
                except ValueError:
                    print(f"Invalid command format. Please use the format: {user_input[0]}<number> <item_name>")
                    continue

                value = self.convert(value_str)
                if not isinstance(value, (int, float)):
                    print(f"Error: Invalid quantity: {value_str}. Please enter a valid number.")
                    continue

                obj = self.find_item(item)
                if not obj:
                    print(f"Error: Item '{item}' not found.")
                    continue

                new_quantity = obj["quantity"] + value

                if new_quantity >= 0:
                    obj["quantity"] = new_quantity
                    self.update(self.file)
                    print(f"Item '{item}' updated. New quantity: {new_quantity}")
                else:
                    print("Error: Quantity cannot be negative.")

            elif user_input.startswith("n "):
                
                command = user_input[2:].strip().split(",")
                
                try:
                    self.add_item((command[0], command[1], command[2]))
                except IndexError:
                    print("Invalid command format. Please use the format: n item_name,tags,quantity")

            elif user_input == "new":
                name = input(">Enter the item name: ").lower()

                if any(obj["name"] == name for obj in self.data):
                    print("Item already exists.")
                    continue

                tags = input(">Enter the item tags (slash-separated): ")
                quantity = self.convert(input(">Enter the item quantity: "))

                if not isinstance(quantity, (int, float)):
                    print(f"Error: Invalid quantity: {quantity}. Please enter a valid number.")
                    continue

                self.add_item((name, tags, quantity))

            elif user_input == "edit":

                item_name = input(">Enter the item name to edit: ")

                obj = self.find_item(item_name)

                if not obj:
                    print(f"Error: Item '{item_name}' not found.")
                    continue

                new_tags = input(">Enter the new item tags (slash-separated): ")
                obj["tags"] = new_tags.lower()
                self.update(self.file)

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
                self.update(self.file   )

            elif user_input == "remove":

                item_name = input(">Enter the item name to remove: ")

                obj = self.find_item(item_name)
                if not obj:
                    print(f"Error: Item '{item_name}' not found.")
                    continue

                self.data.remove(obj)
                self.update(self.file)

            elif user_input.startswith("r "):

                command = user_input[2:].strip()
                if not command:
                    print("Invalid command format. Please use the format: r item_name")
                    continue

                obj = self.find_item(command)
                if not obj:
                    print(f"Error: Item '{command}' not found.")
                    continue

                self.data.remove(obj)
                self.update(self.file)
            
            elif user_input in {"help", "h"}:
                print("Help:")
                print("  help - Show this help message *")
                print("  new - Add a new item *")
                print("  edit - Edit an existing item tags *")
                print("  remove - Remove an existing item *")
                print("  quit - Quit the program")
                print("  +<number> <item_name> - Increase the quantity of an item")
                print("  -<number> <item_name> - Decrease the quantity of an item")
                print("  <item_name/tags> - Search for an item by name or tag")
                print("  all - Show all items")
                print("  current - Show the current inventory file")
                print("  switch - Switch to another inventory file *")
                print("  file - Create a new inventory file *")
                print("  delete - Delete an inventory file (cannot be undone), the 'all' argument delete every app files *")
                print("  all command with an asterisk (*) can be used with the first letter only using a comma-separated list of values instead of interactive input, for example: n item_name,tags,quantity")

            elif user_input in {"a", "all"}:

                for obj in self.data:
                    print(f"Item: {obj['name']}, Tags: {obj['tags']}, Quantity: {obj['quantity']}")
            
            elif user_input == "switch":

                for obj in os.listdir(self.path):
                    if obj.endswith(".json") and obj not in {"default.json", "params.json"}:
                        print(f"  {obj}")

                name = input(">Enter the name of the inventory file to switch to: ")
                self.switch(name)
            
            elif user_input.startswith("s "):
                command = user_input[2:].strip()
                if command:
                    self.switch(command)

            elif user_input in {"c", "current"}:
                print(f"Current inventory file: {os.path.basename(self.file)}")

            elif user_input == "file":
                name = input(">Enter the new file name: ")

                self.create_file(name)
            
            elif user_input.startswith("f "):
                command = user_input[2:].strip()
                if command:
                    self.create_file(command)
                else:
                    print("Error: Please provide a valid file name.")

            else:
                _input = self.find_item(user_input)

                if not _input:
                    count = 0
                    user_input = user_input.lower()

                    for obj in self.data:
                        if user_input in obj["tags"].split("/"):
                            print(f"Item: {obj['name']}, Tags: {obj['tags']}, Quantity: {obj['quantity']}")
                            count +=1

                    if count == 0:
                        print(f"Error: Item or tag '{user_input}' not found.")
                else:
                    print(f"Item: {_input['name']}, Tags: {_input['tags']}, Quantity: {_input['quantity']}")

    def add_item(self, item: tuple) -> None:
        """add an item to the inventory, either in detailed mode or with a tuple of values"""

        if item is None or len(item) != 3:
            print("Invalid item data. Please provide 3 parameters: name,tags,quantity).")
            return
        
        elif any(obj["name"] == item[0].lower() for obj in self.data):
            print("Item that name already exists.")
            return
        
        quantity = self.convert(item[2])

        if not isinstance(quantity, (int, float)):
            print(f"Error: Invalid quantity: {item[2]}. Please enter a valid number.")
            return
        if quantity < 0:
            print(f"Error: Invalid quantity: {item[2]}. Can't put negative quantity.")
            return  
        
        self.data.append({"name": item[0].lower(), "tags": item[1].lower(), "quantity": quantity})

        self.update(self.file)

    def convert(self, value: str) -> int|float|None:
        """convert a string to an int, float, or return None if conversion fails."""
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return None

    def update(self, file: str) -> None:
        """update the json file with the current inventory data."""
        try: 
            with open(file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4)
        except OSError:
            print(f"Error: Couldn't save {os.path.basename(file)}")

    def find_item(self, name: str) -> dict|None:
        """find an item by name"""
        name = name.lower()

        for obj in self.data:
            if obj["name"] == name:
                return obj
            
        return None
    
    def switch(self, name: str) -> None:
        """switch to the selected file"""

        if not self.check_name(name):
            return
        
        selected = name if name.endswith(".json") else f"{name}.json"

        if name == "params":
            print("Error: can't switch to the parameter file")
            return

        try:
            self.update(self.file)
            with open(os.path.join(self.path, selected), "r", encoding="utf-8") as f:

                self.data = json.load(f)

                if not isinstance(self.data, list):
                    print("Error: The inventory file is invalid. Opening an empty inventory.")
                    self.data = []
                    return

                self.file = os.path.join(self.path, selected)

                with open(self.params, "w", encoding="utf-8") as f:
                    json.dump({"loading": selected}, f)
                print(f"Switched to inventory file: {name}.")

        except FileNotFoundError:
            print(f"Error: Inventory file '{name}' not found.")

        except json.JSONDecodeError:
            print(f"Error: Inventory file '{name}' is corrupted, couldn't switch to it.")

    def delete_file(self, name: str) -> None:
        """delete the file with given name"""

        if not self.check_name(name):
            return

        selected = os.path.join(self.path, f"{name}.json")

        confirm = input("are you sure you want to delete the inventory file? This action cannot be undone. (y/n)").lower()

        if confirm != "y":
            print("Deletion cancelled.")
            return

        if name.lower() in {"default", "params"}:
            print("Error: can't delete the default/params file, try another one.")
            return

        try:
            if selected == self.file:
                self.switch("default")
                os.remove(selected)
                print("Current inventory file deleted. Switching to default")
                return

            os.remove(selected)
            print("Inventory file deleted")

        except PermissionError:
            print("Error: Failed to delete the inventory file. Please check your permissions.")
        
        except FileNotFoundError:
            print(f"Error: Couldn't find the inventory file {name}, please try again.")

    def create_file(self, name: str) -> None:
        """create a json file with given name"""

        if not self.check_name(name):
            return

        path = os.path.join(self.path, f"{name}.json")

        if os.path.exists(path):
            print("Error: file that name already exists.")
            return

        print(f"creating new inventory file {name}...")

        with open(path, "w", encoding="utf-8") as f:
            json.dump([], f)

        if os.path.exists(path):
            print("File succesfully created.")
        else:
            print("Error: the file couldn't be created.")
    
    def check_name(self, name:str) -> bool:
        """check a file name"""
        for char in "/\\:*\"<>|":
            if char in name:
                print("Error: Invalid file name (can't contain: /\\:*\"<>|)")
                return False
            
        return True
        
if __name__ == "__main__":
    app = Inventory()
    app.run()