use crate::track::Playable;
use std::fs::File;

type AnyResult<T = ()> = anyhow::Result<T>;
use anyhow::anyhow;

use super::error::TrackError;
use super::Source;

pub struct LocalTrack {
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
    fn get_source(&self) -> &Source {
        &self.source
    }

    fn refresh(&mut self) -> AnyResult {
        if self.file.is_none() {
            self.file = File::open(&self.source.uri).ok();
        };

        Ok(())
    }

    fn check_available(&self) -> AnyResult {
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
}
