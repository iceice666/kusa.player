#[cfg(test)]
mod test {
    use crate::track::playlist;
    use crate::track::{local, youtube};

    fn take_input() -> String {
        let mut input = String::new();

        match std::io::stdin().read_line(&mut input) {
            Ok(_) => input.trim().to_string().to_lowercase(),
            Err(e) => {
                panic!("{}", e)
            }
        }
    }

    #[test]
    fn test_play_youtube() {
        let track = youtube::track("https://www.youtube.com/watch?v=AFBLtSZMNGc".to_string());
        let mut pl = playlist();

        pl.append(track);
        pl.play(|| {
            println!("Do you hear the 'hifumi, daisuki?' music?: (y/n) ");

            assert_eq!(take_input(), "y");
        });
    }

    #[test]
    fn test_play_local() {
        let track = local::track("music/test/bruh.mp3".to_string());
        let mut pl = playlist();

        pl.append(track);

        pl.play(|| {
            println!("Do you hear a 'bruh' sound?: (y/n) ");

            assert_eq!(take_input(), "y");
        });
    }

    #[test]
    fn test_repeat() {
        let track = local::track("music/test/bruh.mp3".to_string());
        let mut pl = playlist();

        pl.append(track);
    }
}
