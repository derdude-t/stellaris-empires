import sys
import os
import tempfile
import shutil

def process_lines(reader, writer):
    """
    Liest Zeilen vom Reader, entfernt leere Zeilen und schreibt
    die nicht-leeren Zeilen (mit ihrem ursprünglichen Zeilenumbruch) zum Writer.
    """
    for line_with_newline in reader:
        # Zeile ohne Zeilenumbruch für die Prüfung
        line_for_check = line_with_newline.rstrip('\n')
        # Eine Zeile ist "leer", wenn sie nach dem Entfernen von Leerzeichen leer ist
        if line_for_check.strip():  # line_for_check.strip() ist True, wenn nicht leer
            writer.write(line_with_newline) # Schreibe die Originalzeile mit Zeilenumbruch

def main():
    args = sys.argv
    script_name = os.path.basename(sys.argv[0])

    try:
        if len(args) == 1:
            # Keine Argumente: Lese von stdin, schreibe nach stdout
            process_lines(sys.stdin, sys.stdout)
        elif len(args) == 2:
            # Ein Argument: Lese von angegebener Datei, schreibe nach stdout
            input_path = args[1]
            with open(input_path, 'r', encoding='utf-8') as reader:
                process_lines(reader, sys.stdout)
        elif len(args) == 3:
            input_path = args[1]
            output_path = args[2]

            # Prüfen, ob es sich um eine In-Place-Bearbeitung handelt
            # (d.h. Eingabe- und Ausgabepfad sind identisch)
            if os.path.abspath(input_path) == os.path.abspath(output_path):
                temp_file_path = None # Für den finally-Block
                try:
                    # Erstelle eine temporäre Datei im selben Verzeichnis wie die Quelldatei
                    # um ein atomares Verschieben (shutil.move) zu ermöglichen.
                    # delete=False, damit wir sie manuell umbenennen/verschieben können.
                    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8',
                                                     dir=os.path.dirname(input_path) or '.', # dir='.' falls input_path nur Dateiname ist
                                                     prefix="." + os.path.basename(input_path) + "_tmp_", # z.B. .meineDatei.txt_tmp_xyz
                                                     delete=False) as tmp_writer:
                        temp_file_path = tmp_writer.name
                        with open(input_path, 'r', encoding='utf-8') as reader:
                            process_lines(reader, tmp_writer)
                    
                    # Ersetze die Originaldatei atomar durch die temporäre Datei
                    shutil.move(temp_file_path, input_path)
                    temp_file_path = None # Signalisiert, dass die Datei erfolgreich verschoben wurde
                finally:
                    # Wenn temp_file_path noch gesetzt ist (d.h. das Verschieben ist fehlgeschlagen
                    # oder ein Fehler ist vorher aufgetreten), lösche die temporäre Datei.
                    if temp_file_path and os.path.exists(temp_file_path):
                        os.remove(temp_file_path)
            else:
                # Zwei unterschiedliche Argumente: Lese von input_file, schreibe nach output_file
                with open(input_path, 'r', encoding='utf-8') as reader:
                    with open(output_path, 'w', encoding='utf-8') as writer:
                        process_lines(reader, writer)
        else:
            # Zu viele Argumente: Zeige usage und beende mit Fehler
            print(f"Benutzung: {script_name} [<EingabeDatei> [<AusgabeDatei>]]", file=sys.stderr)
            sys.exit(1)

    except FileNotFoundError as e:
        print(f"Fehler: Datei '{e.filename}' nicht gefunden.", file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        # e.filename ist oft None bei stdin/stdout Problemen, daher vorsichtiger Zugriff
        filename_info = f"Datei '{e.filename}'" if e.filename else "Standard E/A"
        print(f"E/A-Fehler bei Zugriff auf {filename_info}: {e.strerror}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Ein unerwarteter Fehler ist aufgetreten: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()