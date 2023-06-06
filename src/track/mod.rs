use std::{collections::VecDeque, fs::File, io::BufReader};

use rodio::{Decoder, OutputStream, Sink};

pub mod local;
// pub mod youtube;

pub trait PlayableTrack {
    /// `is_expired` check is the uri expired
    /// `refresh` refresh uri and playable track/uri
    fn is_expired(&self) -> bool;
    fn refresh(&mut self);
    fn get_source(&mut self) -> Option<Decoder<BufReader<File>>>;
}

pub struct Playlist<T: PlayableTrack> {
    pub tracks: VecDeque<T>,
    sink: Sink,
}

impl<T> Playlist<T>
where
    T: PlayableTrack,
{
    // sink / player funcitons
    pub fn set_volume(&self, vol: f32) {
        self.sink.set_volume(vol);
    }

    pub fn get_volume(&self) -> f32 {
        self.sink.volume()
    }

    pub fn set_speed(&self, speed: f32) {
        self.sink.set_speed(speed);
    }

    pub fn get_speed(&self) -> f32 {
        self.sink.speed()
    }

    pub fn resume(&self) {
        self.sink.play();
    }

    pub fn pause(&self) {
        self.sink.pause();
    }

    pub fn is_paused(&self) -> bool {
        self.sink.is_paused()
    }

    pub fn stop(&self) {
        self.sink.stop();
    }

    pub fn clear(&self) {
        self.sink.clear();
    }

    pub fn skip(&self) {
        self.sink.skip_one();
    }

    // tracks control
    pub fn play(&mut self) -> Option<T> {
        if !self.tracks.is_empty() && self.sink.empty() {
            let mut first_track = self.tracks.pop_front().unwrap();
            let source = first_track.get_source().unwrap();
            self.sink.append(source);

            Some(first_track)
        } else {
            None
        }
    }
}

pub fn playlist<T: PlayableTrack>() -> Playlist<T> {
    // Get a output stream handle to the default physical sound device
    let (_stream, stream_handle) = OutputStream::try_default().unwrap();
    let sink = Sink::try_new(&stream_handle).unwrap();

    // Set default volume
    sink.set_volume(0.3);

    Playlist {
        tracks: VecDeque::new(),
        sink,
    }
}
