# Home Bar Management App

Deze webapplicatie is gemaakt met Flask en helpt bij het beheren van drankbestellingen in een kleine baromgeving. Klanten kunnen drankjes bestellen, tabs worden bijgehouden en afgesloten, en er is een leaderboard om te zien wie de meeste drankjes heeft besteld.

---

## Functionaliteiten

- Overzicht van categorieën en drankjes
- Drankjes toevoegen aan tabs per klant
- Tabs bekijken en beheren per klant
- Tabs afsluiten (rekening betalen)
- Instellingen beheren: klanten, categorieën en drankjes toevoegen/verwijderen
- Leaderboard met klanten die de meeste drankjes hebben besteld

---

## Installatie

1. Dowload de bestenden


Installeer de vereiste packages:

pip install flask

Start de app:

    python app.py

    Open je browser en ga naar: http://localhost:5000

Bestanden

    app.py – De Flask applicatie

    templates/ – HTML templates (zoals categories.html, tab.html, leaderboard.html, etc.)

    static/ – Statische bestanden zoals CSS en JavaScript (indien aanwezig)

    data.json – JSON-bestand waarin het menu en de tabs worden opgeslagen

Gebruik

    Op de startpagina kies je een categorie en vervolgens een drankje.

    Je voegt drankjes toe aan een klant (bestaand of nieuw).

    In het tabblad per klant zie je welke drankjes hij/zij besteld heeft.

    Je sluit tabs af via de detailpagina per klant.

    Via /leaderboard zie je een ranglijst van klanten met de meeste bestellingen.

Aanpassen

    Menu en klanten worden opgeslagen in data.json.

    Voeg nieuwe categorieën, drankjes en klanten toe via de instellingenpagina /settings.

License

Deze code is open-source en vrij te gebruiken onder de MIT License.
Contact

Voor vragen of suggesties, neem contact op via GitHub Issues.

Veel plezier met het beheren van je home bar! 🍹
