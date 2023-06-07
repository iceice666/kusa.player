use rodio::Decoder;
use std::fs::File;
use std::io::BufReader;

use super::{empty_tackinfo, PlayableTrack, TrackInfo};

pub struct Local {
    source_uri: String,
    info: TrackInfo,
}

impl PlayableTrack for Local {
    fn is_expired(&self) -> bool {
        false
    }

    fn refresh(&mut self) {
        // Load a sound from a file, using a path relative to Cargo.toml
    }

    fn get_source(&mut self) -> Decoder<BufReader<File>> {
        if self.is_expired() {
            self.refresh();
        }

        // Decode that sound file into a source
        let file = File::open(self.source_uri.clone()).unwrap();
        let source = Decoder::new(BufReader::new(file)).unwrap();
        source
    }

    fn info(&self) -> TrackInfo {
        self.info.clone()
    }
}

pub fn track(source_uri: String) -> Local {
    Local {
        source_uri,
        info: empty_tackinfo(),
    }
}
