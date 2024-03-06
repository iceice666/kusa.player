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
    fn get_source(&self) -> AnyResult<Self::Source> {
        self.refresh()?;

        let path = File::open(&self.file_path)?;
        let buf = BufReader::new(path);

        Ok(buf)
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

    use super::super::simple_player::new_player;
    use super::*;

    type AnyResult<T = ()> = anyhow::Result<T>;
    #[test]
    fn file_path() -> AnyResult {
        let track = LocalTrack::new("assets/ViRTUS.m4a");
        println!("{:#?}", track);

        let (_stream, stream_handle) = OutputStream::try_default().unwrap();
        let sink = Sink::try_new(&stream_handle).unwrap();
        println!("New sink");

        let dec = Decoder::new(track.get_source()?)?;
        println!("New decoded source");

        sink.append(dec);
        println!("Appended to sink");

        sink.play();
        println!("Playing");

        std::thread::sleep(std::time::Duration::from_secs(60));

        Ok(())
    }
}
