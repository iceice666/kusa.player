use std::{collections::VecDeque, fs::File, io::BufReader};

use rodio::{Decoder, OutputStream, Sink};

pub mod local;
pub mod youtube;

#[derive(Clone)]
pub struct TrackInfo {
    title: String,
    author: String,
}

pub fn empty_trackinfo() -> TrackInfo {
    TrackInfo {
        title: "<Untitled>".to_string(),
        author: "<someone>".to_string(),
    }
}

pub trait PlayableTrack {
    /// `is_expired` check is the uri expired
    /// `refresh` refresh uri and playable track/uri
    fn is_expired(&self) -> bool;
    fn refresh(&self);
    fn get_source(&mut self) -> Decoder<BufReader<File>>;
    fn info(&self) -> TrackInfo;
}

pub struct Playlist<T: PlayableTrack> {
    pub tracks: VecDeque<T>,
    sink: Sink,
    pub do_repeat: bool,
    pub do_loop: bool,
    pub track_info: TrackInfo,
}

impl<T> Playlist<T>
    where
        T: PlayableTrack,
{
    // track
    pub fn append(&mut self, track: T) {
        self.tracks.push_back(track);
    }
    pub fn insert(&mut self, index: usize, track: T) {
        self.tracks.insert(index, track)
    }

    pub fn pop(&mut self, index: usize) -> T {
        if index == 0 {
            self.tracks.pop_front()
        } else if index == self.tracks.len() {
            self.tracks.pop_back()
        } else {
            let mut temp_tracks = self.tracks.split_off(index);
            let result = temp_tracks.pop_front().unwrap();
            self.tracks.append(&mut temp_tracks);
            result
        }
    }

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

    pub fn toggle_repeat(&mut self) {
        self.do_repeat = !self.do_repeat;
    }

    pub fn toggle_loop(&mut self) {
        self.do_loop = !self.do_loop;
    }

    pub fn play(&mut self) {
        let (_stream, stream_handle) = OutputStream::try_default().unwrap();
        self.sink = Sink::try_new(&stream_handle).unwrap();

        while self.tracks.len() > 0 {
            let mut next_track = self.tracks.pop_front().unwrap();
            let source = next_track.get_source();
            self.track_info = next_track.info();

            self.sink.append(source);
            self.sink.sleep_until_end();

            if self.do_repeat {
                self.tracks.insert(0, next_track);
            } else if self.do_repeat {
                self.tracks.insert(self.tracks.len(), next_track);
            }
        }
    }
}

pub fn playlist<T: PlayableTrack>() -> Playlist<T> {
    // Get a output stream handle to the default physical sound device
    let (_stream, stream_handle) = OutputStream::try_default().unwrap();
    let sink = Sink::try_new(&stream_handle).unwrap();

    sink.set_volume(0.3);

    Playlist {
        tracks: VecDeque::new(),
        sink,
        do_repeat: false,
        do_loop: false,
        track_info: empty_trackinfo(),
    }
}
