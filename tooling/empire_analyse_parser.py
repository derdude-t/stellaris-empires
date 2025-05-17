import re
from enum import Enum

# Schritt 1: Enum für Stellaris Ethiken definieren (mit abgekürzten Namen)
class StellarisEthic(Enum):
    # Xenophil vs. Xenophob
    XIL = "ethic_xenophile"
    FAN_XIL = "ethic_fanatic_xenophile"
    XOB = "ethic_xenophobe"
    FAN_XOB = "ethic_fanatic_xenophobe"

    # Egalitär vs. Autoritär
    EGA = "ethic_egalitarian"
    FAN_EGA = "ethic_fanatic_egalitarian"
    AUT = "ethic_authoritarian"
    FAN_AUT = "ethic_fanatic_authoritarian"

    # Materialistisch vs. Spiritualistisch
    MAT = "ethic_materialist"
    FAN_MAT = "ethic_fanatic_materialist"
    SPI = "ethic_spiritualist"
    FAN_SPI = "ethic_fanatic_spiritualist"

    # Pazifist vs. Militarist
    PAC = "ethic_pacifist"
    FAN_PAC = "ethic_fanatic_pacifist"
    MIL = "ethic_militarist"
    FAN_MIL = "ethic_fanatic_militarist"

    # Gestaltbewusstsein
    GES = "ethic_gestalt_consciousness" # Abkürzung für Gestalt, anpassbar

    @classmethod
    def from_string(cls, s):
        try:
            return cls(s)  # Sucht nach dem Wert (z.B. "ethic_xenophile")
        except ValueError:
            print(f"Warnung: Unbekannte Ethik '{s}' gefunden und ignoriert.")
            return None

# Funktion zum Parsen von Key und Ethiken aus dem Inhalt eines einzelnen Imperiumblocks
# (bleibt unverändert zur vorherigen Version)
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

# Funktion zum Aufteilen des Datei-Inhalts in einzelne Imperiumsblöcke
# (bleibt unverändert zur vorherigen Version)
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
            elif balance < 0:
                print("Warnung: Potenziell fehlerhafte Klammerstruktur in der Datei entdeckt.")
                balance = 0
                current_block_start_index = -1
    return empire_blocks_content

# Hauptfunktion zum Transformieren der Imperiumsdesigns
# (bleibt unverändert zur vorherigen Version)
def transform_empire_designs(filepath="user_empire_designs_v3.4.txt"):
    try:
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Fehler: Datei '{filepath}' nicht gefunden.")
        return []
    except Exception as e:
        print(f"Fehler beim Lesen der Datei '{filepath}': {e}")
        return []

    empire_content_strings = split_into_empire_blocks(content)
    parsed_empires_data = []

    if not empire_content_strings:
        print("Keine Imperiumsblöcke in der Datei gefunden.")

    for i, block_str in enumerate(empire_content_strings):
        empire_data = parse_empire_data_from_block(block_str)
        
        if empire_data['ethics']:
            parsed_empires_data.append(empire_data)
        elif empire_data['key']:
            print(f"Hinweis: Imperium mit Key '{empire_data['key']}' besitzt keine Ethiken und wird daher nicht in der kategorisierten Liste geführt.")

    return parsed_empires_data

# Beispielhafte Verwendung des Skripts
if __name__ == "__main__":
    dummy_filepath = "user_empire_designs_v3.4.txt"
    dummy_content_v3 = """
{
    name="Human Commonwealth"
    key="HUMAN_COMMONWEALTH_KEY"
    ethic="ethic_xenophile"      # Wird zu XIL
    ethic="ethic_egalitarian"    # Wird zu EGA
    ethic="ethic_materialist"    # Wird zu MAT
}
{
    name="Ix'Idar Star Collective"
    key="IXIDAR_COLLECTIVE_KEY"
    ethic="ethic_gestalt_consciousness" # Wird zu GES
}
{
    name="Kroll Hegemony"
    key="KROLL_HEGEMONY_KEY"
    ethic="ethic_fanatic_authoritarian" # Wird zu FAN_AUT
    ethic="ethic_militarist"            # Wird zu MIL
}
{
    name="Spiritual Seekers"
    key="SPIRIT_SEEKERS_KEY"
    ethic="ethic_fanatic_spiritualist" # Wird zu FAN_SPI
    ethic="ethic_pacifist"             # Wird zu PAC
}
{
    name="Xenophobic Isolationists"
    key="XENO_ISO_KEY"
    ethic="ethic_fanatic_xenophobe"   # Wird zu FAN_XOB
}
    """
    #with open(dummy_filepath, 'w', encoding='utf-8') as f:
    #    f.write(dummy_content_v3)

    transformed_data = transform_empire_designs(dummy_filepath)

    if transformed_data:
        print("\n--- Transformierte Imperiums-Daten (Key und abgekürzte Ethiken) ---")
        for i, empire_info in enumerate(transformed_data):
            empire_key_display = empire_info['key'] if empire_info['key'] is not None else "N/A"
            # Hier wird .name verwendet, was jetzt die Abkürzungen liefert
            ethic_names = [ethic.name for ethic in empire_info['ethics']]
            print(f"Imperium Eintrag {i+1}: Key='{empire_key_display}', Ethiken={ethic_names}")
    else:
        print("Keine Imperien mit Ethiken gefunden oder Datei konnte nicht verarbeitet werden.")

    # import os
    # os.remove(dummy_filepath)