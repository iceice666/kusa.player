use super::error::TrackError;
use super::Playable;
use super::Source;
use super::SourceType;
use std::fs::File;

type AnyResult<T = ()> = anyhow::Result<T>;
use anyhow::anyhow;

#[derive(Debug)]
pub struct LocalTrack {
    source: Source,
    file: Option<File>,
}

impl LocalTrack {
    fn new(file_path: &String) -> LocalTrack {
        LocalTrack {
            file: File::open(file_path).ok(),
            source: Source {
                uri: file_path.to_string(),
                source_type: SourceType::LocalFile,
            },
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
            false => Err(anyhow!(TrackError::SourceIsNotAFile)),
        }
    }
}

#[cfg(test)]
mod test {

    use super::LocalTrack;

    #[test]
    fn teat_parser() {
        let path: String = "./media/local/test.wav".to_string();
        let track = LocalTrack::new(&path);

        assert_eq!(path, track.source.uri);

        println!("{:?}", track);
    }
}
