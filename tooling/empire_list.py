import re
from enum import Enum
from collections import defaultdict
import itertools # Für Kombinationen
import csv       # Für CSV-Ausgabe
import os        # Für Dateiprüfung und Dummy-Erstellung

# === Enum Definition (aus vorherigem Skript) ===
class StellarisEthic(Enum):
    XIL = "ethic_xenophile"
    FAN_XIL = "ethic_fanatic_xenophile"
    XOB = "ethic_xenophobe"
    FAN_XOB = "ethic_fanatic_xenophobe"
    EGA = "ethic_egalitarian"
    FAN_EGA = "ethic_fanatic_egalitarian"
    AUT = "ethic_authoritarian"
    FAN_AUT = "ethic_fanatic_authoritarian"
    MAT = "ethic_materialist"
    FAN_MAT = "ethic_fanatic_materialist"
    SPI = "ethic_spiritualist"
    FAN_SPI = "ethic_fanatic_spiritualist"
    PAC = "ethic_pacifist"
    FAN_PAC = "ethic_fanatic_pacifist"
    MIL = "ethic_militarist"
    FAN_MIL = "ethic_fanatic_militarist"
    GES = "ethic_gestalt_consciousness"

    @classmethod
    def from_string(cls, s):
        try:
            return cls(s)
        except ValueError:
            # print(f"Warnung: Unbekannte Ethik '{s}' in Enum nicht definiert.")
            return None
    
    def is_fanatic(self):
        return self.name.startswith('FAN_')

    def is_simple(self): # Nicht-fanatisch und nicht-gestalt
        return not self.name.startswith('FAN_') and self != StellarisEthic.GES

# === Parsing Logic (aus vorherigem Skript, leicht angepasst für weniger Ausgaben) ===
def parse_empire_data_from_block(empire_content_str):
    ethics = []
    empire_key = None
    for line in empire_content_str.splitlines():
        line = line.strip()
        if line.startswith("key=") and empire_key is None:
            match = re.match(r'key="([^"]+)"', line)
            if match:
                empire_key = match.group(1)
        elif line.startswith("ethic="):
            match = re.match(r'ethic="([^"]+)"', line)
            if match:
                ethic_str = match.group(1)
                ethic_enum = StellarisEthic.from_string(ethic_str)
                if ethic_enum:
                    ethics.append(ethic_enum)
    return {'key': empire_key, 'ethics': ethics}

def split_into_empire_blocks(file_content):
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
            elif balance < 0: # Fehlerhafte Struktur minimal behandeln
                balance = 0
                current_block_start_index = -1
    return empire_blocks_content

def transform_empire_designs(filepath="user_empire_designs_v3.4.txt"):
    try:
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            content = f.read()
    except FileNotFoundError:
        return [] # Fehler wird im Hauptteil behandelt
    except Exception as e:
        print(f"Fehler beim Lesen der Datei '{filepath}': {e}")
        return []

    empire_content_strings = split_into_empire_blocks(content)
    parsed_empires_data = []
    
    for block_str in empire_content_strings:
        empire_data = parse_empire_data_from_block(block_str)
        if empire_data['ethics']: # Nur Imperien mit Ethiken berücksichtigen
            parsed_empires_data.append(empire_data)
    return parsed_empires_data

# === Ethic Categorization and Combination Generation ===
def define_ethic_attributes():
    """Definiert Ethik-Kategorien (einfach, fanatisch) und ihre Achsen."""
    simple_ethics = {e for e in StellarisEthic if e.is_simple()}
    fanatic_ethics = {e for e in StellarisEthic if e.is_fanatic()}
    
    ethic_to_axis = {}
    # Achsen-Definitionen basierend auf den Enum-Mitgliedern
    AXIS_DEFINITIONS = {
        'XENO': {StellarisEthic.XIL, StellarisEthic.FAN_XIL, StellarisEthic.XOB, StellarisEthic.FAN_XOB},
        'POLITIC': {StellarisEthic.EGA, StellarisEthic.FAN_EGA, StellarisEthic.AUT, StellarisEthic.FAN_AUT},
        'INTERNAL': {StellarisEthic.MAT, StellarisEthic.FAN_MAT, StellarisEthic.SPI, StellarisEthic.FAN_SPI},
        'WAR': {StellarisEthic.PAC, StellarisEthic.FAN_PAC, StellarisEthic.MIL, StellarisEthic.FAN_MIL}
    }
    for axis_name, ethics_in_axis in AXIS_DEFINITIONS.items():
        for ethic_enum in ethics_in_axis:
            ethic_to_axis[ethic_enum] = axis_name
            
    return simple_ethics, fanatic_ethics, ethic_to_axis

