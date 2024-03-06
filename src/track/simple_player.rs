use rodio::{OutputStream, Sink};

type AnyResult<T = ()> = anyhow::Result<T>;

pub fn new_player() -> AnyResult<Sink> {
    let (_stream, stream_handle) = OutputStream::try_default()?;
    let sink = Sink::try_new(&stream_handle)?;

    Ok(sink)
}

#[cfg(test)]
mod test {
    use rodio::{source::Source, Decoder, OutputStream, Sink};
    use std::fs::File;
    use std::io::BufReader;

    #[test]
    fn player() {
        let path = File::open("assets/ViRTUS.m4a").unwrap();
        let buf = BufReader::new(path);
        let dec = Decoder::new(buf).unwrap();

        let (_stream, stream_handle) = OutputStream::try_default().unwrap();
        let sink = Sink::try_new(&stream_handle).unwrap();

        sink.append(dec);

        sink.sleep_until_end();
    }
}
