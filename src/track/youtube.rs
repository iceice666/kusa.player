use super::error::YoutubeTrackError;
use super::{Playable, Source, SourceType};
use std::process::Command;

type AnyResult<T = ()> = anyhow::Result<T>;
pub struct YoutubeTrack {
    source: Source,
}

fn resolve_url(url: &String) -> AnyResult<Vec<String>> {
    let output = Command::new("yt-dlp")
        .args(["--format", "m4a", "--print", "urls", url])
        .output()?;

    if output.status.success() {
        let resolved_urls: Vec<String> = String::from_utf8_lossy(&output.stdout)
            .to_string()
            .split("\n")
            .map(|v| v.to_string())
            .collect();

        Ok(resolved_urls)
    } else {
        Err(anyhow::anyhow!(YoutubeTrackError::YtdlpExitedUnexpectedly(
            String::from_utf8_lossy(&output.stderr).to_string()
        )))
    }
}

impl YoutubeTrack {
    pub fn new(url: String) -> AnyResult<Vec<YoutubeTrack>> {
        Ok(resolve_url(&url)?
            .into_iter()
            .map(|v| YoutubeTrack {
                source: Source {
                    uri: v,
                    source_type: SourceType::RemoteFile,
                },
            })
            .collect())
    }
}

impl Playable for YoutubeTrack {
    fn get_source(&self) -> &Source {
        &self.source
    }

    fn refresh(&mut self) -> AnyResult {
        let url = &self.source.uri;

        let ru = &resolve_url(&url)?[0];

        self.source = Source {
            uri: ru.to_string(),
            source_type: SourceType::RemoteFile,
        };

        Ok(())
    }

    fn check_available(&self) -> AnyResult {
        Ok(())
    }
}
