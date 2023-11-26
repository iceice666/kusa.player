mod error;
mod player;
mod test;
mod track;
mod util;
use std::error::Error;
use std::time::Duration;

use stream_download::http::reqwest::Client;
use stream_download::http::HttpStream;
use stream_download::source::SourceStream;
use stream_download::storage::temp::TempStorageProvider;
use stream_download::{Settings, StreamDownload};
use tracing::info;
use tracing::metadata::LevelFilter;
use tracing_subscriber::EnvFilter;

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    tracing_subscriber::fmt()
        .with_env_filter(EnvFilter::default().add_directive(LevelFilter::INFO.into()))
        .with_line_number(true)
        .with_file(true)
        .init();

    let playlist = vec!["https://rr3---sn-ipoxu-3iik.googlevideo.com/videoplayback?expire=1701023203&ei=gzljZcqANLGCvcAPo-eygAk&ip=2001%3Ab011%3Ac000%3A3d9d%3A15dd%3A5fa9%3A7858%3Aba11&id=o-AMkONuVS8Qk8TKvgqHDFc3ujQxPY40MHUqeBbrT5zLiN&itag=140&source=youtube&requiressl=yes&mh=1x&mm=31%2C29&mn=sn-ipoxu-3iik%2Csn-un57enez&ms=au%2Crdu&mv=m&mvi=3&pcm2cms=yes&pl=57&initcwndbps=995000&vprv=1&svpuc=1&mime=audio%2Fmp4&gir=yes&clen=3575646&dur=220.891&lmt=1671359878700905&mt=1701001019&fvip=1&keepalive=yes&fexp=24007246&c=IOS&txp=5318224&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cvprv%2Csvpuc%2Cmime%2Cgir%2Cclen%2Cdur%2Clmt&sig=ANLwegAwRQIgWVGdc_mKRLafcLLb1EWu3Aj3TlB76Io3imq5vgZ5zgsCIQD57gQ3Ls_mXiO1kOAMfPaRkD5ak-d6DsQQeU1PI-JP1Q%3D%3D&lsparams=mh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpcm2cms%2Cpl%2Cinitcwndbps&lsig=AM8Gb2swRQIgESz9fiUlk-L640-utaqnqa9L23fsDpto0RnFf-z687ECIQCBgmoWcJwdU6o29b-VE4DIOwsM3MN-9_mlYKQXp25lew%3D%3D","http://www.hyperion-records.co.uk/audiotest/14 Clementi Piano Sonata in D major, Op 25 No 6 - Movement 2 Un poco andante.MP3"];

    let (_stream, handle) = rodio::OutputStream::try_default()?;
    let sink = rodio::Sink::try_new(&handle)?;

    let iter = playlist.into_iter();

    for item in iter {
        let stream = HttpStream::new(new_client()?, item.parse()?).await?;

        let reader =
            StreamDownload::from_stream(stream, TempStorageProvider::new(), Settings::default())
                .await?;
        sink.append(rodio::Decoder::new(reader)?);

        tokio::task::spawn_blocking(|| loop {}).await?;

        sink.set_volume(sink.volume() / 2.0);
    }
    Ok(())
}

fn new_client() -> Result<Client, reqwest::Error> {
    Client::builder()
        .connect_timeout(Duration::from_secs(30))
        .build()
}
