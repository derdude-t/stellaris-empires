import re
import csv
import os # Für Dateiprüfung und Dummy-Erstellung
from collections import defaultdict

# === Parsing Logic ===

def parse_empire_origin_and_key(empire_content_str):
    """
    Parst einen String-Block der Definition eines einzelnen Imperiums, 
    um dessen Key und Origin zu extrahieren.
    Ein Imperium hat nur einen Origin. Nimmt die erste gefundene 'origin='-Zeile.
    """
    empire_origin = None
    empire_key = None
    
    lines = empire_content_str.splitlines()
    for line in lines:
        stripped_line = line.strip()
        # Extrahiere Key (nimm den ersten gefundenen)
        if stripped_line.startswith("key=") and empire_key is None:
            match = re.match(r'key="([^"]+)"', stripped_line)
            if match:
                empire_key = match.group(1)
        # Extrahiere Origin (nimm den ersten gefundenen)
        elif stripped_line.startswith("origin=") and empire_origin is None:
            match = re.match(r'origin="([^"]+)"', stripped_line)
            if match:
                empire_origin = match.group(1)
                
    return {'key': empire_key, 'origin': empire_origin}

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
                balance = 0 # Bei fehlerhafter Struktur zurücksetzen
                current_block_start_index = -1
    return empire_blocks_content

def extract_origins_data_from_file(filepath="user_empire_designs_v3.4.txt"):
    """
    Liest die Stellaris User Empire Designs Datei, parst jedes Imperium
    und extrahiert dessen Key und Origin.
    """
    try:
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            content = f.read()
    except FileNotFoundError:
        # Dieser Fall wird im Hauptblock mit einer Dummy-Datei-Option behandelt
        return []
    except Exception as e:
        print(f"Fehler beim Lesen der Datei '{filepath}': {e}")
        return []

    empire_block_strings = split_into_empire_blocks(content)
    parsed_empires_list = []
    
    for i, block_str in enumerate(empire_block_strings):
        empire_details = parse_empire_origin_and_key(block_str)
        # Nur Imperien einbeziehen, bei denen ein Origin tatsächlich gefunden wurde
        if empire_details.get('origin'):
            # Stelle einen Key-Platzhalter sicher, falls einer fehlt
            if empire_details['key'] is None:
                empire_details['key'] = f"UNKNOWN_KEY_EMPIRE_{i+1}"
            parsed_empires_list.append(empire_details)
            
    return parsed_empires_list

# === Data Grouping ===

def group_empires_by_origin(parsed_empires_list):
    """
    Gruppiert Imperien anhand ihres Origins.
    """
    origin_to_empires_map = defaultdict(list)
    for empire_data in parsed_empires_list:
        # Wir haben bereits nach Imperien mit Origins gefiltert und Keys in
        # extract_origins_data_from_file sichergestellt
        origin_name = empire_data['origin']
        empire_key = empire_data['key']
        origin_to_empires_map[origin_name].append(empire_key)
    return origin_to_empires_map

# === CSV Preparation ===

def prepare_origin_data_for_csv(origin_to_empires_map):
    """
    Bereitet die gruppierten Origin-Daten für die CSV-Ausgabe vor.
    Ausgabeformat: [[Anzahl, Origin_Name, Liste_der_Imperiums_Keys], ...]
    """
    data_for_csv = []
    for origin_name, empire_keys_list in origin_to_empires_map.items():
        count = len(empire_keys_list)
        data_for_csv.append([count, origin_name, empire_keys_list])
    
    # Sortiere die Daten: primär nach Origin-Name (item[1]) für konsistente CSV-Ausgabe
    sorted_data_for_csv = sorted(data_for_csv, key=lambda item: item[1])
    return sorted_data_for_csv

# === CSV Output Function ===

