import re
import csv
import os
from collections import defaultdict

# === Parsing Logic ===

def parse_empire_portraits_and_key(empire_content_str):
    """
    Parst einen String-Block der Definition eines einzelnen Imperiums, um dessen Key,
    primäres Spezies-Portrait und sekundäres Spezies-Portrait zu extrahieren.
    """
    empire_key = None
    primary_portrait = None
    secondary_portrait = None

    # 1. Extrahiere den top-level Key des Imperiums
    key_match = re.search(r'^\s*key\s*=\s*"([^"]+)"', empire_content_str, re.MULTILINE)
    if key_match:
        empire_key = key_match.group(1)

    # 2. Extrahiere das primäre Spezies-Portrait
    # Das Regex sucht nach 'species = {', dann nicht-gierig nach beliebigen Zeichen 
    # (inkl. einfacher geschachtelter Blöcke), bis es 'portrait = "..."' findet.
    # (?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*? ist der Teil, der versucht, Inhalt 
    # innerhalb von Klammern zu navigieren, ohne durch andere einfache Blöcke verwirrt zu werden.
    primary_portrait_match = re.search(
        r'species\s*=\s*\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*?portrait\s*=\s*"([^"]+)"',
        empire_content_str,
        re.DOTALL  # re.DOTALL lässt '.' auch Newlines matchen
    )
    if primary_portrait_match:
        primary_portrait = primary_portrait_match.group(1)

    # 3. Extrahiere das sekundäre Spezies-Portrait (falls vorhanden)
    secondary_portrait_match = re.search(
        r'secondary_species\s*=\s*\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*?portrait\s*=\s*"([^"]+)"',
        empire_content_str,
        re.DOTALL
    )
    if secondary_portrait_match:
        secondary_portrait = secondary_portrait_match.group(1)
        
    return {'key': empire_key, 'primary_portrait': primary_portrait, 'secondary_portrait': secondary_portrait}


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

def extract_portraits_data_from_file(filepath="user_empire_designs_v3.4.txt"):
    """
    Liest die Stellaris User Empire Designs Datei, parst jedes Imperium
    und extrahiert Portrait-Instanzen (primär und sekundär).
    Gibt eine Liste von Dictionaries zurück: {'portrait_name': str, 'empire_key_ref': str}
    """
    try:
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            content = f.read()
    except FileNotFoundError:
        return [] # Wird im Hauptteil behandelt
    except Exception as e:
        print(f"Fehler beim Lesen der Datei '{filepath}': {e}")
        return []

    empire_block_strings = split_into_empire_blocks(content)
    all_portrait_occurrences = []
    
    for i, block_str in enumerate(empire_block_strings):
        empire_details = parse_empire_portraits_and_key(block_str)
        
        raw_empire_key = empire_details.get('key')
        # Verwende einen Platzhalter, falls ein Imperiumsblock überraschenderweise keinen Key hat, aber Portraits liefert
        if raw_empire_key is None:
            raw_empire_key = f"UNKNOWN_KEY_BLOCK_{i+1}" 

        if empire_details.get('primary_portrait'):
            all_portrait_occurrences.append({
                'portrait_name': empire_details['primary_portrait'],
                'empire_key_ref': raw_empire_key 
            })
        if empire_details.get('secondary_portrait'):
            all_portrait_occurrences.append({
                'portrait_name': empire_details['secondary_portrait'],
                'empire_key_ref': f"secondary_{raw_empire_key}" # Präfix für sekundäre Spezies
            })
            
    return all_portrait_occurrences

# === Data Grouping ===

def group_by_portrait_name(portrait_occurrences_list):
    """
    Gruppiert Portrait-Instanzen nach Portrait-Namen.
    """
    portrait_to_empires_map = defaultdict(list)
    for occurrence in portrait_occurrences_list:
        portrait_to_empires_map[occurrence['portrait_name']].append(occurrence['empire_key_ref'])
    return portrait_to_empires_map

# === CSV Preparation ===

def prepare_portrait_data_for_csv(portrait_to_empires_map):
    """
    Bereitet die gruppierten Portrait-Daten für die CSV-Ausgabe vor.
    Format: [[Anzahl, Portrait_Name, Liste_der_Empire_Key_Referenzen], ...]
    """
    data_for_csv = []
    for portrait_name, empire_key_refs_list in portrait_to_empires_map.items():
        count = len(empire_key_refs_list)
        data_for_csv.append([count, portrait_name, empire_key_refs_list])
    
    # Sortiere Daten: primär nach Portrait-Name (item[1]) für konsistente CSV-Ausgabe
    sorted_data_for_csv = sorted(data_for_csv, key=lambda item: item[1])
    return sorted_data_for_csv

# === CSV Output Function ===

