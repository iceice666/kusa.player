use crate::track::{EmptyTrack, Playable, Track};
use std::collections::LinkedList;

struct Player {
    playlist: LinkedList<Track>,
    current_track: Track,
}

impl Player {
    fn new() -> Player {
        Player {
            playlist: LinkedList::new(),
            current_track: Box::new(EmptyTrack::new()),
        }
    }

    async fn play(&mut self){

        while self.playlist.len() > 0 {
            
        }

    }
}
