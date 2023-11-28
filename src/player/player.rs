use super::error::PlayerError;
use crate::player::SourceDecoder;
use crate::track::error::TrackError;
use crate::track::Track;
use anyhow::anyhow;
use rand::Rng;
use rodio::{Sink, Source};
use std::collections::VecDeque;

type AnyResult<T = ()> = anyhow::Result<T>;

pub struct Player {
    playlist: VecDeque<Track>,
    current_track: Option<Track>,
    flag: Flag,
    sink: Sink,
}

struct Flag {
    exit: bool,
    repeat: bool,
    loop_: bool,
    random: bool,
}

fn new_sink() -> AnyResult<Sink> {
    let (_stream, handle) = rodio::OutputStream::try_default()?;
    let sink = rodio::Sink::try_new(&handle)?;

    Ok(sink)
}

impl Player {
    pub fn new() -> AnyResult<Player> {
        Ok(Player {
            playlist: VecDeque::new(),
            current_track: None,
            sink: new_sink()?,
            flag: Flag {
                exit: false,
                repeat: false,
                loop_: false,
                random: false,
            },
        })
    }

    fn update_current_track(&mut self) -> AnyResult {
        let prelaod = loop {
            if self.playlist.is_empty() {
                break None;
            }

            let t = {
                if self.flag.repeat {
                    self.current_track.take()
                } else if self.flag.random {
                    self.playlist
                        .remove(rand::thread_rng().gen_range(0..self.playlist.len()))
                } else {
                    self.playlist.pop_front()
                }
            };

            if t.is_some() {
                break t;
            }
        };

        if self.flag.loop_ {
            if let Some(v) = self.current_track.take() {
                self.playlist.push_back(v)
            }
        }

        self.current_track = prelaod;

        Ok(())
    }

    async fn play_track(&mut self) -> AnyResult {
        if self.flag.exit {
            return Err(anyhow!(PlayerError::PlayerHasExited));
        };

        if self.playlist.is_empty() {
            return Err(anyhow!(PlayerError::PlaylistIsEmpty));
        }

        self.update_current_track()?;

        if self.current_track.is_none() {
            return Err(anyhow!(TrackError::SourceIsMissing));
        }

        let track = self.current_track.as_mut().unwrap();

        match track.check_available() {
            Ok(_) => {}
            Err(_) => track.refresh()?,
        };

        let source = track.get_source();

        let decoder = SourceDecoder::new(source).await?;

        // let duration = Source::total_duration(&decoder);

        self.sink.append(decoder);

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
