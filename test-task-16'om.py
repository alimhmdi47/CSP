from itertools import permutations
from random import choice
from typing import List

class Product:
    def __init__(self, name: str, category: str, length: int, width: int, height: int, weight: float, incompatible_with: List[str], is_breakable: bool):
        self.name = name
        self.category = category
        self.length = length
        self.width = width 
        self.height = height
        self.dimensions = sorted((length, width, height))  # Sort dimensions (smallest to largest)
        self.volume = length * width * height
        self.weight = weight
        self.incompatible_with = set(incompatible_with)
        self.is_breakable = is_breakable
        self.placed = False

    def __repr__(self) -> str:
        return (
            f"Product name: {self.name}, Category: {self.category},"
            f"Volume: {self.volume}, Weight: {self.weight}"
        )

class Box:
    def __init__(self, name: str, length: int, width: int, height: int, max_weight: float, priority: int):
        self.name = name
        self.length = length
        self.width = width 
        self.height = height
        self.dimensions = sorted((length, width, height))  # Sort dimensions (smallest to largest)
        self.volume = length * width * height
        self.remaining_volume = self.volume
        self.max_weight = max_weight
        self.remaining_weight = max_weight
        self.products: List[Product] = []
        self.contains_categories = set()
        self.contains_non_breakable = False
        self.priority = priority

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
            f"{self.name} : {"Not Breakalbe" if self.contains_non_breakable else "Breakable"} | "
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
                    and box.max_weight >= product.weight
                ):
                    new_box = Box(box.name, box.length, box.width , box.height , box.max_weight , box.priority)
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
                box.max_weight - box.remaining_weight
            ) <= box_type.max_weight:

                box.name = box_type.name
        boxes.append(box)

    final_boxes = sorted(boxes, key=lambda x: x.priority)
    return final_boxes

class BinPack():
    def __init__(self,box:Box,products:List[Product]):
        self.box = box
        self.products = products
        self.placement = []
        self.unplaced = []
        self.current_weight = 0
        
    def rotations(self,product:Product):
      return list(set(permutations(product.dimensions, 3)))
    def can_place(self, x, y, z, dim, weight) -> bool:
        if self.current_weight + weight > self.box.max_weight:
            return False
        if (x + dim[0] > self.box.dimensions[0] or
            y + dim[1] > self.box.dimensions[1] or
            z + dim[2] > self.box.dimensions[2]):
            return False
        return True
    def pack(self):
        self.unplaced.clear()
        items_sorted = sorted(self.products, key=lambda it: it.volume, reverse=True)
        for item in items_sorted:
            placed = False
            for rot in self.rotations(item):
                if self.can_place(0,0,0, rot, item.weight):
                    self.placement.append((item))
                    self.current_weight += item.weight
                    placed = True
                    break
            if not placed:
                self.unplaced.append(item)
    
