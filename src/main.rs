mod track;

use track::local::Local;

use crate::track::Track;

fn main() {
    println!("Welcome to use rust-player!");

    let lotrack = Local {
        source_uri: "music/local/music.ogg".to_string(),
    };

    loop {
        lotrack.play();
    }
}
