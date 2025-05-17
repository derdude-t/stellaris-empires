import re
import csv
import os
from collections import defaultdict

# === Parsing Logic ===

def parse_empire_initializer_and_key(empire_content_str):
    """
    Parst einen String-Block der Definition eines einzelnen Imperiums, 
    um dessen Key und Initializer-Wert zu extrahieren.
    """
    empire_initializer = None  # Standard, falls die Zeile nicht gefunden wird
    empire_key = None
    initializer_line_found = False # Um sicherzustellen, dass wir nur den ersten Eintrag nehmen

    lines = empire_content_str.splitlines()
    for line in lines:
        stripped_line = line.strip()
        
        # Extrahiere Key (nimm den ersten gefundenen)
        if stripped_line.startswith("key=") and empire_key is None:
            # Erlaubt auch leere Keys, obwohl unüblich: key=""
            match = re.match(r'key="([^"]*)"', stripped_line) 
            if match:
                empire_key = match.group(1)
                
        # Extrahiere Initializer (nimm den ersten gefundenen)
        elif stripped_line.startswith("initializer=") and not initializer_line_found:
            # Erlaubt explizit leere Strings: initializer=""
            match = re.match(r'initializer="([^"]*)"', stripped_line)
            if match:
                empire_initializer = match.group(1) # Kann jetzt "" sein
                initializer_line_found = True
                
    return {'key': empire_key, 'initializer': empire_initializer}

def split_into_empire_blocks(file_content): # Wiederverwendet
    """Teilt den gesamten Dateiinhalt in Strings auf, die jeweils einen Imperiumsblock darstellen."""
    empire_blocks_content = []
    balance = 0
    current_block_start_index = -1
    for i, char in enumerate(file_content):
        if char == '{':
            if balance == 0:
                current_block_start_index = i + 1
            balance += 1
        elif char == '}':
            balance -= 1
            if balance == 0 and current_block_start_index != -1:
                empire_blocks_content.append(file_content[current_block_start_index:i])
                current_block_start_index = -1
            elif balance < 0: 
                balance = 0 
                current_block_start_index = -1
    return empire_blocks_content

def extract_initializers_data_from_file(filepath="user_empire_designs_v3.4.txt"):
    """
    Liest die Stellaris User Empire Designs Datei, parst jedes Imperium
    und extrahiert dessen Key und Initializer.
    """
    try:
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            content = f.read()
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"Fehler beim Lesen der Datei '{filepath}': {e}")
        return []

    empire_block_strings = split_into_empire_blocks(content)
    parsed_empires_list = []
    
    for i, block_str in enumerate(empire_block_strings):
        empire_details = parse_empire_initializer_and_key(block_str)
        
        # Stelle einen Key-Platzhalter sicher, falls einer fehlt, da jedes Imperium verarbeitet wird
        if empire_details['key'] is None:
            empire_details['key'] = f"UNKNOWN_KEY_EMPIRE_{i+1}"
        
        # Füge alle Imperien hinzu, da wir auch die ohne Initializer-Zeile oder mit leerem Initializer sehen wollen
        parsed_empires_list.append(empire_details)
            
    return parsed_empires_list

# === Data Grouping ===

def group_empires_by_initializer(parsed_empires_list):
    """
    Gruppiert Imperien anhand ihres Initializer-Wertes.
    """
    initializer_to_empires_map = defaultdict(list)
    for empire_data in parsed_empires_list:
        initializer_value = empire_data['initializer']
        empire_key = empire_data['key'] # Key wurde bereits in extract_initializers_data_from_file sichergestellt

        # Verwende einen speziellen Anzeigewert, wenn die Initializer-Zeile komplett fehlte (None)
        if initializer_value is None:
            display_initializer = "<NOT_SET>"
        else:
            display_initializer = initializer_value # Kann "" oder ein anderer String sein
            
        initializer_to_empires_map[display_initializer].append(empire_key)
    return initializer_to_empires_map

# === CSV Preparation ===

def prepare_initializer_data_for_csv(initializer_to_empires_map):
    """
    Bereitet die gruppierten Initializer-Daten für die CSV-Ausgabe vor.
    Ausgabeformat: [[Anzahl, Initializer_Wert, Liste_der_Imperiums_Keys], ...]
    """
    data_for_csv = []
    for initializer_value, empire_keys_list in initializer_to_empires_map.items():
        count = len(empire_keys_list)
        data_for_csv.append([count, initializer_value, empire_keys_list])
    
    # Sortiere die Daten: primär nach Initializer-Wert (item[1]) für konsistente CSV-Ausgabe
    sorted_data_for_csv = sorted(data_for_csv, key=lambda item: item[1])
    return sorted_data_for_csv

