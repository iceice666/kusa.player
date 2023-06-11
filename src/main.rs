use crate::track::{playlist, youtube};

mod test;
mod track;
mod util;

fn main() {
    println!("Welcome to use rust-player!");
    let track = youtube::track("https://www.youtube.com/watch?v=AFBLtSZMNGc".to_string());
    let mut pl = playlist();

    pl.append(track);
    pl.play(|| {});
}
