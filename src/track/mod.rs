use std::collections::VecDeque;

use anyhow::Result;
use rodio::{OutputStream, Sink};
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

////////////////////////////////////////////////////////
pub trait PlayableTrack {
    /// `is_expired` check is the uri expired
    /// `refresh` refresh uri and playable track/uri
    fn is_expired(&self) -> bool;
    fn refresh(&mut self);
    fn play(&mut self, sink: Sink) -> Result<()>;
    fn info(&self) -> TrackInfo;
}

pub struct Playlist<T>
where
    T: PlayableTrack,
{
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
            // the first
            self.tracks.pop_front().unwrap()
        } else if index == self.tracks.len() {
            // the last
            self.tracks.pop_back().unwrap()
        } else {
            // split the track by index
            let mut temp_tracks = self.tracks.split_off(index);
            // the item we want will be the first of the second track
            let result = temp_tracks.pop_front().unwrap();
            // chain together
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

    pub fn play<F>(&mut self, callback: F)
    where
        F: Fn(),
    {
        let (_stream, stream_handle) = OutputStream::try_default().unwrap();

        while self.tracks.len() > 0 {
            // generate new sink to play
            let sink = Sink::try_new(&stream_handle).unwrap();
            // get the next track
            let mut next_track = self.tracks.pop_front().unwrap();
            // get track info
            self.track_info = next_track.info();
            // refresh source if need
            if next_track.is_expired() {
                next_track.refresh();
            }
            // get the source and apply
            if let Err(e) = next_track.play(sink) {
                println!(
                    "This track is broken and with error msg following:\n{:?}",
                    e
                );
                continue;
            }

            callback();

            if self.do_repeat {
                self.tracks.insert(0, next_track);
            } else if self.do_repeat {
                self.tracks.insert(self.tracks.len(), next_track);
            }
        }
    }
}

pub fn playlist<T>() -> Playlist<T>
where
    T: PlayableTrack,
{
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
