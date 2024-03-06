mod local;
mod simple_player;

use std::{
    collections::{HashMap, VecDeque},
    io::{Read, Seek},
};

type AnyResult<T = ()> = anyhow::Result<T>;

trait Track {
    type Source: Seek + Read + Sync + Send;

    fn refresh(&self) -> AnyResult;

    fn get_source(&self) -> AnyResult<Self::Source>;

    fn get_metadata(&self) -> AnyResult<HashMap<String, String>>;
}

struct TrackList<T>(VecDeque<T>)
where
    T: Track,
    T::Source: Seek + Read + Sync + Send;

impl<T: Track> IntoIterator for TrackList<T> {
    type Item = T;
    type IntoIter = std::collections::vec_deque::IntoIter<T>;

    fn into_iter(self) -> Self::IntoIter {
        self.0.into_iter()
    }
}
