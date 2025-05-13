use std::io::{self, BufRead, BufWriter, Write};
use std::fs::File;
use std::env;
use std::process;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<String> = env::args().collect();

    // Entscheide, woher gelesen und wohin geschrieben werden soll
    let (reader, writer): (Box<dyn BufRead>, Box<dyn Write>) = match args.len() {
        1 => {
            // Keine Argumente: Lese von stdin, schreibe nach stdout
            (Box::new(io::BufReader::new(io::stdin())),
             Box::new(io::BufWriter::new(io::stdout())))
        },
        2 => {
            // Ein Argument: Lese von angegebener Datei, schreibe nach stdout
            let input_path = &args[1];
            let input_file = File::open(input_path)?;
            (Box::new(io::BufReader::new(input_file)),
             Box::new(io::BufWriter::new(io::stdout())))
        },
        3 => {
            // Zwei Argumente: Lese von input_file, schreibe nach output_file
            let input_path = &args[1];
            let output_path = &args[2];
            let input_file = File::open(input_path)?;
            let output_file = File::create(output_path)?;
            (Box::new(io::BufReader::new(input_file)),
             Box::new(io::BufWriter::new(output_file)))
        },
        _ => {
            // Zu viele Argumente: Zeige usage und beende mit Fehler
            eprintln!("Benutzung: {} [<EingabeDatei> [<AusgabeDatei>]]", args[0]);
            process::exit(1);
        }
    };

    let mut reader = reader; // Iterator benötigt Mutabilität
    let mut writer = writer;

    // Verarbeite jede Zeile
    for line_result in reader.lines() {
        let line = line_result?; // Behandelt mögliche Lese-Fehler

        // Eine Zeile ist "leer", wenn sie nach dem Entfernen von Leerzeichen leer ist
        if !line.trim().is_empty() {
            writeln!(writer, "{}", line)?; // Schreibe die Zeile und füge den Zeilenumbruch wieder hinzu
        }
    }

    writer.flush()?; // Stelle sicher, dass alle gepufferten Daten geschrieben sind

    Ok(()) // Erfolg
}