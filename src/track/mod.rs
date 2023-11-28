pub mod error;
mod local;
mod youtube;
type AnyResult<T = ()> = anyhow::Result<T>;
pub type Track = Box<dyn Playable>;

/////////////////////////////////////////
pub use youtube::YoutubeTrack;
pub use local::LocalTrack;

/////////////////////////////////////////

pub trait Playable {
    // Player will get the uri and play it
    fn get_source(&self) -> &Source;
    // Player will run it when `is_available` is false
    fn refresh(&mut self) -> AnyResult {
        Ok(())
    }
    // This method will be called to check the playable source is available
    fn check_available(&self) -> AnyResult {
        Ok(())
    }
}

#[derive(Debug)]
pub enum SourceType {
    LocalFile,
    RemoteFile,
    Streamlink,
    OtherStream,
    Empty,
}

#[derive(Debug)]
pub struct Source {
    pub(crate) uri: String,
    pub(crate) source_type: SourceType,
}
