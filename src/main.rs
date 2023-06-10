mod track;

use std::collections::VecDeque;

use track::local;
use track::playlist;

use crate::track::youtube;

fn main() {
    println!("Welcome to use rust-player!");

    let lotrack = local::track("music/local/sleep.m4a".to_string());
    let yttrack = youtube::track("music/local/sleep.m4a".to_string());

    let mut pl = playlist();

    let mut new_track: VecDeque<_> = [lotrack, yttrack].into();


    pl.tracks.append(&mut [lotrack, yttrack].into());
    pl.toggle_loop();
    pl.set_volume(0.3);
    pl.play();
}