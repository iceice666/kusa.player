
use thiserror::Error;


#[derive(Error, Debug)]
pub enum PlayerError {
    #[error("The playlist is empty!")]
    PlaylistIsEmpty,
    #[error("The player has exited!")]
    PlayerHasExited,
}


