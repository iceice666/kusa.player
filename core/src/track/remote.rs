type AnyResult<T = ()> = anyhow::Result<T>;

use async_trait::async_trait;
use rodio::Decoder;
use stream_download::{storage::temp::TempStorageProvider, Settings, StreamDownload};
use tracing::instrument;

use crate::track::Track;

#[derive(Debug)]
struct RemoteTrack {
    url: String,
}

impl RemoteTrack {
    pub fn new(url: impl Into<String>) -> Self {
        Self { url: url.into() }
    }
}

#[async_trait]
impl Track for RemoteTrack {
    type Source = StreamDownload<TempStorageProvider>;

    #[instrument]
    async fn get_decoded_source(&self) -> AnyResult<Decoder<Self::Source>> {
        let reader = StreamDownload::new_http(
            self.url.parse()?,
            TempStorageProvider::new(),
            Settings::default(),
        )
        .await?;

        let dec = Decoder::new(reader)?;

        Ok(dec)
    }
}
