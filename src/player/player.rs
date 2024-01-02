use super::{error::PlayerError, source_decoder::ReaderType};
use crate::player::SourceDecoder;
use crate::track::error::TrackError;
use crate::track::Track;
use anyhow::anyhow;
use rand::Rng;
use rodio::{Decoder, Sink};
use std::collections::VecDeque;
use tracing::warn;

type AnyResult<T = ()> = anyhow::Result<T>;

pub struct Player {
    pub playlist: VecDeque<Track>,
    pub current_track: Option<Track>,
    flag: Flag,
    sink: Sink,
}

struct Flag {
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
            flag: Flag {
                repeat: false,
                loop_: false,
                random: false,
            },

            sink: new_sink()?,
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

    pub async fn gen_next_source(&mut self) -> AnyResult<Decoder<ReaderType>> {
        if self.playlist.is_empty() {
            return Err(anyhow!(PlayerError::PlaylistIsEmpty));
        }

        if let Err(v) = self.update_current_track() {
            warn!("{}", &v);
        }

        if self.current_track.is_none() {
            return Err(anyhow!(TrackError::SourceIsMissing));
        }

        let track = self.current_track.as_mut().unwrap();

        if let Err(_) = track.check_available() {
            track.refresh()?
        };

        let source = track.get_source();

        let decoder = SourceDecoder::new(source).await?;

        Ok(decoder)
    }

    /// This is an async function.
    ///
    /// If current sink is paused, resume it.
    /// Otherwise, play next track.
    #[inline]
    pub async fn play(&mut self) -> AnyResult {
        if self.sink.is_paused() {
            self.sink.play();
        } else {
            let source = self.gen_next_source().await?;
            self.sink.append(source);
        }
        Ok(())
    }

    /// Pause current sink
    #[inline]
    pub fn pause(&self) {
        self.sink.pause();
    }

    /// This is an async function.
    ///
    /// Stop current sink, and play next track.
    #[inline]
    pub async fn skip(&mut self) -> AnyResult {
        self.stop();
        self.play().await?;
        Ok(())
    }

    /// Stop current sink
    #[inline]
    pub fn stop(&self) {
        self.sink.stop();
    }

    /// If given speed is None, it return current speed.
    /// If given speed is Some, it will set speed and return None.
    #[inline]
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
    #[inline]
    pub fn volume(&self, val: Option<f32>) -> Option<f32> {
        match val {
            Some(v) => {
                self.sink.set_volume(v);
                None
            }
            None => Some(self.sink.volume()),
        }
    }

    /// Drop self
    #[inline]
    pub fn exit(self) {}
}
