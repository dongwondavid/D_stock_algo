use std::sync::Once;

static INIT: Once = Once::new();

pub fn init_logger() {
    INIT.call_once(|| {
        env_logger::builder()
            .format_target(false)
            .format_timestamp_millis()
            .init();
    });
} 