use crate::track::{local, playlist, youtube};

mod test;
mod track;
mod util;

fn main() {
    println!("Welcome to use rust-player!");
    let track = local::track("music/download/save.m4a".to_string());
    let mut pl = playlist();

    pl.append(track);

    pl.play(|| {});
}
