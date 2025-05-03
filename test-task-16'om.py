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
            f"Product name: {self.name},"
            f"Category: {self.category},"
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
        
    def __repr__(self):
        product_names = [product.name for product in self.products]
        return (
            f"{self.name} : {"Not Breakalbe" if self.contains_non_breakable else "Breakable"} | "
            f"Categories: {self.contains_categories} \n"
            f"Products: {product_names} \n"
            f"Free Volume: {self.remaining_volume}, Free Weight: {self.remaining_weight} \n"
            "----------"
    )

class BinPack():
    def __init__(self,box:Box,products:List[Product]):
        self.box = box
        self.products = products
        self.placement = []
        self.unplaced = []
        self.current_weight = 0
        self.available_positions = set([(0, 0, 0)])

    def rotations(self,product:Product):
      return list(set(permutations(product.dimensions, 3)))
    
    def intersects(self, p1, p2) -> bool:
        x1, y1, z1, d1 = p1[1], p1[2], p1[3], p1[4]
        x2, y2, z2, d2 = p2[1], p2[2], p2[3], p2[4]
        return not (
            x1 + d1[0] <= x2 or x2 + d2[0] <= x1 or
            y1 + d1[1] <= y2 or y2 + d2[1] <= y1 or
            z1 + d1[2] <= z2 or z2 + d2[2] <= z1
        )
    def can_place(self, x, y, z, dim, weight) -> bool:
        if self.current_weight + weight > self.box.max_weight:
            return False
        if (x + dim[0] > self.box.dimensions[0] or
            y + dim[1] > self.box.dimensions[1] or
            z + dim[2] > self.box.dimensions[2]):
            return False
        new_placement = (None, x, y, z, dim)
        for placed in self.placement:
            if self.intersects(new_placement, placed):
                return False
        return True
    
    def place_item(self, item:Product, pos, dim):
        self.placement.append((item, pos[0], pos[1], pos[2], dim))
        self.current_weight += item.weight
        self.update_available_positions(pos, dim)
    
    def update_available_positions(self, pos, dim):
        x, y, z = pos
        l, w, h = dim
        self.available_positions.remove(pos)
        new_points = [
            (x + l, y, z),
            (x, y + w, z),
            (x, y, z + h),
            (x + l, y + w, z),
            (x + l, y, z + h),
            (x + l, y + w, z + h),
            (x, y + w, z + h)
        ]
        for point in new_points:
            if point not in self.available_positions:
                self.available_positions.add(point)
   
    def pack(self):
        self.unplaced.clear()
        items_sorted = sorted(self.products, key=lambda it: it.volume, reverse=True)
        for item in items_sorted:
            placed = False
            for pos in sorted(self.available_positions, key=lambda p: (p[2], p[1], p[0])):
                for rot in self.rotations(item):
                    if self.can_place(pos[0], pos[1], pos[2], rot, item.weight):
                        self.place_item(item, pos, rot)
                        placed = True
                        break
                if placed:
                    break
            if not placed:
                self.unplaced.append(item)
    
def set_constraint(products):
    products_with_constraint = []
    for product in products:
        product.incompatible_with = constraint.get(product.category , product.incompatible_with)
        products_with_constraint.append(product)
    return products_with_constraint

def categorize(products):
    products = sorted(products , key = lambda x: x.category)
    products_category_data = {}
    breakable = {}
    non_breakable = {}
    breakable_products = {}
    non_breakable_products = {}
    
    for product in products:
        if product.category in products_category_data:
            products_category_data[product.category] += 1
        else:
            products_category_data[product.category] = 1
            breakable[product.category] = 0
            non_breakable[product.category] = 0
            breakable_products[product.category] = []
            non_breakable_products[product.category] = []
            
        if product.is_breakable:
            breakable[product.category] += 1
            breakable_products[product.category].append(product)
        else:
            non_breakable[product.category] += 1
            non_breakable_products[product.category].append(product)

    return products_category_data, breakable, non_breakable, breakable_products, non_breakable_products

def optimize_states(categorized , conditions):
    for key,value in conditions.items():
        if isinstance(value,str):
            conditions[key] = value
            
    def can_add(subset,new_item):
        for item in subset:
            if (item in conditions and new_item in conditions[item]) or (new_item in conditions and item in conditions[new_item]):
                return False
        return True

    items = set(categorized.keys())
    all_subset = []
    total = 0
    
    while items:
        subset = [] 
        first_item = max(items ,key= lambda x: categorized[x])
        subset.append(first_item)
        items.remove(first_item)
        for item in list(sorted(items, key= lambda x: categorized[x], reverse=True)):
            if can_add(subset, item):       
                subset.append(item)
                items.remove(item)
        all_subset.append(subset)
        total += sum(categorized[x] for x in subset)
        
    return all_subset, total          

