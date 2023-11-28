use thiserror::Error;


#[derive(Error, Debug)]
pub enum TrackError {
    #[error("Given source path ({0}) is not a file.")]
    SourceIsNotAFile(String),
    #[error("Given source is missing")]
    SourceIsMissing,
    #[error("This is a empty source")]
    SourceIsEmpty,
}


