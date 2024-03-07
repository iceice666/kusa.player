use rodio::Decoder;
use std::{collections::HashMap, fs::File, io::BufReader, path::Path};
use tracing::instrument;

use super::Track;

type AnyResult<T = ()> = anyhow::Result<T>;

#[derive(Debug)]
struct LocalTrack {
    file_path: String,
}

impl LocalTrack {
    pub fn new(file_path: &str) -> LocalTrack {
        LocalTrack {
            file_path: file_path.to_string(),
        }
    }
}

impl Track for LocalTrack {
    type Source = BufReader<File>;

    #[instrument]
    fn refresh(&self) -> AnyResult {
        let path = Path::new(&self.file_path);

        match path.exists() {
            true => {
                // Nothing to do here
                Ok(())
            }
            false => Err(anyhow::anyhow!("File does not exist: {}", self.file_path)),
        }
    }

    #[instrument]
    fn get_decoded_source(&self) -> AnyResult<Decoder<Self::Source>> {
        self.refresh()?;

        let path = File::open(&self.file_path)?;
        let buf = BufReader::new(path);
        let dec = Decoder::new(buf)?;

        Ok(dec)
    }

    #[instrument]
    fn get_metadata(&self) -> AnyResult<HashMap<String, String>> {
        Ok(HashMap::new())
    }
}

#[cfg(test)]
mod test {
    use rodio::Decoder;

    use rodio::{OutputStream, Sink};

    use tracing::info;

    use super::*;

    type AnyResult<T = ()> = anyhow::Result<T>;
    #[test]
    fn file_path() -> AnyResult {
        tracing_subscriber::fmt::init();

        let track = LocalTrack::new("assets/ViRTUS.m4a");
        info!("{:#?}", track);

        let (_stream, stream_handle) = OutputStream::try_default().unwrap();
        let sink = Sink::try_new(&stream_handle).unwrap();
        info!("New sink");

        sink.set_volume(0.1);

        let dec = track.get_decoded_source()?;
        info!("New decoded source");

        sink.append(dec);
        info!("Appended to sink");

        sink.play();
        info!("Playing");

        sink.sleep_until_end();
        info!("End");

        std::thread::sleep(std::time::Duration::from_secs(5));
        info!("Wait for 5 secs");

        let dec = track.get_decoded_source()?;
        info!("Prepare to play again");

        sink.append(dec);
        info!("Appended to sink");

        sink.play();
        info!("Playing");

        sink.sleep_until_end();
        info!("End");

        Ok(())
    }
}
