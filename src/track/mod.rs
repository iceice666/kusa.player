pub mod local;
// pub mod youtube;

pub trait Track {
    /// `is_expired` check is the uri expired
    /// `refresh` refresh uri
    /// `play` play music
    fn is_expired(&self) -> bool;
    fn refresh(&self) -> String;
    fn play(&self);
}

pub trait TrackInfo {}
