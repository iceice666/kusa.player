use crate::track::Track;
use async_trait::async_trait;
use rodio::Decoder;
use stream_download::{storage::temp::TempStorageProvider, Settings, StreamDownload};

type AnyResult<T = ()> = anyhow::Result<T>;

#[derive(Debug)]
struct RemoteTrack {
    url: String,
}

#[async_trait]
impl Track for RemoteTrack {
    type Source = StreamDownload<TempStorageProvider>;

    async fn get_decoded_source(&self) -> AnyResult<Decoder<Self::Source>> {
        let source = StreamDownload::new_http(
            self.url.parse()?,
            TempStorageProvider::default(),
            Settings::default(),
        )
        .await?;

        let dec = Decoder::new(source)?;

        Ok(dec)
    }
}
