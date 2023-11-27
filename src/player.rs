use crate::source_decoder::SourceDecoder;
use crate::track::Track;
use rodio::Sink;
use std::collections::VecDeque;
type AnyResult<T = ()> = anyhow::Result<T>;

struct Player {
    playlist: VecDeque<Track>,
    current_track: Option<Track>,
    flag_exit: bool,
    flag_repeat: bool,
    flag_loop: bool,
    sink: Sink,
}

fn new_sink() -> AnyResult<Sink> {
    let (_stream, handle) = rodio::OutputStream::try_default()?;
    let sink = rodio::Sink::try_new(&handle)?;

    Ok(sink)
}

impl Player {
    fn new() -> AnyResult<Player> {
        Ok(Player {
            playlist: VecDeque::new(),
            current_track: None,
            flag_exit: false,
            flag_loop: false,
            flag_repeat: false,
            sink: new_sink()?,
        })
    }

    fn update_current_track(&mut self) {
        let prelaod = loop {
            if self.playlist.is_empty() {
                break None;
            }

            let t = {
                if self.flag_loop {
                    self.playlist.pop_front()
                } else if self.flag_repeat {
                    self.current_track.take()
                } else {
                    self.playlist.pop_front()
                }
            };

            if t.is_some() {
                break t;
            }
        };

        self.current_track = prelaod;
    }

    pub async fn mainloop(mut self) -> AnyResult {
        while !self.flag_exit {
            if self.playlist.is_empty() {
                continue;
            }

            self.update_current_track();

            if self.current_track.is_none() {
                continue;
            }

            let track = self.current_track.as_ref().unwrap();

            let source = track.get_source();

            let decoder = SourceDecoder::new(source).await?;

            // let duration = decoder.total_duration();

            self.sink.append(decoder);
        }

        Ok(())
    }

    pub fn play(&self) {
        self.sink.play();
    }

    pub fn pause(&self) {
        self.sink.pause();
    }

    /// If given speed is None, it return current speed.
    /// If given speed is Some, it will set speed and return None.
    pub fn speed(&self, val: Option<f32>) -> Option<f32> {
        match val {
            Some(v) => {
                self.sink.set_speed(v);
                None
            }
            None => Some(self.sink.speed()),
        }
    }

    /// If given volume is None, it return current speed.
    /// If given volume is Some, it will set volume and return None.
    pub fn volume(&self, val: Option<f32>) -> Option<f32> {
        match val {
            Some(v) => {
                self.sink.set_volume(v);
                None
            }
            None => Some(self.sink.volume()),
        }
    }
}
