/*
 * Raspberry Pi C Client for Rescue Vision
 * 
 * This client captures frames from a camera and sends them to the Django backend.
 * 
 * Compilation:
 *   gcc -o raspberry_pi_client raspberry_pi_client.c -lcurl -lpthread
 * 
 * Dependencies:
 *   - libcurl-dev
 *   - Camera library (e.g., raspicam, V4L2)
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <curl/curl.h>
#include <time.h>

#define BACKEND_URL "http://localhost:8000"
#define READY_ENDPOINT "/api/frames/ready/"
#define INGEST_ENDPOINT "/api/frames/ingest/"
#define POLL_INTERVAL 5  // seconds
#define MAX_RETRIES 3

// Structure to hold HTTP response
struct ResponseData {
    char *data;
    size_t size;
};

// Callback function for curl
size_t WriteCallback(void *contents, size_t size, size_t nmemb, struct ResponseData *data) {
    size_t realsize = size * nmemb;
    data->data = realloc(data->data, data->size + realsize + 1);
    if (data->data) {
        memcpy(&(data->data[data->size]), contents, realsize);
        data->size += realsize;
        data->data[data->size] = 0;
    }
    return realsize;
}

// Check if backend is ready to receive frames
int check_backend_ready(CURL *curl) {
    char url[256];
    snprintf(url, sizeof(url), "%s%s", BACKEND_URL, READY_ENDPOINT);
    
    struct ResponseData response;
    response.data = malloc(1);
    response.size = 0;
    
    curl_easy_setopt(curl, CURLOPT_URL, url);
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);
    
    CURLcode res = curl_easy_perform(curl);
    
    int ready = 0;
    if (res == CURLE_OK) {
        // Simple JSON parsing - check for "ready":true
        if (strstr(response.data, "\"ready\":true") != NULL) {
            ready = 1;
        }
    }
    
    free(response.data);
    return ready;
}

// Capture frame from camera (placeholder - implement with actual camera library)
int capture_frame(const char *filename) {
    // TODO: Implement actual camera capture
    // Example with raspicam:
    //   system("raspistill -o frame.jpg -w 640 -h 480 -t 100");
    
    // For testing, create a dummy file
    FILE *fp = fopen(filename, "w");
    if (fp) {
        fprintf(fp, "dummy frame data");
        fclose(fp);
        return 1;
    }
    return 0;
}

// Send frame to backend
int send_frame(CURL *curl, const char *image_path) {
    char url[256];
    snprintf(url, sizeof(url), "%s%s", BACKEND_URL, INGEST_ENDPOINT);
    
    curl_httppost *formpost = NULL;
    curl_httppost *lastptr = NULL;
    
    // Add image file to form
    curl_formadd(&formpost, &lastptr,
                 CURLFORM_COPYNAME, "image",
                 CURLFORM_FILE, image_path,
                 CURLFORM_CONTENTTYPE, "image/jpeg",
                 CURLFORM_END);
    
    struct ResponseData response;
    response.data = malloc(1);
    response.size = 0;
    
    curl_easy_setopt(curl, CURLOPT_URL, url);
    curl_easy_setopt(curl, CURLOPT_HTTPPOST, formpost);
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);
    
    CURLcode res = curl_easy_perform(curl);
    
    curl_formfree(formpost);
    free(response.data);
    
    return (res == CURLE_OK);
}

int main(int argc, char *argv[]) {
    CURL *curl;
    curl = curl_easy_init();
    
    if (!curl) {
        fprintf(stderr, "Failed to initialize curl\n");
        return 1;
    }
    
    printf("Rescue Vision Raspberry Pi Client\n");
    printf("Connecting to backend: %s\n", BACKEND_URL);
    
    const char *frame_file = "/tmp/frame.jpg";
    int retry_count = 0;
    
    while (1) {
        // Check if backend is ready
        if (check_backend_ready(curl)) {
            printf("[%ld] Backend is ready, capturing frame...\n", time(NULL));
            
            // Capture frame from camera
            if (capture_frame(frame_file)) {
                printf("[%ld] Frame captured, sending to backend...\n", time(NULL));
                
                // Send frame to backend
                if (send_frame(curl, frame_file)) {
                    printf("[%ld] Frame sent successfully\n", time(NULL));
                    retry_count = 0;
                } else {
                    fprintf(stderr, "[%ld] Failed to send frame\n", time(NULL));
                    retry_count++;
                }
                
                // Clean up frame file
                unlink(frame_file);
            } else {
                fprintf(stderr, "[%ld] Failed to capture frame\n", time(NULL));
            }
        } else {
            printf("[%ld] Backend not ready, waiting...\n", time(NULL));
        }
        
        // Check retry limit
        if (retry_count >= MAX_RETRIES) {
            fprintf(stderr, "Max retries reached, exiting\n");
            break;
        }
        
        // Wait before next iteration
        sleep(POLL_INTERVAL);
    }
    
    curl_easy_cleanup(curl);
    return 0;
}
