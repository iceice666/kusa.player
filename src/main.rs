
use tracing::metadata::LevelFilter;
use tracing_subscriber::EnvFilter;

type AnyResult<T = ()> = anyhow::Result<T>;

#[tokio::main]
async fn main() -> AnyResult {
    tracing_subscriber::fmt()
        .with_env_filter(EnvFilter::default().add_directive(LevelFilter::INFO.into()))
        .with_line_number(true)
        .with_file(true)
        .init();

    Ok(())
}
