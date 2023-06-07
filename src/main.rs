mod track;

use std::collections::VecDeque;

use track::local;
use track::playlist;

fn main() {
    println!("Welcome to use rust-player!");

    let lotrack = local::track("music/local/sleep.m4a".to_string());

    let mut pl = playlist();

    let mut new_track: VecDeque<_> = [lotrack].into();

    pl.tracks.append(&mut new_track);
    pl.toggle_loop();
    pl.set_volume(0.6);
    pl.play();
}