def write_portraits_csv(data_for_csv, output_filepath="portraits_report.csv"):
    """
    Schreibt die Portrait-Daten in eine CSV-Datei, wobei Semikolon als Trennzeichen verwendet wird.
    """
    if not data_for_csv:
        print("Keine Daten zum Schreiben in CSV vorhanden.")
        return

    try:
        with open(output_filepath, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=';')
            
            # Header: N;Name;Reiche
            csv_writer.writerow(['N', 'Name', 'Reiche'])
            
            for count, portrait_name, empire_key_refs_list in data_for_csv:
                # Füge Imperiums-Key-Referenzen mit Semikolon zusammen.
                # Das csv-Modul wird das Feld automatisch in Anführungszeichen setzen,
                # wenn es das Trennzeichen (Semikolon) enthält.
                keys_str = ";".join(sorted(empire_key_refs_list)) 
                
                csv_writer.writerow([count, portrait_name, keys_str])
        print(f"\nCSV-Datei erfolgreich geschrieben: {output_filepath}")
    except IOError as e:
        print(f"Fehler beim Schreiben der CSV-Datei '{output_filepath}': {e}")

# === Main Execution ===
if __name__ == "__main__":
    input_filepath = "user_empire_designs_v3.4.txt"
    output_csv_filepath = "portraits_report.csv"

    print(f"Starte Analyse der Species Portraits aus: {input_filepath}")

    # 1. Extrahiere Portrait-Daten aus der Datei
    parsed_portrait_data = extract_portraits_data_from_file(input_filepath)
    
    if not os.path.exists(input_filepath):
        print(f"\nDatei '{input_filepath}' nicht gefunden.")
        dummy_q = input(f"Möchten Sie eine Dummy-Datei '{input_filepath}' für Testzwecke erstellen? (j/n): ").lower()
        if dummy_q == 'j':
            dummy_content_portraits = """
            empire_one = {
                key="EMP_ALPHA"
                # some other empire data
                species={
                    class="HUM"
                    portrait="humanoid_01" # Primär
                    name="Humans"
                    plural="Humans"
                    adjective="Human"
                    # ... other species data
                }
                secondary_species={       # Sekundär
                    class="REP"
                    portrait="reptilian_05"
                    name="Vorgons"
                    # ... other secondary species data
                }
            }
            empire_two = {
                key="EMP_BETA"
                species={
                    class="MAM"
                    portrait="molluscoid_02" # Primär
                    traits = { trait_adaptive trait_nomadic }
                }
                # Keine sekundäre Spezies
            }
            empire_three = {
                key="EMP_GAMMA"
                species={
                    class="FUN"
                    portrait="fungoid_03" # Primär
                }
                secondary_species={
                    class="AVI"
                    portrait="avian_01" # Sekundär
                }
            }
            empire_four = {
                # Kein Key zum Testen des Platzhalters
                species={
                    portrait="humanoid_01" # Primär, wie bei EMP_ALPHA
                }
            }
            empire_five = {
                key="EMP_DELTA"
                # Kein species-Block, oder kein Portrait im species-Block
            }
            empire_six = {
                key="EMP_EPSILON"
                species={
                    # portrait fehlt hier
                    name="Nameless Ones"
                }
                secondary_species={
                    portrait="molluscoid_02" # Sekundär, wie EMP_BETA primär
                }
            }
            """
            try:
                with open(input_filepath, 'w', encoding='utf-8') as f:
                    f.write(dummy_content_portraits)
                print(f"Dummy-Datei '{input_filepath}' erfolgreich erstellt. Bitte das Skript erneut ausführen.")
                exit()
            except IOError as e:
                print(f"Fehler beim Erstellen der Dummy-Datei: {e}")
                exit()
        else:
            print("Skript wird fortgesetzt. Wenn die Datei leer ist, wird kein Bericht erstellt.")
    
    if not parsed_portrait_data:
        if os.path.exists(input_filepath):
            print(f"Keine Portrait-Daten in '{input_filepath}' gefunden oder Datei ist leer/fehlerhaft.")
        # Wenn Datei nicht existierte und Nutzer keine Dummy-Datei wollte, führt dieser Pfad auch zu keinen Daten.
        print("Keine Daten zur Verarbeitung vorhanden.")
    else:
        print(f"{len(parsed_portrait_data)} Portrait-Instanzen (primär/sekundär) gefunden.")

        # 2. Gruppiere Instanzen nach Portrait-Name
        grouped_by_portrait = group_by_portrait_name(parsed_portrait_data)
        print(f"{len(grouped_by_portrait)} einzigartige Portraits gefunden.")

        # 3. Bereite Daten für die CSV-Ausgabe vor
        data_for_csv_output = prepare_portrait_data_for_csv(grouped_by_portrait)
        
        # 4. Schreibe in CSV
        write_portraits_csv(data_for_csv_output, output_csv_filepath)