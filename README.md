# Inventory-app
a basic console app to manage inventories 

## Command List
the action list is :
- help - Show this help message *
- new - Add a new item *
- edit - Edit an existing item tags *
- remove - Remove an existing item *
- quit - Quit the program
- +<number> <item_name> - Increase the quantity of an item
- -<number> <item_name> - Decrease the quantity of an item
- <item_name/tags> - Search for an item by name or tag
- all - Show all items
- current - Show the current inventory file
- switch - Switch to another inventory file *
- file - Create a new inventory file *
- delete - Delete an inventory file (cannot be undone), the 'all' argument delete every app files *
- all command with an asterisk (*) can be used with the first letter only using a comma-separated list of values instead of interactive input, for example: n item_name,tags,quantity
