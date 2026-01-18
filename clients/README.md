# Raspberry Pi C Client

This directory contains the C client for Raspberry Pi integration with Rescue Vision.

## Building

```bash
gcc -o raspberry_pi_client raspberry_pi_client.c -lcurl -lpthread
```

## Dependencies

- `libcurl-dev` - HTTP client library
- Camera library (e.g., raspicam, V4L2)

Install on Raspberry Pi:
```bash
sudo apt-get update
sudo apt-get install libcurl4-openssl-dev
```

## Usage

```bash
./raspberry_pi_client
```

## Configuration

Edit the constants in `raspberry_pi_client.c`:
- `BACKEND_URL`: Django backend URL
- `POLL_INTERVAL`: Seconds between frame captures
- `MAX_RETRIES`: Maximum retry attempts

## Implementation Notes

The client:
1. Polls `/api/frames/ready/` to check backend readiness
2. Captures frames from camera when ready
3. Sends frames to `/api/frames/ingest/` via HTTP POST
4. Implements backpressure handling

## Camera Integration

The `capture_frame()` function is a placeholder. Implement actual camera capture using:
- **raspicam**: `raspistill` command-line tool
- **V4L2**: Video4Linux2 API
- **OpenCV**: C++/C API

Example with raspicam:
```c
int capture_frame(const char *filename) {
    char command[256];
    snprintf(command, sizeof(command), "raspistill -o %s -w 640 -h 480 -t 100", filename);
    return system(command) == 0;
}
```
