use crate::track::Playable;
use std::fs;
use std::fs::File;

use anyhow::Result as anyResult;

struct LocalTrack<'a> {
    uri: &'a str,
    available: bool,
}

impl Playable for LocalTrack<'a> {
    fn get_uri(&self) -> &'a str {
        todo!()
    }

    fn refresh(&mut self) {
        todo!()
    }

    fn is_available(&self) -> anyResult<bool> {
        let file = File::open(self.uri)?;

        Ok(file.metadata()?.is_file())
    }
}
