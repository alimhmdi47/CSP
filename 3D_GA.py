
# Product class
from functools import lru_cache
from itertools import permutations
import random
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
   
    # def __repr__(self):
    #     return f"{self.name} : [{self.length},{self.width},{self.height}]"

# Box class
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
        self.products_size = [] 
        self.products_weight = []
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
        self.products_size.append([product.length, product.width, product.height])
        self.products_weight.append(product.weight)
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

class Genetic3DBinPacking:
    def __init__(self, bin_size, bin_weight_limit, items, item_weights, population_size=50, generations=100):
        self.bin_size = bin_size
        self.bin_weight_limit = bin_weight_limit
        self.items = items
        self.item_weights = item_weights
        self.population_size = population_size
        self.generations = generations
        self.placements = []  # برای ذخیره مختصات آیتم‌های قرارگرفته
        self.unplaced_items = []  # برای ذخیره آیتم‌های جا‌نشدنی

    @lru_cache(maxsize=None)
    def generate_valid_rotations(self, item):
        """تولید چرخش‌های معتبر برای آیتم‌هایی که داخل bin جا می‌شوند"""
        rotations = set(permutations(tuple(item)))  # حذف چرخش‌های تکراری
        return [r for r in rotations if all(dim <= bin_dim for dim, bin_dim in zip(r, self.bin_size))]

    def does_overlap(self, existing_items, position, size):
        """بررسی برخورد آیتم جدید با آیتم‌های موجود در bin"""
        for item in existing_items:
            pos2, size2 = item["position"], item["size"]
            # اگر در هیچ محور جدایی نباشد، Collision داریم
            if not (
                position[0] + size[0] <= pos2[0] or pos2[0] + size2[0] <= position[0] or
                position[1] + size[1] <= pos2[1] or pos2[1] + size2[1] <= position[1] or
                position[2] + size[2] <= pos2[2] or pos2[2] + size2[2] <= position[2]
            ):
                return True
        return False

    def can_fit(self, bin, item):
        """بررسی می‌کند که آیا آیتم در یکی از نقاط خالی bin جا می‌شود"""
        for position in bin["empty_spaces"]:
            # چک درون مرزهای جعبه
            if all(position[i] + item[i] <= self.bin_size[i] for i in range(3)):
                # اگر برخورد نداشت
                if not self.does_overlap(bin["items"], position, item):
                    return position
        return None

    def place_in_bin(self, bin, item, position):
        """جای‌گذاری آیتم در bin در موقعیت مشخص"""
        # حذف نقطه‌ی استفاده‌شده
        if position in bin["empty_spaces"]:
            bin["empty_spaces"].remove(position)
        # ثبت آیتم
        bin["items"].append({
            "position": position,
            "size": item
        })
        # افزودن نقاط خالی جدید
        x, y, z = position
        w, d, h = item
        for new_pos in [(x + w, y, z), (x, y + d, z), (x, y, z + h)]:
            if all(0 <= new_pos[i] < self.bin_size[i] for i in range(3)):
                if new_pos not in bin["empty_spaces"]:
                    bin["empty_spaces"].append(new_pos)

    def create_new_bin(self):
        """ایجاد bin جدید با یک نقطه خالی اولیه"""
        return {
            "items": [],
            "empty_spaces": [(0, 0, 0)]
        }

    def fitness(self, solution):
        """تابع ارزیابی: تعداد bin‌های مصرف‌شده و آیتم‌های جا‌نشدنی"""
        used_bins = 0
        bins = []
        bin_weights = []
        placements = []
        unplaced = []

        for idx in solution:
            dims = self.items[idx]
            rotations = self.generate_valid_rotations(tuple(dims))
            weight = self.item_weights[idx]
            placed = False

            for rot in rotations:
                # تلاش در بین binهای موجود
                for i, b in enumerate(bins):
                    pos = self.can_fit(b, rot)
                    if pos and bin_weights[i] + weight <= self.bin_weight_limit:
                        self.place_in_bin(b, rot, pos)
                        bin_weights[i] += weight
                        placements.append({
                            "item_index": idx,
                            "rotation": rot,
                            "bin_index": i,
                            "position": pos
                        })
                        placed = True
                        break
                if placed:
                    break

            if not placed:
                # اگر نتوانست داخل هیچ bin جا شود
                unplaced.append(idx)

        # ثبت نتایج
        self.placements = placements
        self.unplaced_items = unplaced
        # penalize unplaced heavily: fewer bins plus penalized
        return - (len(bins) - len(unplaced) * 0.1)

    def crossover(self, parent1, parent2):
        point = random.randint(0, len(parent1) - 1)
        return parent1[:point] + parent2[point:]

    def mutation(self, child):
        if len(child) < 2:
            return
        if random.random() < 0.1:
            i, j = random.sample(range(len(child)), 2)
            child[i], child[j] = child[j], child[i]

    def run(self):
        population = [random.sample(range(len(self.items)), len(self.items)) for _ in range(self.population_size)]
        for _ in range(self.generations):
            population.sort(key=lambda sol: self.fitness(sol))
            parents = population[:10]
            new_pop = parents.copy()
            while len(new_pop) < self.population_size:
                p1, p2 = random.sample(parents, 2)
                child = self.crossover(p1, p2)
                self.mutation(child)
                new_pop.append(child)
            population = new_pop
        return population[0]
    
    def get_unplaced_item(self):
        return self.unplaced_items
    def get_placedment(self):
        return self.placements



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



box_sizes = [
    Box("XLarge Box", 1000, 800, 700, 15, 1),
    Box("Large Box", 800, 600, 500, 10, 2),
    Box("Medium Box", 600, 400, 300, 5, 3),
    Box("Small Box", 400, 300, 200, 2, 4),
]
products =[
 Product("Fridge Magnet", "Magnet", 5, 5, 2, 0.1, [], False),
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
    Product("Over size", "Over", 80000000, 800, 800, 5.0, [], False),
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
    Product("Over size", "Over", 8000000, 800, 800, 5.0, [], False),
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
print("########################################################")

print("$$$$$$$$$$$$$$$$4")
for box in all_boxes:
    bin_size = [box.length, box.width, box.height]    
    bin_weight_limit = box.max_weight
    items = box.products_size
    items_weights = box.products_weight
    solver = Genetic3DBinPacking(bin_size, bin_weight_limit, items, items_weights)
    solution = solver.run()
    print("best arrangement", solution)
    # اجرای الگوریتم
    solution = solver.run()
    print("placment:", solver.get_placedment())
    print("unplaced:", solver.get_unplaced_item())
    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
   