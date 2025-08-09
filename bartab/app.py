from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import json, os, io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__)
app.secret_key = "supersecretkey"

DATA_FILE = "data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"menu": {}, "tabs": {}}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data.get("menu"), list):
        data["menu"] = {"Overig": data["menu"]}
        save_data(data)

    for tab_list in data.get("tabs", {}).values():
        for item in tab_list:
            item["price"] = float(item.get("price", 0))

    return data

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

@app.route("/")
def categories():
    data = load_data()
    tabs = data["tabs"]

    tabs_totals = {}
    for name, tab in tabs.items():
        total = sum(float(item.get("price", 0)) for item in tab)
        tabs_totals[name] = total

    return render_template(
        "categories.html",
        categories=data["menu"].keys(),
        tabs=tabs,
        tabs_totals=tabs_totals
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

    amount = request.form.get("amount", "1")
    try:
        amount = int(amount)
        if amount < 1:
            amount = 1
    except ValueError:
        amount = 1

    if name not in data["tabs"]:
        data["tabs"][name] = []

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
        data["tabs"][name] = []
    save_data(data)
    flash(f"Rekening van {name} is afgesloten (klant blijft in systeem)", "info")
    return redirect(url_for("categories"))

@app.route("/leaderboard")
def leaderboard():
    data = load_data()
    counts = {name: len(tab) for name, tab in data.get("tabs", {}).items()}
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return render_template("leaderboard.html", leaderboard=sorted_counts)

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


# Nieuwe route om PDF overzicht te downloaden
@app.route("/download_overzicht")
def download_overzicht():
    data = load_data()
    tabs = data.get("tabs", {})

    overzicht = []
    totaal_avond = 0
    for name, tab in tabs.items():
        totaal = sum(item.get("price", 0) for item in tab)
        overzicht.append((name, totaal))
        totaal_avond += totaal

    overzicht.sort(key=lambda x: x[1], reverse=True)

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Overzicht drankjes per persoon")

    c.setFont("Helvetica", 12)
    y = height - 80
    c.drawString(50, y, "Naam")
    c.drawString(300, y, "Bedrag (€)")
    y -= 20
    c.line(50, y, 550, y)
    y -= 20

    for naam, bedrag in overzicht:
        c.drawString(50, y, naam)
        c.drawRightString(400, y, f"€{bedrag:.2f}")
        y -= 20
        if y < 50:
            c.showPage()
            y = height - 50

    c.line(50, y, 550, y)
    y -= 30
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Totaal opbrengst avond:")
    c.drawRightString(400, y, f"€{totaal_avond:.2f}")

    c.save()
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="overzicht_drankjes.pdf", mimetype="application/pdf")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
