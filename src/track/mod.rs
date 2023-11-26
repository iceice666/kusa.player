use std::error::Error;

use anyhow::Result as anyResult;
mod local;

pub trait Playable {
    // Player will get the uri and play it
    fn get_uri(&self) -> &str;
    // Player will run it when `is_available` is false
    fn refresh(&mut self);
    // This method will be called to check the playable source is available
    fn is_available(&self) -> anyResult<bool>;
}

struct TestTrack<'a> {
    uri: &'a str,
    available: bool,
}

impl<'a> TestTrack<'a> {
    fn new(uri: &'a str) -> Self {
        Self {
            uri,
            available: false,
        }
    }

    fn get_uri(&self) -> &'a str {
        println!("uri: {}", self.uri);
        self.uri
    }

    fn refresh(&mut self) {
        println!("refresh");
        let yee = "another uri";
        self.uri = yee;
    }

    fn is_available(&self) -> bool {
        self.available
    }
}
