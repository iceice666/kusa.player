mod local;

use std::{
    collections::HashMap,
    io::{Read, Seek},
};

use rodio::Decoder;

type AnyResult<T = ()> = anyhow::Result<T>;

pub(crate) trait Track {
    type Source: Read + Seek + Sync + Send + 'static;

    fn refresh(&self) -> AnyResult;

    fn get_decoded_source(&self) -> AnyResult<Decoder<Self::Source>>;

    fn get_metadata(&self) -> AnyResult<HashMap<String, String>>;
}