def generate_all_valid_ethic_combinations(simple_ethics, fanatic_ethics, ethic_to_axis):
    """Generiert alle validen Ethik-Kombinationen basierend auf Stellaris-Regeln."""
    all_combos_enums = set() # Ein Set von Tupeln von Enum-Mitgliedern

    # Regel 1: GES ist allein
    # Das Tupel wird sortiert (obwohl nur ein Element), um Konsistenz zu wahren
    all_combos_enums.add(tuple(sorted([StellarisEthic.GES], key=lambda e: e.name)))

    # Regel 2: 1 Fanatische + 1 Einfache Ethik (insgesamt 2 Ethiken, 3 Ethikpunkte)
    # Ethiken müssen von unterschiedlichen Achsen stammen.
    for f_ethic in fanatic_ethics:
        for s_ethic in simple_ethics:
            # Prüfe, ob beide Ethiken einer Achse zugeordnet sind und ob diese unterschiedlich sind
            f_axis = ethic_to_axis.get(f_ethic)
            s_axis = ethic_to_axis.get(s_ethic)
            if f_axis is not None and s_axis is not None and f_axis != s_axis:
                combo = tuple(sorted((f_ethic, s_ethic), key=lambda e: e.name))
                all_combos_enums.add(combo)

    # Regel 3: 3 Einfache Ethiken (insgesamt 3 Ethiken, 3 Ethikpunkte)
    # Alle 3 Ethiken müssen von unterschiedlichen Achsen stammen.
    for combo_candidate in itertools.combinations(simple_ethics, 3):
        axes_in_combo = {ethic_to_axis.get(e) for e in combo_candidate}
        # Stelle sicher, dass alle Ethiken eine Achse haben und es 3 unterschiedliche Achsen sind
        if None not in axes_in_combo and len(axes_in_combo) == 3:
            combo = tuple(sorted(combo_candidate, key=lambda e: e.name))
            all_combos_enums.add(combo)
            
    return all_combos_enums

# === Data Grouping and Preparation for CSV ===
def group_empires_by_ethics(parsed_empires_data):
    ethics_to_empires_map = defaultdict(list)
    for i, empire_data in enumerate(parsed_empires_data):
        # Verwende einen Platzhalter, falls ein Key fehlt (sollte laut Annahme nicht oft vorkommen)
        empire_key = empire_data['key'] if empire_data['key'] is not None else f"KEY_MISSING_EMPIRE_{i+1}"
        
        # Ethik-Namen sortieren für einen kanonischen Schlüssel
        ethic_names = sorted([ethic.name for ethic in empire_data['ethics']])
        ethics_combination_key = tuple(ethic_names) # Tupel von Strings (z.B. ('AUT', 'MIL'))
        
        ethics_to_empires_map[ethics_combination_key].append(empire_key)
    return ethics_to_empires_map

def prepare_data_for_csv(all_possible_combos_enums, actual_ethics_to_empires_map):
    """Bereitet die finale Datenliste für die CSV-Ausgabe vor."""
    data_for_csv = [] # Liste von Listen: [[Tuple_Ethik_Namen, Liste_Imperium_Keys], ...]
    
    for combo_enums_tuple in all_possible_combos_enums:
        # Konvertiere das Tupel von Enum-Mitgliedern zu einem sortierten Tupel von Ethik-Namen (Strings)
        # Dies dient als Schlüssel für die `actual_ethics_to_empires_map`
        combo_names_tuple = tuple(sorted([e.name for e in combo_enums_tuple]))
        
        empire_keys_list = actual_ethics_to_empires_map.get(combo_names_tuple, []) # Standard: leere Liste
        data_for_csv.append([combo_names_tuple, empire_keys_list])
        
    # Sortiere die gesamte Liste basierend auf dem Ethik-Kombinationstupel für eine konsistente CSV-Ausgabe
    # Tuples werden elementweise verglichen, was für sortierte Namenstuppel gut funktioniert.
    sorted_data_for_csv = sorted(data_for_csv, key=lambda item: item[0])
    
    return sorted_data_for_csv

