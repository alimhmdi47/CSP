from random import choice

class Product:
    def __init__(
        self,
        name: str,
        category: str,
        length: int,
        width: int,
        height: int,
        weight: float,
        incompatible_with: list[str],
        is_breakable: bool,
    ):

        self.name = name
        self.category = category
        self.length = length
        self.width = width
        self.height = height
        self.volume = self.calculate_volume()
        self.weight = weight
        self.incompatible_with = incompatible_with
        self.is_breakable = is_breakable

    def calculate_volume(self) -> int:
        return self.length * self.width * self.height
    
    def __repr__(self) -> str:
        return (
            f"Product name: {self.name}, Category: {self.category},"
            f"Volume: {self.volume}, Weight: {self.weight}"
        )


class Box:
    def __init__(self,
                 box_type: str,
                 volume: int,
                 weight_capacity: int, number:int):

        self.box_type = box_type
        self.volume = volume
        self.weight_capacity = weight_capacity
        self.remaining_volume = volume
        self.remaining_weight = weight_capacity
        self.products = []
        self.contains_categories = set()
        self.contains_non_breakable = False
        self.number = number

    def can_fit(self, product):
        if (
            self.remaining_volume < product.volume
            or self.remaining_weight < product.weight
        ):
            return False

        if product.is_breakable and self.contains_non_breakable:
            return False

        if not product.is_breakable and any(
            box_products.is_breakable for box_products in self.products
        ):
            return False

        for existing_product in self.products:
            if (
                existing_product.category in product.incompatible_with
                or product.category in existing_product.incompatible_with
            ):
                return False
            
        return True

    def add_product(self, product):
        self.products.append(product)
        self.contains_categories.add(product.category) 
        
        self.remaining_volume -= product.volume
        self.remaining_weight -= product.weight
        
        if not product.is_breakable:
            self.contains_non_breakable = True

    def __repr__(self):
        product_names = [product.name for product in self.products]
        return (
            f"{self.box_type} : {"Not Breakalbe" if self.contains_non_breakable else "Breakable"} | "
            f"Categories: {self.contains_categories} \n"
            f"Products: {product_names} \n"
            f"Free Volume: {self.remaining_volume}, Free Weight: {self.remaining_weight} \n"
            "----------"
    )

def set_constraint(products):
    products_with_constraint = []
    for product in products:
        product.incompatible_with = constraint.get(product.category , product.incompatible_with)
        products_with_constraint.append(product)
    return products_with_constraint

def pack_products(products, box_sizes):
    products = sorted(products, key=lambda x: (x.weight, x.volume), reverse=True)

    boxes = []
    remaining_products = []
    
    for product in products:
        placed = False
        
        for box in boxes:
            if box.can_fit(product):
                box.add_product(product)
                placed = True
                break
            
        if not placed:
            for box in box_sizes:
                if (
                    box.volume >= product.volume
                    and box.weight_capacity >= product.weight
                ):
                    new_box = Box(box.box_type, box.volume, box.weight_capacity, box.number)
                    new_box.add_product(product)
                    boxes.append(new_box)
                    break
                
                else:
                    remaining_products.append(product)
                    break
                
    return boxes, remaining_products

def modifid_boxes(packed_boxes):
    boxes = []
    for box in packed_boxes:
        for box_type in box_sizes[1:]:
            if (box.volume - box.remaining_volume) <= box_type.volume and (
                box.weight_capacity - box.remaining_weight
            ) <= box_type.weight_capacity:

                box.box_type = box_type.box_type
        boxes.append(box)

    final_boxes = sorted(boxes, key=lambda x: x.number)
    return final_boxes


products_base = [
    # Electronics
    Product("Laptop", "Electronics", 750, 2.5, [], True),
    Product("Tablet", "Electronics", 600, 0.8, [], True),
    Product("Bluetooth Speaker", "Electronics", 500, 1.0, [], True),
    Product("Digital Camera", "Electronics", 400, 0.9, [], True),
    Product("E-Reader", "Electronics", 350, 0.5, [], True),
    Product("Smartwatch", "Electronics", 200, 0.3, [], True),
    # Food
    Product("Chocolate", "Food", 300, 0.2, [], False),
    Product("Cheese", "Food", 500, 0.5, [], False),
    Product("Olive Oil", "Food", 800, 1.0, [], True),
    Product("Tomato Sauce", "Food", 700, 0.9, [], True),
    Product("Pasta", "Food", 400, 0.4, [], False),
    Product("Honey", "Food", 750, 1.2, [], True),
    # Detergent
    Product("Laundry Detergent", "Detergent", 1200, 2.0, [], False),
    Product("Dish Soap", "Detergent", 900, 1.5, [], False),
    Product("Bleach", "Detergent", 1000, 2.0, [], False),
    Product("Glass Cleaner", "Detergent", 600, 1.0, [], False),
    Product("Toilet Cleaner", "Detergent", 800, 1.7, [], False),
    # Glassware
    Product("Wine Glass", "Glassware", 400, 0.3, [], True),
    Product("Glass Vase", "Glassware", 1500, 2.5, [], True),
    Product("Mirror", "Glassware", 2000, 3.0, [], True),
    Product("Glass Jar", "Glassware", 800, 1.0, [], True),
    Product("Crystal Bowl", "Glassware", 1200, 1.8, [], True),
    # Magnet
    Product("Fridge Magnet", "Magnet", 100, 0.1, [], False),
    Product("Industrial Magnet", "Magnet", 800, 5.0, [], False),
    Product("Magnetic Toy", "Magnet", 300, 0.5, [], False),
    Product("Magnet Strip", "Magnet", 400, 0.3, [], False),
    Product("Magnetic Hooks", "Magnet", 350, 0.4, [], False),
    # Over size and weight
    Product("Over size", "Over", 10000, 5, [], False),
    Product("Over weight", "Over", 500, 30, [], False),
    # Incomapible with all
    Product(
        "All incompatible Not Breakalbe",
        "Incomapatible",
        500,
        3,
        ["Food", "Electronics", "Magnet", "Detergent"],
        False,
    ),
    Product(
        "All incompatible Breakable",
        "Incomapatible",
        500,
        3,
        ["Food", "Electronics", "Magnet", "Detergent"],
        True,
    ),

]

products = [choice(products_base) for _ in range(100)] 

box_sizes = [
    Box("XLarge Box", 7000, 15, 1),
    Box("Large Box", 5000, 10, 2),
    Box("Medium Box", 1500, 5, 3),
    Box("Small Box", 1000, 2, 4),
]

constraint = {
    "Food" : ["Detergent"],
    "Detergent" : ["Food"],
    "Electronics" : ["Magnet"],
    "Magnet" : ["Electronics"],
    "Glassware" : [],
}

products = set_constraint(products)
packed_boxes, remaining_product = pack_products(products, box_sizes)
all_boxes = modifid_boxes(packed_boxes)

print("#########")
print("-- Boxes:")

for i, box in enumerate(all_boxes):
    print(f"Box {i+1}: {box}")

print("-- Remaining products:")
for i, product in enumerate(remaining_product):
    print(f"{i+1}:{product}")