products = [
    Product("Fridge Magnet", "Magnet", 5, 5, 2, 0.1, [], False),
    Product("Over weight", "Over", 30, 30, 30, 500, [], False),
    Product("Bluetooth Speaker", "Electronics", 20, 15, 2, 1.0, [], True),
    Product("Tablet", "Electronics", 25, 18, 1, 0.8, [], True),
    Product("Toilet Cleaner", "Detergent", 25, 15, 15, 1.7, [], False),
    Product("Toilet Cleaner", "Detergent", 25, 15, 15, 1.7, [], False),
    Product("Digital Camera", "Electronics", 15, 10, 3, 0.9, [], True),
    Product("Smartwatch", "Electronics", 10, 10, 2, 0.3, [], True),
    Product("Tomato Sauce", "Food", 25, 10, 10, 0.9, [], True),
    Product("Chocolate", "Food", 15, 10, 2, 0.2, [], False),
    Product("Industrial Magnet", "Magnet", 20, 20, 20, 5.0, [], False),
    Product("Toilet Cleaner", "Detergent", 25, 15, 15, 1.7, [], False),
    Product("E-Reader", "Electronics", 20, 12, 1, 0.5, [], True),
    Product("Industrial Magnet", "Magnet", 20, 20, 20, 5.0, [], False),
    Product("Cheese", "Food", 20, 15, 3, 0.5, [], False),
    Product("Magnetic Toy", "Magnet", 15, 10, 5, 0.5, [], False),
    Product("Laptop", "Electronics", 30, 20, 2, 2.5, [], True),
    Product("Bluetooth Speaker", "Electronics", 20, 15, 2, 1.0, [], True),
    Product("Crystal Bowl", "Glassware", 25, 25, 20, 1.8, [], True),
    Product("Laundry Detergent", "Detergent", 30, 20, 20, 2.0, [], False),
    Product("Crystal Bowl", "Glassware", 25, 25, 20, 1.8, [], True),
    Product("All incompatible Not Breakable", "Incompatible", 20, 20, 20, 3.0, ["Food", "Electronics", "Magnet", "Detergent"], False),
    Product("Chocolate", "Food", 15, 10, 2, 0.2, [], False),
    Product("E-Reader", "Electronics", 20, 12, 1, 0.5, [], True),
    Product("Fridge Magnet", "Magnet", 5, 5, 2, 0.1, [], False),
    Product("Over size", "Over", 800000, 800, 800, 5.0, [], False),
    Product("Digital Camera", "Electronics", 15, 10, 3, 0.9, [], True),
    Product("Laundry Detergent", "Detergent", 30, 20, 20, 2.0, [], False),
    Product("Chocolate", "Food", 15, 10, 2, 0.2, [], False),
    Product("Pasta", "Food", 20, 15, 5, 0.4, [], False),
    Product("Mirror", "Glassware", 50, 40, 2, 3.0, [], True),
    Product("Honey", "Food", 25, 10, 10, 1.2, [], True),
    Product("Tomato Sauce", "Food", 25, 10, 10, 0.9, [], True),
    Product("Laptop", "Electronics", 30, 20, 2, 2.5, [], True),
    Product("Toilet Cleaner", "Detergent", 25, 15, 15, 1.7, [], False),
    Product("Magnetic Hooks", "Magnet", 15, 10, 3, 0.4, [], False),
    Product("Olive Oil", "Food", 30, 10, 10, 1.0, [], True),
    Product("Digital Camera", "Electronics", 15, 10, 3, 0.9, [], True),
    Product("Tomato Sauce", "Food", 25, 10, 10, 0.9, [], True),
    Product("Over size", "Over", 800000, 800, 800, 5.0, [], False),
    Product("All incompatible Breakable", "Incompatible", 20, 20, 20, 3.0, ["Food", "Electronics", "Magnet", "Detergent"], True),
    Product("All incompatible Breakable", "Incompatible", 20, 20, 20, 3.0, ["Food", "Electronics", "Magnet", "Detergent"], True),
    Product("Magnet Strip", "Magnet", 20, 5, 2, 0.3, [], False),
    Product("Glass Vase", "Glassware", 30, 20, 30, 2.5, [], True),
    Product("Mirror", "Glassware", 50, 40, 2, 3.0, [], True),
    Product("All incompatible Breakable", "Incompatible", 20, 20, 20, 3.0, ["Food", "Electronics", "Magnet", "Detergent"], True),
    Product("Magnetic Hooks", "Magnet", 15, 10, 3, 0.4, [], False),
    Product("Honey", "Food", 25, 10, 10, 1.2, [], True),
    Product("Smartwatch", "Electronics", 10, 10, 2, 0.3, [], True),
    Product("Honey", "Food", 25, 10, 10, 1.2, [], True),
    Product("Olive Oil", "Food", 30, 10, 10, 1.0, [], True),
]

box_sizes = [
    Box("XLarge Box", 700, 700, 700, 15, 1),
    Box("Large Box", 500, 500, 500, 10, 2),
    Box("Medium Box", 300, 300, 300, 5, 3),
    Box("Small Box", 200, 200, 200, 2, 4),
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
    
for box in all_boxes:
    packer = BinPack(box, box.products)
    packer.pack()
