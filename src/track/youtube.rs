use super::{empty_trackinfo, PlayableTrack, TrackInfo};
use serde_json::json;
use std::process::Command;

pub struct Youtube {
    source_uri: String,
    uri: String,
    info: TrackInfo,
    ytdlp_exe: String,
}

impl PlayableTrack for Youtube {
    fn refresh(&self) {
        let output = Command::new(self.ytdlp_exe.clone())
            .arg("-J")
            .arg("--no-download")
            .arg(format!("'{}'", self.uri))
            .output()
            .unwrap();

        let val = json!(String::from_utf8_lossy(&output.stdout));
    }

    fn is_expired(&self) -> bool {
        false
    }

    fn get_source(&mut self) -> rodio::Decoder<std::io::BufReader<std::fs::File>> {
        todo!()
    }

    fn info(&self) -> TrackInfo {
        todo!()
    }
}

pub fn track(uri: String) -> Youtube {
    Youtube {
        uri,
        source_uri: "".to_string(),
        info: empty_trackinfo(),
        ytdlp_exe: "yt-dlp.exe".to_string(),
    }
}
