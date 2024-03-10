mod local;
mod remote;
mod youtube;

use async_trait::async_trait;
use std::{
    collections::HashMap,
    io::{Read, Seek},
};

use rodio::Decoder;

pub(crate) use local::LocalTrack;

type AnyResult<T = ()> = anyhow::Result<T>;

#[async_trait]
pub(crate) trait Track {
    type Source: Read + Seek + Sync + Send + 'static;

    async fn get_decoded_source(&self) -> AnyResult<Decoder<Self::Source>>;
}

pub trait Metadata {
    fn metadata(&self) -> AnyResult<&HashMap<String, String>>;
}
