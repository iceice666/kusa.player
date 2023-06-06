use rodio::decoder::DecoderError;
use rodio::Decoder;
use std::fs::File;
use std::io::BufReader;

use super::PlayableTrack;

pub struct Local {
    source_uri: String,
}

impl PlayableTrack for Local {
    fn is_expired(&self) -> bool {
        false
    }

    fn refresh(&mut self) {
        // Load a sound from a file, using a path relative to Cargo.toml
    }

    fn get_source(&mut self) -> Option<Decoder<BufReader<File>>> {
        if self.is_expired() {
            self.refresh();
        }

        // Decode that sound file into a source
        let file = File::open(&self.source_uri).unwrap();
        let source = match Decoder::new(BufReader::new(file)) {
            Ok(v) => Some(v),
            Err(e) => match e {
                DecoderError::IoError(err) => {
                    print!("IoError {}", err);
                    return None;
                }
                DecoderError::DecodeError(err) => {
                    print!("DecodeError {}", err);
                    return None;
                }
                DecoderError::LimitError(err) => {
                    print!("LimitError {}", err);
                    return None;
                }
                _ => {
                    return None;
                }
            },
        };

        source
    }
}

pub fn track(source_uri: String) -> Local {
    Local { source_uri }
}
