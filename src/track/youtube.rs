use super::Playable;



pub struct YoutubeTrack{}


impl Playable for YoutubeTrack{
    fn get_source(&self) -> &super::Source {
        todo!()
    }

    fn refresh(&mut self) -> super::AnyResult {
        Ok(())
    }

    fn check_available(&self) -> super::AnyResult {
        Ok(())
    }
}
