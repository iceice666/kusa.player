use std::error::Error;

use anyhow::Result as anyResult;
mod local;

pub type Track = Box<dyn Playable>;

pub trait Playable {
    // Player will get the uri and play it
    fn get_source(&self) -> &Source;
    // Player will run it when `is_available` is false
    fn refresh(&mut self) {}
    // This method will be called to check the playable source is available
    fn is_available(&self) -> anyResult<()> {
        Ok(())
    }
}

#[derive(Debug)]
pub enum SourceType {
    LocalFile,
    RemoteFile,
    Stream,
    Empty,
}

#[derive(Debug)]
pub struct Source {
    pub(crate) uri: String,
    pub(crate) source_type: SourceType,
}

pub struct EmptyTrack {
    source: Source,
}

impl EmptyTrack {
    pub fn new() -> EmptyTrack {
        EmptyTrack {
            source: Source {
                uri: String::new(),
                source_type: SourceType::Empty,
            },
        }
    }
}

impl Playable for EmptyTrack {
    fn get_source(&self) -> &Source {
        &self.source
    }
}