def estimate_boxes(products , states, box_sizes):
    biggest_box = box_sizes[0]
    targets = [(box.volume , box.max_weight) for box in box_sizes]
    estimated_boxes = {}
    
    while states: 
        state = tuple(states.pop(0))
        estimated_boxes[state] = []
        filtered_products = [value for category, values in products.items() if category in state for value in values]
        filtered_products = sorted(filtered_products , key= lambda x: (x.weight , x.volume), reverse=True)
        
        for item in filtered_products.copy():
                if (item.volume > biggest_box.volume or
                    item.weight > biggest_box.max_weight or
                    item.length > biggest_box.length or
                    item.width > biggest_box.width or
                    item.height > biggest_box.height): 
                    filtered_products.remove(item)
                    continue
        
        boxes = []
                
        while filtered_products:
            box = []
            temp_volume = 0
            temp_weight = 0
            while filtered_products:
                def score(c):
                    best_s = sorted(
                        targets,
                        key=lambda t: (t[0] - (temp_volume + c.volume)) + 3 * (t[1] - (temp_weight + c.weight))
                    )
                    best_t = max(best_s)
                    tx, ty = best_t
                    return abs(tx - (temp_volume + c.volume) ) + 3 * abs(ty - (temp_weight + c.weight) )

                can = sorted(filtered_products, key = score)
                best = can[0]
               
                if (best.volume + temp_volume) > biggest_box.volume or (best.weight + temp_weight) > biggest_box.max_weight:
                    estimated_boxes[state].append((biggest_box , box))
                    box = []
                    temp_volume =0 
                    temp_weight = 0    

                filtered_products.remove(best)
                can.remove(best)
                box.append(best)
                temp_volume += best.volume
                temp_weight += best.weight
                
                if not filtered_products: 
                    for b in box_sizes[-1:0:-1]:
                        if (b.volume - temp_volume) > 0 and (b.max_weight - temp_weight) > 0:
                            estimated_boxes[state].append((b,box))
                            break
                            
    return estimated_boxes
      
def pack_products(estimated_boxes,box_sizes):
    for boxes in estimated_boxes.values():
        for (box, products) in boxes:
            packer = BinPack(box, products)
            packer.pack()
            print(f"placed items:  {packer.placement}")
            print(f"unplaced items:  {[i.name for i in packer.unplaced]}")
                           
products = [
    Product("Crystal Bowl", "Glassware", 25, 25, 20, 1.8, [], True),
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
    Product("Laundry Detergent", "Detergent", 30, 20, 20, 2.0, [], False),
    Product("Crystal Bowl", "Glassware", 25, 25, 20, 1.8, [], True),
    Product("All incompatible Not Breakable", "Incompatible", 20, 20, 20, 3.0, [], False),
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
    Product("All incompatible Breakable", "Incompatible", 20, 20, 20, 3.0, [], True),
    Product("All incompatible Breakable", "Incompatible", 20, 20, 20, 3.0, [], True),
    Product("Magnet Strip", "Magnet", 20, 5, 2, 0.3, [], False),
    Product("Glass Vase", "Glassware", 30, 20, 30, 2.5, [], True),
    Product("Mirror", "Glassware", 50, 40, 2, 3.0, [], True),
    Product("All incompatible Breakable", "Incompatible", 20, 20, 20, 3.0, [], True),
    Product("Magnetic Hooks", "Magnet", 15, 10, 3, 0.4, [], False),
    Product("Honey", "Food", 25, 10, 10, 1.2, [], True),
    Product("Smartwatch", "Electronics", 10, 10, 2, 0.3, [], True),
    Product("Honey", "Food", 25, 10, 10, 1.2, [], True),
    Product("Olive Oil", "Food", 30, 10, 10, 1.0, [], True),
]

box_sizes = [
    Box("XLarge Box", 70, 70, 70, 15, 1),
    Box("Large Box", 50, 50, 50, 10, 2),
    Box("Medium Box", 30, 30, 30, 5, 3),
    Box("Small Box", 20, 20, 20, 2, 4),
]

constraint = {
    "Food" : ["Detergent"],
    "Detergent" : ["Food"],
    "Electronics" : ["Magnet"],
    "Magnet" : ["Electronics"],
    "Incompatible" : ["Food", "Electronics", "Magnet", "Detergent", "Glassware"]
}

products = set_constraint(products)

(categorized,
 breakable_categories,
 non_breakable_categories,
 breakable_products,
 non_breakable_products
) = categorize(products)

subsets,total = optimize_states(categorized,constraint)
breakable_subsets, breakable_total = optimize_states(breakable_categories, constraint)
non_breakable_subsets, non_breakable_total = optimize_states(non_breakable_categories, constraint)


breakable_boxes_estimated = estimate_boxes(breakable_products,breakable_subsets,box_sizes)
non_breakable_boxes_estimated = estimate_boxes(non_breakable_products,non_breakable_subsets,box_sizes)

breakable_boxes = pack_products(breakable_boxes_estimated,box_sizes)
non_breakable_boxes = pack_products(non_breakable_boxes_estimated,box_sizes)