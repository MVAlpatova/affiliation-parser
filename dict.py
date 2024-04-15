import tkinter as tk
from tkinter import filedialog
import ctypes

# Define the known aliases for Moscow Polytechnic University
possible_names = [
    "Moscow Polytechnic University",
    "Moscow Polytech",
    "Moscow State Polytechnic University",
    "Mospolytech",
    "Moscow Polytechnical University",
    "Moscow State Polytech Univ",
    "Moscow Polytech Univ",
    'Moscow Polytech University',
    'FGBOU VO Moscow Polytech Univ',
    'Moscow Politech Univ'
]

# Define the list of all countries
all_countries = """
Abkhazia; Afghanistan; Aland Islands; Albania; Algeria; American Samoa; Andorra; Angola; Anguilla; Antarctica;
Antigua & Barbuda; Argentina; Armenia; Artsakh; Aruba; Australia; Austria; Azerbaijan; Bahamas; Bahrain; Bangladesh;
Barbados; Belarus; Belgium; Belize; Benin; Bermuda; Bhutan; Bolivia; Bosnia & Herzegovina; Botswana; Bouvet Island;
Brazil; British Indian Ocean Territory; British Virgin Islands; Brunei; Bulgaria; Burkina Faso; Burundi; Cambodia;
Cameroon; Canada; Cape Verde; Caribbean Netherlands; Cayman Islands; Central African Republic; Chad; Chile; China;
Christmas Island; Cocos; Colombia; Comoros; Congo; Cook Islands; Costa Rica; Croatia; Cuba; Curaçao; Cyprus; Czechia;
Côte d'Ivoire; Denmark; Djibouti; Dominica; Dominican Republic; Ecuador; Egypt; El Salvador; Equatorial Guinea; Eritrea;
Estonia; Eswatini; Ethiopia; Falkland Islands; Faroe Islands; Fiji; Finland; France; French Guiana; French Polynesia;
French Southern Territories; Gabon; Gambia; Georgia; Germany; Ghana; Gibraltar; Greece; Greenland; Grenada; Guadeloupe;
Guam; Guatemala; Guernsey; Guinea; Guinea-Bissau; Guyana; Haiti; Heard & McDonald Islands; Honduras; Hong Kong SAR China;
Hungary; Iceland; India; Indonesia; Iran; Iraq; Ireland; Isle of Man; Israel; Italy; Jamaica; Japan; Jersey; Jordan;
Kazakhstan; Kenya; Kiribati; Kosovo; Kuwait; Kyrgyzstan; Laos; Latvia; Lebanon; Lesotho; Liberia; Libya; Liechtenstein;
Lithuania; Luxembourg; Macao SAR China; Madagascar; Malawi; Malaysia; Maldives; Mali; Malta; Marshall Islands; Martinique;
Mauritania; Mauritius; Mayotte; Mexico; Micronesia; Moldova; Monaco; Mongolia; Montenegro; Montserrat; Morocco; Mozambique;
Myanmar; Namibia; Nauru; Nepal; Netherlands; New Caledonia; New Zealand; Nicaragua; Niger; Nigeria; Niue; Norfolk Island;
North Korea; North Macedonia; Northern Cyprus; Northern Mariana Islands; Norway; Oman; Pakistan; Palau; Palestinian Territories;
Panama; Papua New Guinea; Paraguay; Peru; Philippines; Pitcairn Islands; Poland; Portugal; Puerto Rico; Qatar; Romania;
Russia; Russian Federation; Rwanda; Réunion; Sahrawi Arab Democratic Republic; Samoa; San Marino; Saudi Arabia; Senegal;
Serbia; Seychelles; Sierra Leone; Singapore; Sint Maarten; Slovakia; Slovenia; Solomon Islands; Somalia; Somaliland;
South Africa; South Georgia & South Sandwich Islands; South Korea; South Ossetia; South Sudan; Spain; Sri Lanka; St. Barthélemy;
St. Helena; St. Kitts & Nevis; St. Lucia; St. Martin; St. Pierre & Miquelon; St. Vincent & Grenadines; Sudan; Suriname;
Svalbard & Jan Mayen; Sweden; Switzerland; Syria; São Tomé & Príncipe; Taiwan; Tajikistan; Tanzania; Thailand; Timor-Leste;
Togo; Tokelau; Tonga; Transnistria; Trinidad & Tobago; Tunisia; Turkey; Turkmenistan; Turks & Caicos Islands; Tuvalu;
U.S. Outlying Islands; U.S. Virgin Islands; Uganda; Ukraine; United Arab Emirates; United Kingdom; United States; Uruguay;
Uzbekistan; Vanuatu; Vatican City; Venezuela; Vietnam; Wallis & Futuna; Western Sahara; Yemen; Zambia; Zimbabwe
"""

# Define the list of all possible publication types
publication_type_translations = {
    'Article': 'Статья',
    'Book Chapter': 'Глава книги',
    'Conference Paper': 'Материалы конференции',
    'Proceedings Paper': 'Материалы конференции',
    'Editorial': 'Редакционная статья',
    'Erratum': 'Эрратум',
    'Review': 'Обзор'
}


# Function to show a system popup message
def show_popup(message):
    ctypes.windll.user32.MessageBoxW(0, message, "Получен результат", 1)


# Set up the root Tkinter window
root = tk.Tk()
root.withdraw()  # We don't want a full GUI, so keep the root window from appearing

# Show the file dialog
#file_path = filedialog.askopenfilename(
#    title="Выберите файл CSV с данными из Scopus",
#    filetypes=(("CSV files", "*.csv"), ("all files", "*.*"))
#)