# === CSV Output Function ===

def write_initializers_csv(data_for_csv, output_filepath="initializers_report.csv"):
    """
    Schreibt die Initializer-Daten in eine CSV-Datei, wobei Semikolon als Trennzeichen verwendet wird.
    """
    if not data_for_csv:
        print("Keine Daten zum Schreiben in CSV vorhanden.")
        return

    try:
        with open(output_filepath, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=';')
            
            # Schreibe den Header
            csv_writer.writerow(['N', 'Initializer', 'Reiche'])
            
            for count, initializer_value, empire_keys_list in data_for_csv:
                # Füge Imperiums-Keys mit Semikolon zusammen.
                # Das csv-Modul wird das Feld "Reiche" automatisch in Anführungszeichen setzen,
                # wenn es das Trennzeichen (Semikolon) enthält (d.h. bei mehreren Keys).
                keys_str = ";".join(sorted(empire_keys_list)) 
                
                csv_writer.writerow([count, initializer_value, keys_str])
        print(f"\nCSV-Datei erfolgreich geschrieben: {output_filepath}")
    except IOError as e:
        print(f"Fehler beim Schreiben der CSV-Datei '{output_filepath}': {e}")

# === Main Execution ===

if __name__ == "__main__":
    input_filepath = "user_empire_designs_v3.4.txt"
    output_csv_filepath = "initializers_report.csv"

    print(f"Starte Analyse der Initializer aus: {input_filepath}")

    # 1. Extrahiere Initializer-Daten aus der Datei
    parsed_initializers_data = extract_initializers_data_from_file(input_filepath)
    
    if not os.path.exists(input_filepath):
        print(f"\nDatei '{input_filepath}' nicht gefunden.")
        dummy_q = input(f"Möchten Sie eine Dummy-Datei '{input_filepath}' für Testzwecke erstellen? (j/n): ").lower()
        if dummy_q == 'j':
            dummy_content_initializers = """
            empire_one = {
                key="EMP_A"
                initializer="standard_ship_designs" # Mit Wert
            }
            empire_two = {
                key="EMP_B"
                initializer="" # Leerer String
            }
            empire_three = {
                key="EMP_C"
                # Keine Initializer-Zeile
            }
            empire_four = {
                key="EMP_D"
                initializer="another_custom_init"
            }
            empire_five = {
                key="EMP_E"
                initializer="" # Weiterer leerer String
            }
            empire_no_key = {
                 initializer="init_for_no_key_empire"
            }
            """
            try:
                with open(input_filepath, 'w', encoding='utf-8') as f:
                    f.write(dummy_content_initializers)
                print(f"Dummy-Datei '{input_filepath}' erfolgreich erstellt. Bitte das Skript erneut ausführen.")
                exit() 
            except IOError as e:
                print(f"Fehler beim Erstellen der Dummy-Datei: {e}")
                exit()
        else:
            print("Skript wird fortgesetzt. Wenn die Datei leer ist, wird kein Bericht erstellt.")
    
    if not parsed_initializers_data and os.path.exists(input_filepath):
         print(f"Keine Imperien in '{input_filepath}' gefunden oder Datei ist leer/fehlerhaft.")
    
    if not parsed_initializers_data:
        print("Keine Daten zur Verarbeitung vorhanden.")
    else:
        print(f"{len(parsed_initializers_data)} Imperien-Einträge für Initializer-Analyse verarbeitet.")

        # 2. Gruppiere Imperien nach ihrem Initializer-Wert
        grouped_by_initializer = group_empires_by_initializer(parsed_initializers_data)
        print(f"{len(grouped_by_initializer)} einzigartige Initializer-Werte (inkl. '' und '<NOT_SET>') gefunden.")

        # 3. Bereite Daten für die CSV-Ausgabe vor
        data_for_csv_output = prepare_initializer_data_for_csv(grouped_by_initializer)
        
        # 4. Schreibe in CSV
        write_initializers_csv(data_for_csv_output, output_csv_filepath)