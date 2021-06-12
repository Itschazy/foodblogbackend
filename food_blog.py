import sqlite3
import argparse
conn = sqlite3.connect('food_blog.db')
cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS meals(
                    meal_id INT PRIMARY KEY,
                    meal_name VARCHAR(20) NOT NULL UNIQUE
                    )""")

cur.execute("""CREATE TABLE IF NOT EXISTS ingredients(
                    ingredient_id INT PRIMARY KEY,
                    ingredient_name VARCHAR(20) NOT NULL UNIQUE
                    )""")

cur.execute("""CREATE TABLE IF NOT EXISTS measures(
                    measure_id INT PRIMARY KEY,
                    measure_name VARCHAR(20) UNIQUE
                    )""")
cur.execute("""CREATE TABLE IF NOT EXISTS recipes(
                    recipe_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    recipe_name VARCHAR(20) NOT NULL,
                    recipe_description VARCHAR(20)
                    )""")

cur.execute("""PRAGMA foreign_keys = ON;""")

cur.execute("""CREATE TABLE IF NOT EXISTS serve(
                    serve_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    recipe_id INT NOT NULL,
                    meal_id INT NOT NULL,
                    FOREIGN KEY(recipe_id) REFERENCES recipes(recipe_id),
                    FOREIGN KEY(meal_id) REFERENCES meals(meal_id)
                    )""")

cur.execute("""CREATE TABLE IF NOT EXISTS quantity(
                    quantity_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    measure_id INT NOT NULL,
                    ingredient_id INT NOT NULL,
                    quantity INT NOT NULL,
                    recipe_id INT NOT NULL,
                    FOREIGN KEY(measure_id) REFERENCES measures(measure_id),
                    FOREIGN KEY(ingredient_id) REFERENCES ingredients(ingredient_id),
                    FOREIGN KEY(recipe_id) REFERENCES recipes(recipe_id)
                    )""")

data = {"meals": ("breakfast", "brunch", "lunch", "supper"),
        "ingredients": ("milk", "cacao", "strawberry", "blueberry", "blackberry", "sugar"),
        "measures": ("ml", "g", "l", "cup", "tbsp", "tsp", "dsp", "")}

parser = argparse.ArgumentParser()
parser.add_argument("food_blog.py", default="food_blog.py")
parser.add_argument("--ingredients", default=None)
parser.add_argument("--meals", default=None)
args = parser.parse_args()

for key in data.keys():
    id = 1
    for value in data[key]:
        cur.execute(f"""INSERT OR IGNORE INTO {key} VALUES ({id}, '{value}');""")
        id += 1

conn.commit()
if args.ingredients == None and args.meals == None:
    print("Pass the empty recipe name to exit.")
    recipe_name = None
    while True:
        print("Recipe name:", end=' ')
        recipe_name = input()
        if recipe_name == "":
                break
        else:
            print("Recipe description:", end=' ')
            recipe_description = input()
            last_row = cur.execute(f"""INSERT INTO recipes (recipe_name, recipe_description) VALUES ('{recipe_name}', '{recipe_description}');""").lastrowid
            result = cur.execute("""SELECT * FROM meals""")
            all_rows = result.fetchall()
            print(all_rows)
            print("Enter proposed meals separated by a space:", end=" ")
            user_input = input().split()
            for value in user_input:
                cur.execute(f"INSERT INTO serve (recipe_id, meal_id) VALUES ({int(last_row)}, {int(value)})")
            while True:
                print("Input quantity of ingredient <press enter to stop>:", end=' ')
                user_input = input()
                if user_input == "":
                    break
                else:
                    if len(user_input.split()) == 2:
                        measure = ""
                        quantity, ingredient = user_input.split()
                    else:
                        quantity, measure, ingredient = user_input.split()
                    cnt_measure = 0
                    cnt_ingredient = 0
                    get_measure_id = None
                    get_ingredient_id = None
                    measure_name_value = None
                    ingredient_name_value = None
                    for value in data["measures"]:
                        if measure in value and measure != "":
                            cnt_measure += 1
                            if cnt_measure > 1:
                                print("The measure is not conclusive!")
                                break
                            elif measure !="":
                                measure_name_value = value
                                get_measure_id = cur.execute(f"""SELECT measure_id
                                                     FROM measures
                                                     WHERE measure_name == "{measure_name_value}";""").fetchone()[0]
                        else:
                            get_measure_id = '8'
                    for value in data["ingredients"]:
                        if ingredient in value:
                            cnt_ingredient += 1
                            if cnt_ingredient > 1:
                                print("The ingredient is not conclusive!")
                                break
                            else:
                                ingredient_name_value = value
                    get_ingredient_id = cur.execute(f"""SELECT ingredient_id
                                                        FROM ingredients
                                                        WHERE ingredient_name == "{ingredient_name_value}";""").fetchone()[0]
                    cur.execute(f"""INSERT INTO quantity (quantity, recipe_id, measure_id, ingredient_id) 
                                VALUES ({int(quantity)}, {int(last_row)}, {int(get_measure_id)}, {int(get_ingredient_id)})""")
else:
    f_ingr = str()
    f_meals = str()
    if args.ingredients != None:
        find_ingredients = args.ingredients.split(',')
        count = len(find_ingredients)
        i = 0
        while i < count:
            f_ingr += f"'{find_ingredients[i]}'"
            i += 1
            if i < count:
                f_ingr += f","

    else:
        find_ingredients = ()
    if args.meals != None:
        find_meals = args.meals.split(',')
        count = len(find_meals)
        i = 0
        while i < count:
            f_meals += f"'{find_meals[i]}'"
            i += 1
            if i < count:
                f_meals += f","
    else:
        find_meals = ()
    get_recipe = cur.execute(f"""SELECT recipes.recipe_name,recipes.recipe_id, ingredients.ingredient_name, meals.meal_name
                                FROM recipes 
                                INNER JOIN serve
                                ON  recipes.recipe_id = serve.recipe_id
                                INNER JOIN meals 
                                ON serve.meal_id = meals.meal_id
                                INNER JOIN quantity
                                ON recipes.recipe_id = quantity.recipe_id
                                INNER JOIN ingredients
                                ON quantity.ingredient_id = ingredients.ingredient_id
                                WHERE ingredients.ingredient_name IN ({f_ingr}) and meals.meal_name IN ({f_meals});
                                """).fetchall()

    if get_recipe is not None:
        recipe_book = dict()
        for element in get_recipe:
            if element[1] not in recipe_book.keys():
                recipe_book[element[1]] = set()
            recipe_book[element[1]].add(element[2])
        input_ingredients = set(args.ingredients.split(","))
        recipe_names = list()

        for key, value in recipe_book.items():
            if input_ingredients <= value:
                recipe_names.append([recipe[0] for recipe in get_recipe if recipe[1] == key][0])

    if recipe_names:
        print(f"Recipes selected for you: {', '.join(recipe_names)}")
    else:
        print("There are no such recipes in the database.")


conn.commit()
conn.close()
