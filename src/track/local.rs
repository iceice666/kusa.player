use rodio::decoder::DecoderError;
use rodio::{Decoder, OutputStream, Sink};
use std::fs::File;
use std::io::BufReader;

use super::Track;

pub struct Local {
    pub source_uri: String,
}

impl Track for Local {
    fn is_expired(&self) -> bool {
        false
    }

    fn play(&self) {
        // Get a output stream handle to the default physical sound device
        let (_stream, stream_handle) = OutputStream::try_default().unwrap();
        let sink = Sink::try_new(&stream_handle).unwrap();

        // Load a sound from a file, using a path relative to Cargo.toml
        let file = BufReader::new(File::open(&self.source_uri).unwrap());

        // Decode that sound file into a source
        let source = match Decoder::new(file) {
            Ok(v) => v,
            Err(e) => match e {
                DecoderError::IoError(err) => {
                    print!("IoError {}", err);
                    return;
                }
                DecoderError::DecodeError(err) => {
                    print!("DecodeError {}", err);
                    return;
                }
                DecoderError::LimitError(err) => {
                    print!("LimitError {}", err);
                    return;
                }
                _ => {
                    return;
                }
            },
        };

        // Play the sound directly on the device
        sink.append(source);

        // The sound plays in a separate thread. This call will block the current thread until the sink
        // has finished playing all its queued sounds.
        sink.sleep_until_end();
    }

    fn refresh(&self) -> String {
        self.source_uri.clone()
    }
}
