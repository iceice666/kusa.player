use std::collections::VecDeque;

use crate::track::Track as TrackTrait;

pub struct Player<S: TrackTrait> {
    pub(crate) playlist: VecDeque<S>,
}
