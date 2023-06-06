mod track;

use std::collections::VecDeque;

use track::local;
use track::playlist;

fn main() {
    println!("Welcome to use rust-player!");

    let lotrack = local::track("music/local/music.ogg".to_string());

    let mut pl = playlist();

    let mut new_track: VecDeque<_> = [lotrack].into();

    pl.tracks.append(&mut new_track);
    pl.play();

    loop {}
}
