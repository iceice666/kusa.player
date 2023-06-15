use super::{empty_trackinfo, PlayableTrack, TrackInfo};
use crate::util::downloader::PartialRangeIter;
use anyhow::{bail, Result};
use reqwest::{
    header::{CONTENT_LENGTH, RANGE},
    StatusCode,
};
use rodio::{Decoder, Sink};
use std::{
    fs::{self, File},
    str::FromStr,
};
use std::{io::BufReader, process::Command};

pub struct Youtube {
    source_uri: String,
    uri: String,
    info: TrackInfo,
    ytdlp_exc: String,
    cached_file: String,
}

impl PlayableTrack for Youtube {
    fn is_expired(&self) -> bool {
        if 0 == fs::metadata(self.cached_file.clone()).unwrap().len() {
            true
        } else {
            false
        }
    }

    fn refresh(&mut self) {
        let output = Command::new(&self.ytdlp_exc)
            .args(["-g", "-f", "m4a", &self.uri])
            .output()
            .unwrap();

        self.source_uri = String::from_utf8_lossy(&output.stdout).trim().to_string();
    }

    fn play(&mut self, sink: Sink) -> Result<()> {
        let mut saved = File::create(&self.cached_file)?;

        if 0 == fs::metadata(self.cached_file.clone())?.len() {
            const CHUNK_SIZE: u32 = 10240;

            let client = reqwest::blocking::Client::new();
            let response = client.head(&self.source_uri).send()?;
            let length = match response.headers().get(CONTENT_LENGTH) {
                Some(v) => v,
                None => bail!("response doesn't include the content length"),
            };
            let length = u64::from_str(length.to_str()?)?;

            saved = File::create("music/download/save.m4a")?;
            println!("starting download...");
            for range in PartialRangeIter::new(0, length - 1, CHUNK_SIZE)? {
                println!("range {:?}", range);
                let mut response = client.get(&self.source_uri).header(RANGE, range).send()?;

                let status = response.status();
                if !(status == StatusCode::OK || status == StatusCode::PARTIAL_CONTENT) {
                    bail!("Unexpected server response: {}", status)
                }
                std::io::copy(&mut response, &mut saved)?;
            }

            let content = response.text()?;
            std::io::copy(&mut content.as_bytes(), &mut saved)?;

            saved.sync_all().expect("Failed to sync file");
        }

        let source = Decoder::new(BufReader::new(saved))?;

        println!("Finished with success!");

        sink.append(source);

        sink.sleep_until_end();
        Ok(())
    }

    fn info(&self) -> TrackInfo {
        self.info.clone()
    }
}

pub fn track(uri: String) -> Youtube {
    let mut cached_file: String = format!(
        "music/download/youtube.{}.m4a",
        uri.split(',').collect::<Vec<&str>>().pop().unwrap()
    );

    Youtube {
        cached_file,
        uri,
        source_uri: "".to_string(),
        info: empty_trackinfo(),
        ytdlp_exc: "yt-dlp.exe".to_string(),
    }
}