# === CSV Output Function ===
def write_ethics_csv(data_for_csv, output_filepath="ethics_combinations_report.csv"):
    """Schreibt die Ethik-Kombinationen und zugehörigen Imperien in eine CSV-Datei."""
    if not data_for_csv:
        print("Keine Daten zum Schreiben in CSV vorhanden.")
        return

    try:
        with open(output_filepath, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            # Schreibe den Header
            csv_writer.writerow(['EthicsCombination', 'EmpireKeys'])
            
            for combo_names_tuple, empire_keys_list in data_for_csv:
                # Formatiere die Ethik-Kombination als einen String, getrennt durch Semikolons
                combo_str = ";".join(combo_names_tuple)
                # Formatiere die Liste der Imperiums-Keys als einen String, getrennt durch Semikolons
                # Sortiere die Keys für konsistente Ausgabe, falls mehrere vorhanden sind
                keys_str = ";".join(sorted(empire_keys_list))
                
                csv_writer.writerow([combo_str, keys_str])
        print(f"\nCSV-Datei erfolgreich geschrieben: {output_filepath}")
    except IOError as e:
        print(f"Fehler beim Schreiben der CSV-Datei '{output_filepath}': {e}")

# === Main Execution ===
if __name__ == "__main__":
    input_filepath = "user_empire_designs_v3.4.txt"
    output_csv_filepath = "ethics_combinations_report.csv"

    print(f"Starte Analyse für Ethik-Kombinationen aus: {input_filepath}")

    # 1. Parse actual empire designs from the file
    parsed_empire_data = transform_empire_designs(input_filepath)
    
    # Behandle den Fall, dass die Eingabedatei nicht existiert oder leer ist
    if not os.path.exists(input_filepath):
        print(f"\nDatei '{input_filepath}' nicht gefunden.")
        dummy_q = input(f"Möchten Sie eine Dummy-Datei '{input_filepath}' für Testzwecke erstellen? (j/n): ").lower()
        if dummy_q == 'j':
            dummy_content_for_analyzer = """
            { name="Alpha Centauri Primus" key="ACP_KEY" ethic="ethic_xenophile" ethic="ethic_egalitarian" }
            { name="Solarian Concord" key="SOL_CON_KEY" ethic="ethic_egalitarian" ethic="ethic_xenophile"}
            { name="Void Cultists" key="VOID_CULT_KEY" ethic="ethic_fanatic_spiritualist" ethic="ethic_xenophobe"}
            { name="Machine Uprising Zero" key="MUZ_KEY" ethic="ethic_gestalt_consciousness" }
            { name="Human Hegemony" key="HUM_HEG_KEY" ethic="ethic_authoritarian" ethic="ethic_militarist" }
            { name="Pacifist Traders" key="PAC_TRADE" ethic="ethic_pacifist" ethic="ethic_xenophile" ethic="ethic_materialist"}
            { name="Spiritual Dominators" key="SPI_DOM" ethic="ethic_fanatic_authoritarian" ethic="ethic_spiritualist"}
            """
            try:
                with open(input_filepath, 'w', encoding='utf-8') as f:
                    f.write(dummy_content_for_analyzer)
                print(f"Dummy-Datei '{input_filepath}' erfolgreich erstellt. Bitte das Skript erneut ausführen, um sie zu verwenden.")
                # Das Skript muss nach der Erstellung der Dummy-Datei erneut ausgeführt werden, um sie einzulesen.
                # Daher hier beenden oder die Logik anpassen, um direkt fortzufahren.
                # Für Einfachheit hier beenden.
                exit() 
            except IOError as e:
                print(f"Fehler beim Erstellen der Dummy-Datei: {e}")
                exit()
        else:
            print("Skript wird fortgesetzt, es werden nur theoretische Kombinationen ohne reale Imperien generiert (falls möglich).")
            # parsed_empire_data bleibt leer, was ok ist.
    elif not parsed_empire_data:
         print(f"Keine Imperien mit Ethiken in '{input_filepath}' gefunden, oder Datei ist leer.")


    # 2. Group actual empires by their ethics
    actual_ethics_to_empires_map = group_empires_by_ethics(parsed_empire_data)
    if parsed_empire_data: # Nur drucken, wenn Daten geparst wurden
        print(f"{len(parsed_empire_data)} Imperien mit Ethiken geparst.")
        print(f"{len(actual_ethics_to_empires_map)} einzigartige Ethik-Kombinationen in Verwendung gefunden.")

    # 3. Define ethic attributes (simple, fanatic, axes)
    simple_ethics_set, fanatic_ethics_set, ethic_to_axis_map = define_ethic_attributes()
    # print(f"\nDefinierte Attribute: {len(simple_ethics_set)} einfache Ethiken, {len(fanatic_ethics_set)} fanatische Ethiken.")

    # 4. Generate all theoretically valid ethic combinations
    all_possible_combos_enums_set = generate_all_valid_ethic_combinations(
        simple_ethics_set, fanatic_ethics_set, ethic_to_axis_map
    )
    print(f"{len(all_possible_combos_enums_set)} theoretisch valide Ethik-Kombinationen generiert.")
    
    # 5. Prepare data for CSV (map all valid combos to actual empires)
    final_data_for_csv = prepare_data_for_csv(all_possible_combos_enums_set, actual_ethics_to_empires_map)
    
    # 6. Write to CSV
    write_ethics_csv(final_data_for_csv, output_csv_filepath)