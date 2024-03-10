use async_trait::async_trait;
use rodio::Decoder;
use std::{
    collections::HashMap,
    fs::File,
    io::BufReader,
    path::{Path, PathBuf},
};
use tracing::instrument;

use crate::track::{Metadata, Track};

type AnyResult<T = ()> = anyhow::Result<T>;

#[derive(Debug)]
pub(crate) struct LocalTrack {
    file_path: PathBuf,
    metadata: HashMap<String, String>,
}

impl LocalTrack {
    pub fn new(file_path: impl Into<String>, metadata: HashMap<String, String>) -> LocalTrack {
        LocalTrack {
            file_path: Path::new(&file_path.into()).to_path_buf(),
            metadata,
        }
    }
}

#[async_trait]
impl Track for LocalTrack {
    type Source = BufReader<File>;

    #[instrument]
    async fn get_decoded_source(&self) -> AnyResult<Decoder<Self::Source>> {
        let path = File::open(&self.file_path)?;
        let buf = BufReader::new(path);
        let dec = Decoder::new(buf)?;

        Ok(dec)
    }
}

impl Metadata for LocalTrack {
    fn metadata(&self) -> AnyResult<&HashMap<String, String>> {
        Ok(&self.metadata)
    }
}

#[cfg(test)]
mod test {
    use rodio::{OutputStream, Sink};

    use tracing::info;

    use super::*;

    type AnyResult<T = ()> = anyhow::Result<T>;

    #[tokio::test]
    async fn test() -> AnyResult {
        tracing_subscriber::fmt::init();

        let track = LocalTrack::new("assets/ViRTUS.m4a", HashMap::new());
        info!("{:#?}", track);

        let (_stream, stream_handle) = OutputStream::try_default().unwrap();
        let sink = Sink::try_new(&stream_handle).unwrap();
        info!("New sink");

        sink.set_volume(1.0);

        loop {
            let dec = track.get_decoded_source().await?;
            info!("New decoded source");

            sink.append(dec);
            info!("Appended to sink");

            sink.play();
            info!("Playing");

            sink.sleep_until_end();
            info!("End");
        }

        Ok(())
    }
}
