use crate::track::Track;
use async_trait::async_trait;
use rodio::Decoder;
use stream_download::{storage::temp::TempStorageProvider, StreamDownload};

type AnyResult<T = ()> = anyhow::Result<T>;

#[derive(Debug)]
struct RemoteTrack {
    url: String,
}

#[async_trait]
impl Track for RemoteTrack {
    type Source = StreamDownload<TempStorageProvider>;

    async fn get_decoded_source(&self) -> AnyResult<Decoder<Self::Source>> {
        unimplemented!()
    }
}
