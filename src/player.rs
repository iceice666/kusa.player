use crate::track::{EmptyTrack, Playable, Source, SourceType, Track};
use anyhow::Result as anyResult;
use rodio::{Decoder, Sink};
use std::collections::LinkedList;
use std::fs::File;
use std::io::BufReader;
use stream_download::storage::temp::TempStorageProvider;
use stream_download::{Settings, StreamDownload};

struct Player {
    playlist: LinkedList<Track>,
    current_track: Track,
    flag_exit: bool,
    flag_repeat: bool,
    flag_loop: bool,
}

impl Player {
    fn new() -> Player {
        Player {
            playlist: LinkedList::new(),
            current_track: Box::new(EmptyTrack::new()),
            flag_exit: false,
            flag_loop: false,
            flag_repeat: false,
        }
    }

    async fn mainloop(mut self, mut sink: Sink) -> anyResult<()> {
        while !self.flag_exit {
            if self.playlist.len() <= 0 {
                continue;
            }
            {
                // Update current track
                if self.flag_loop {
                    self.playlist.push_back(self.current_track);
                    self.current_track = self.playlist.pop_front().unwrap();
                } else if self.flag_repeat {
                    // Do nothing
                } else {
                    self.current_track = self.playlist.pop_front().unwrap();
                }
            }

            let source = self.current_track.get_source();
            match source.source_type {
                SourceType::LocalFile => {
                    sink = Player::play_local(sink, source)?;
                }
                SourceType::RemoteFile => {
                    sink = Player::play_remote(sink, source).await?;
                }
                SourceType::Stream => {}
                SourceType::Empty => continue,
            }

            sink.sleep_until_end();
        }

        Ok(())
    }

    fn play_local(sink: Sink, source: &Source) -> anyResult<Sink> {
        let filepath = &source.uri;

        let file = File::open(filepath)?;
        let source = Decoder::new(BufReader::new(file))?;

        sink.append(source);

        Ok(sink)
    }

    async fn play_remote(sink: Sink, source: &Source) -> anyResult<Sink> {
        let url = &source.uri;

        let reader = StreamDownload::new_http(
            url.parse()?,
            TempStorageProvider::new(),
            Settings::default(),
        )
        .await?;

        let decoder = Decoder::new(reader)?;

        sink.append(decoder);

        Ok(sink)
    }
}
