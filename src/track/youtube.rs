use super::Track;

struct Youtube {
    source_uri: String,
}

impl Track for Youtube {
    fn refresh(&self) -> String {
        self.source_uri.clone()
    }
    fn is_expired(&self) -> bool {
        false
    }

    fn play(&self) {}
}
