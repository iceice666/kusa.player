use serde_json::Value;
use std::{ffi::OsStr, path::PathBuf, process::Command};
use tracing::{debug, instrument};

#[derive(Debug)]
pub struct Ytdlp(PathBuf);

type AnyResult<T = ()> = anyhow::Result<T>;

#[derive(Debug)]
pub struct VideoInfo {
    id: String,
    title: String,
    description: String,
    webpage_url: String,
    channel: String,
    filename: String,
    is_live: bool,
    url: String,
}

impl Ytdlp {
    pub fn new(path: impl AsRef<OsStr>) -> Self {
        Self(PathBuf::from(path.as_ref()))
    }

    #[instrument]
    fn download(&self, url: &str) -> AnyResult {
        self.run(vec![url, "--no-playlist", "--format", "m4a"])?;

        unimplemented!();

        Ok(())
    }

    #[instrument]
    pub fn get_info(&self, url: &str) -> AnyResult<VideoInfo> {
        let data = self.run(vec![
            url,
            "--no-playlist",
            "--skip-download",
            "--dump-single-json",
            "--format",
            "m4a",
        ])?;

        let data = VideoInfo {
            id: data["id"].to_string().trim_matches('\"').to_string(),
            title: data["title"].to_string().trim_matches('\"').to_string(),
            description: data["description"]
                .to_string()
                .replace("\\n", "\n")
                .trim_matches('\"')
                .to_string(),
            webpage_url: data["webpage_url"]
                .to_string()
                .trim_matches('\"')
                .to_string(),
            channel: data["uploader"].to_string().trim_matches('\"').to_string(),
            filename: {
                let mut n = data["title"].to_string().trim_matches('\"').to_string();

                n.push_str(".m4a");

                n
            },
            is_live: data["is_live"].as_bool().unwrap_or(false),
            url: data["url"].to_string().trim_matches('\"').to_string(),
        };

        Ok(data)
    }

    #[instrument]
    fn run(&self, mut cmd: Vec<&str>) -> AnyResult<Value> {
        cmd.append(&mut vec!["--quiet", "--no-warnings"]);
        let output = Command::new(self.0.as_os_str()).args(cmd).output()?;

        debug!("status: {:?}", output.status);
        debug!("stdout: {}", String::from_utf8_lossy(&output.stdout));
        debug!("stderr: {}", String::from_utf8_lossy(&output.stderr));

        let data: Value = serde_json::from_str(String::from_utf8_lossy(&output.stdout).trim())?;

        Ok(data)
    }
}

#[cfg(test)]
mod test {
    use tracing::info;

    use super::*;

    #[test]
    fn test() -> AnyResult {
        tracing_subscriber::fmt::init();

        let client = Ytdlp::new("/usr/bin/yt-dlp");
        let res = client.get_info("https://www.youtube.com/watch?v=dQw4w9WgXcQ")?;
        info!("{:#?}", res);

        Ok(())
    }
}
