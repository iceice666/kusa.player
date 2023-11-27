use crate::error::TrackError;
use crate::track::{Source, SourceType};
use anyhow::anyhow;
use rodio::Decoder;
use std::fs::File;
use std::io::BufReader;
use std::io::{Read, Seek};
use std::num::NonZeroUsize;
use stream_download::http::reqwest::Client;
use stream_download::http::HttpStream;
use stream_download::source::SourceStream;
use stream_download::storage::bounded::BoundedStorageProvider;
use stream_download::storage::memory::MemoryStorageProvider;
use stream_download::storage::temp::TempStorageProvider;
use stream_download::{Settings, StreamDownload};

type AnyResult<T = ()> = anyhow::Result<T>;

pub struct SourceDecoder {}

const STREAMLINK_SUPPORTED_URLS: [&'static str; 1] = [""];

pub enum ReaderType {
    Local(BufReader<File>),
    Remote(StreamDownload<TempStorageProvider>),
    OtherStream(StreamDownload<BoundedStorageProvider<MemoryStorageProvider>>),
}

impl Seek for ReaderType {
    fn seek(&mut self, pos: std::io::SeekFrom) -> std::io::Result<u64> {
        match self {
            ReaderType::Local(reader) => reader.seek(pos),
            ReaderType::Remote(reader) => reader.seek(pos),
            ReaderType::OtherStream(reader) => reader.seek(pos),
        }
    }
}

impl Read for ReaderType {
    fn read(&mut self, buf: &mut [u8]) -> std::io::Result<usize> {
        match self {
            ReaderType::Local(reader) => reader.read(buf),
            ReaderType::Remote(reader) => reader.read(buf),
            ReaderType::OtherStream(reader) => reader.read(buf),
        }
    }
}

impl SourceDecoder {
    pub async fn new(source: &Source) -> AnyResult<Decoder<ReaderType>> {
        let uri = source.uri.as_str();
        let reader = match &source.source_type {
            SourceType::LocalFile => SourceDecoder::local(uri).await,
            SourceType::RemoteFile => SourceDecoder::remote(uri).await,
            SourceType::Streamlink => SourceDecoder::streamlink(uri).await,
            SourceType::OtherStream => SourceDecoder::otherstream(uri).await,
            SourceType::Empty => Err(anyhow!(TrackError::SourceIsEmpty))?,
        }?;

        let decoder = Decoder::new(reader)?;

        Ok(decoder)
    }

    pub async fn local(filepath: &str) -> AnyResult<ReaderType> {
        let file = File::open(filepath)?;

        Ok(ReaderType::Local(BufReader::new(file)))
    }

    pub async fn remote(url: &str) -> AnyResult<ReaderType> {
        let reader = StreamDownload::new_http(
            url.parse()?,
            TempStorageProvider::new(),
            Settings::default(),
        )
        .await?;

        Ok(ReaderType::Remote(reader))
    }

    pub async fn otherstream(url: &str) -> AnyResult<ReaderType> {
        let stream = HttpStream::<Client>::create(url.parse()?).await?;
        let bitrate: u64 = stream.header("Icy-Br").unwrap().parse()?;
        // buffer 5 seconds of audio
        // bitrate (in kilobits) / bits per byte * bytes per kilobyte * 5 seconds
        let prefetch_bytes = bitrate / 8 * 1024 * 5;

        let reader = StreamDownload::from_stream(
            stream,
            // use bounded storage to keep the underlying size from growing indefinitely
            BoundedStorageProvider::new(
                MemoryStorageProvider {},
                // be liberal with the buffer size, you need to make sure it holds enough space to
                // prevent any out-of-bounds reads
                NonZeroUsize::new(512 * 1024).unwrap(),
            ),
            Settings::default().prefetch_bytes(prefetch_bytes),
        )
        .await?;

        Ok(ReaderType::OtherStream(reader))
    }

    pub async fn streamlink(url: &str) -> AnyResult<ReaderType> {
        todo!();
    }
}