def write_origins_csv(data_for_csv, output_filepath="origins_report.csv"):
    """
    Schreibt die Origin-Daten in eine CSV-Datei, wobei Semikolon als Trennzeichen verwendet wird.
    """
    if not data_for_csv:
        print("Keine Daten zum Schreiben in CSV vorhanden.")
        return

    try:
        with open(output_filepath, 'w', newline='', encoding='utf-8') as csvfile:
            # Verwende Semikolon als Haupt-Trennzeichen gemäß Benutzerbeispiel "N;Origin;Empires"
            csv_writer = csv.writer(csvfile, delimiter=';')
            
            # Schreibe den Header
            csv_writer.writerow(['N', 'Origin', 'Empires'])
            
            for count, origin_name, empire_keys_list in data_for_csv:
                # Füge Imperiums-Keys mit Semikolon zusammen.
                # Das csv-Modul wird das Feld automatisch in Anführungszeichen setzen,
                # wenn es das Trennzeichen (Semikolon) enthält (d.h. bei mehreren Keys).
                keys_str = ";".join(sorted(empire_keys_list)) 
                
                csv_writer.writerow([count, origin_name, keys_str])
        print(f"\nCSV-Datei erfolgreich geschrieben: {output_filepath}")
    except IOError as e:
        print(f"Fehler beim Schreiben der CSV-Datei '{output_filepath}': {e}")

# === Main Execution ===

if __name__ == "__main__":
    input_filepath = "user_empire_designs_v3.4.txt"
    output_csv_filepath = "origins_report.csv"

    print(f"Starte Analyse der Origins aus: {input_filepath}")

    # 1. Extrahiere Origin-Daten aus der Datei
    parsed_origins_data = extract_origins_data_from_file(input_filepath)
    
    if not os.path.exists(input_filepath):
        print(f"\nDatei '{input_filepath}' nicht gefunden.")
        dummy_q = input(f"Möchten Sie eine Dummy-Datei '{input_filepath}' für Testzwecke erstellen? (j/n): ").lower()
        if dummy_q == 'j':
            dummy_content_origins = """
            { name="Ringworld Start" key="RING_KEY" origin="origin_shattered_ring" species={ class="HUM" } }
            { name="Progenitor Hive" key="HIVE_KEY_1" origin="origin_progenitor_hive" ethic="ethic_gestalt_consciousness" }
            { name="Lost Colony Humans" key="LOST_COL_HUM" origin="origin_lost_colony" species={ class="HUM" } }
            { name="Mechanists" key="MECH_KEY" origin="origin_mechanists" }
            { name="Another Ringworld" key="RING_KEY_2" origin="origin_shattered_ring" }
            { name="No Origin Empire" key="NO_ORIGIN_KEY" species={ class="HUM" } } # Wird herausgefiltert
            { name="Hive Mind 2" key="HIVE_KEY_2" origin="origin_progenitor_hive" ethic="ethic_gestalt_consciousness" }
            { origin="origin_default" key="DEFAULT_ORIGIN_EMPIRE" } # Imperium mit Standard-Origin
            { key="LONE_SURVIVOR" origin="origin_lone_survivor" }
            """
            try:
                with open(input_filepath, 'w', encoding='utf-8') as f:
                    f.write(dummy_content_origins)
                print(f"Dummy-Datei '{input_filepath}' erfolgreich erstellt. Bitte das Skript erneut ausführen.")
                exit() 
            except IOError as e:
                print(f"Fehler beim Erstellen der Dummy-Datei: {e}")
                exit()
        else:
            print("Skript wird fortgesetzt. Wenn die Datei leer ist, wird kein Bericht erstellt.")
    
    if not parsed_origins_data:
        if os.path.exists(input_filepath): # Datei existiert, aber keine Daten geparst
            print(f"Keine Imperien mit Origins in '{input_filepath}' gefunden oder Datei ist leer/fehlerhaft.")
        print("Keine Daten zur Verarbeitung vorhanden.")
    else:
        print(f"{len(parsed_origins_data)} Imperien mit Origins geparst.")

        # 2. Gruppiere Imperien nach ihrem Origin
        grouped_by_origin = group_empires_by_origin(parsed_origins_data)
        print(f"{len(grouped_by_origin)} einzigartige Origins gefunden.")

        # 3. Bereite Daten für die CSV-Ausgabe vor
        data_for_csv_output = prepare_origin_data_for_csv(grouped_by_origin)
        
        # 4. Schreibe in CSV
        write_origins_csv(data_for_csv_output, output_csv_filepath)