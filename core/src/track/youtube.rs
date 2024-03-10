use crate::track::LocalTrack;

#[derive(Debug)]
struct YoutubeTrack {
    url: String,
}

impl From<YoutubeTrack> for LocalTrack {
    fn from(value: YoutubeTrack) -> Self {
        unimplemented!()
    }
}
