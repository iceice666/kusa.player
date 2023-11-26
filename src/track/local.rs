use crate::track::Playable;
use std::fs::File;

use anyhow::anyhow;
use anyhow::Result as anyResult;

use super::Source;
use super::SourceType;

use crate::error::TrackError;

struct LocalTrack {
    source: Source,
    file: Option<File>,
}

impl LocalTrack {
    fn new(source: Source) -> LocalTrack {
        LocalTrack {
            file: File::open(&source.uri).ok(),
            source,
        }
    }
}

impl Playable for LocalTrack {
    fn refresh(&mut self) {
        if self.file.is_none() {
           self.file = File::open(&self.source.uri).ok();
        }
    }

    fn is_available(&self) -> anyResult<()> {
        if self.file.is_none() {
            return Err(anyhow!(TrackError::SourceIsMissing));
        }

        match self.file.as_ref().unwrap().metadata()?.is_file() {
            true => Ok(()),
            false => Err(anyhow!(TrackError::SourceIsNotAFile(
                self.source.uri.to_string()
            ))),
        }
    }

    fn get_source(&self) -> &Source {
        &self.source
    }
}
