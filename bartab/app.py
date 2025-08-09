from flask import Flask, render_template, request, redirect, url_for, flash
import json, os

app = Flask(__name__)
app.secret_key = "supersecretkey"

DATA_FILE = "data.json"

# ---------- Helpers ----------
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"menu": {}, "tabs": {}}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Converter: als menu een lijst is, maak er dict van
    if isinstance(data.get("menu"), list):
        data["menu"] = {"Overig": data["menu"]}
        save_data(data)

    # Fix: zorg dat prijs in tabs als float is
    for tab_list in data.get("tabs", {}).values():
        for item in tab_list:
            item["price"] = float(item.get("price", 0))

    return data

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# ---------- Routes ----------
@app.route("/")
def categories():
    data = load_data()
    return render_template(
        "categories.html",
        categories=data["menu"].keys(),
        tabs=data["tabs"]
    )

@app.route("/category/<cat>")
def drinks(cat):
    data = load_data()
    drinks = data["menu"].get(cat, [])
    return render_template("drinks.html", category=cat, drinks=drinks)

@app.route("/select_customer/<category>/<drink_name>/<price>")
def select_customer(category, drink_name, price):
    data = load_data()
    return render_template(
        "select_customer.html",
        category=category,
        drink_name=drink_name,
        price=price,
        customers=data["tabs"].keys()
    )

@app.route("/add_to_tab", methods=["POST"])
def add_to_tab():
    data = load_data()

    existing_name = request.form.get("existing_name", "")
    new_name = request.form.get("new_name", "").strip()
    name = existing_name if existing_name else new_name

    if not name:
        flash("Geen klantnaam opgegeven!", "danger")
        return redirect(url_for("categories"))

    item_name = request.form["item_name"]
    item_price = float(request.form["item_price"])

    # Lees aantal drankjes uit formulier, default 1
    amount = request.form.get("amount", "1")
    try:
        amount = int(amount)
        if amount < 1:
            amount = 1
    except ValueError:
        amount = 1

    if name not in data["tabs"]:
        data["tabs"][name] = []

    # Voeg het drankje 'amount' keer toe
    for _ in range(amount):
        data["tabs"][name].append({"name": item_name, "price": item_price})

    save_data(data)
    flash(f"{amount}x {item_name} toegevoegd aan {name}", "success")
    return redirect(url_for("categories"))

@app.route("/tab/<name>")
def view_tab(name):
    data = load_data()
    tab = data["tabs"].get(name, [])
    total = sum(item["price"] for item in tab)
    menu = data.get("menu", {})
    return render_template("tab.html", name=name, tab=tab, total=total, menu=menu)

@app.route("/remove_from_tab/<name>/<int:index>", methods=["POST"])
def remove_from_tab(name, index):
    data = load_data()
    if name in data["tabs"] and 0 <= index < len(data["tabs"][name]):
        del data["tabs"][name][index]
    save_data(data)
    return redirect(url_for("view_tab", name=name))

@app.route("/close_tab/<name>", methods=["POST"])
def close_tab(name):
    data = load_data()
    if name in data["tabs"]:
        data["tabs"][name] = []  # klant blijft bestaan
    save_data(data)
    flash(f"Rekening van {name} is afgesloten (klant blijft in systeem)", "info")
    return redirect(url_for("categories"))

# ---------- Leaderboard ----------
@app.route("/leaderboard")
def leaderboard():
    data = load_data()
    counts = {name: len(tab) for name, tab in data.get("tabs", {}).items()}
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return render_template("leaderboard.html", leaderboard=sorted_counts)

# ---------- Settings Routes ----------
@app.route("/settings")
def settings():
    data = load_data()
    return render_template("settings.html", customers=data["tabs"].keys(), categories=data["menu"].keys())

@app.route("/settings/add", methods=["POST"])
def settings_add():
    data = load_data()
    action = request.form.get("action")

    if action == "add_customer":
        new_customer = request.form.get("new_customer", "").strip()
        if new_customer:
            if new_customer not in data["tabs"]:
                data["tabs"][new_customer] = []
                save_data(data)
                flash(f"Klant '{new_customer}' toegevoegd.", "success")
            else:
                flash(f"Klant '{new_customer}' bestaat al.", "warning")
        else:
            flash("Voer een klantnaam in.", "danger")

    elif action == "add_category":
        new_category = request.form.get("new_category", "").strip()
        if new_category:
            if new_category not in data["menu"]:
                data["menu"][new_category] = []
                save_data(data)
                flash(f"Categorie '{new_category}' toegevoegd.", "success")
            else:
                flash(f"Categorie '{new_category}' bestaat al.", "warning")
        else:
            flash("Voer een categorienaam in.", "danger")

    elif action == "add_drink":
        category = request.form.get("category_select")
        drink_name = request.form.get("drink_name", "").strip()
        drink_price = request.form.get("drink_price", "").strip()
        if not category or category not in data["menu"]:
            flash("Selecteer een geldige categorie.", "danger")
        elif not drink_name:
            flash("Voer een dranknaam in.", "danger")
        else:
            try:
                price = float(drink_price)
                data["menu"][category].append({"name": drink_name, "price": price})
                save_data(data)
                flash(f"Drankje '{drink_name}' toegevoegd aan '{category}'.", "success")
            except ValueError:
                flash("Voer een geldig prijsbedrag in.", "danger")
    else:
        flash("Ongeldige actie.", "danger")

    return redirect(url_for("settings"))

@app.route("/settings/delete_customer", methods=["POST"])
def settings_delete_customer():
    data = load_data()
    customer = request.form.get("customer_to_delete")
    if customer in data["tabs"]:
        del data["tabs"][customer]
        save_data(data)
        flash(f"Klant '{customer}' is verwijderd.", "success")
    else:
        flash("Klant niet gevonden.", "danger")
    return redirect(url_for("settings"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
