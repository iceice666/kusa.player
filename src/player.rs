use crate::track::Playable;
use std::collections::LinkedList;

struct Player {
    playlist: LinkedList<Box<dyn Playable>>,
}
