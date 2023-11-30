use thiserror::Error;

#[derive(Error, Debug)]
pub enum TrackError {
    #[error("Given source is not point to a file.")]
    SourceIsNotAFile,
    #[error("Given source is missing")]
    SourceIsMissing,
    #[error("This is a empty source")]
    SourceIsEmpty,
}

#[derive(Debug, Error)]
pub enum YoutubeTrackError {
    #[error("Yt-dlp exited with a non-zero value")]
    YtdlpExitedUnexpectedly(String),

    #[error("The given seems not a valid youtube video url.")]
    InvalidUrl(String),
}
