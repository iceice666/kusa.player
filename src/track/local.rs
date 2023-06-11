use super::{empty_trackinfo, PlayableTrack, TrackInfo};
use anyhow::Result;
use rodio::{Decoder, Sink};
use std::fs::File;
use std::io::BufReader;

pub struct Local {
    source_uri: String,
    info: TrackInfo,
}

impl PlayableTrack for Local {
    fn is_expired(&self) -> bool {
        false
    }

    fn refresh(&mut self) {}

    fn play(&mut self, sink: Sink) -> Result<()> {
        // Decode that sound file into a source
        let file = File::open(self.source_uri.clone()).unwrap();
        let source = Decoder::new(BufReader::new(file)).unwrap();

        sink.append(source);
        sink.sleep_until_end();

        Ok(())
    }

    fn info(&self) -> TrackInfo {
        self.info.clone()
    }
}

pub fn track(source_uri: String) -> Local {
    Local {
        source_uri,
        info: empty_trackinfo(),
    }
}
