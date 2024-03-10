use ytdlp_binding::Ytdlp;

type AnyResult<T = ()> = anyhow::Result<T>;
fn main() -> AnyResult {
    tracing_subscriber::fmt::init();

    let client = Ytdlp::new("/usr/bin/yt-dlp");
    let res = client.get_info("https://www.youtube.com/watch?v=dQw4w9WgXcQ")?;
    println!("{:#?}", res);

    Ok(())
}
