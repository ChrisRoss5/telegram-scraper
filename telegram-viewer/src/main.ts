import { createApp } from "vue";
import App from "./App.vue";
import "./style.css";

const app = createApp(App);

const vViewportLoad = {
  mounted: (el: HTMLImageElement | HTMLVideoElement | HTMLAudioElement) => {
    const observer = new IntersectionObserver(
      (entries) => {
        const entry = entries[0];
        const mediaElement = entry.target as HTMLMediaElement; // Type assertion

        if (entry.isIntersecting) {
          // Element is in viewport: load the media if it's not already loaded.
          // This check prevents re-loading if the element briefly goes out and back in.
          if (
            mediaElement.dataset.src &&
            mediaElement.src !== mediaElement.dataset.src
          ) {
            mediaElement.src = mediaElement.dataset.src;
          }
        } else {
          // Element is out of viewport: unload the media.
          // Pausing is important for video/audio to stop sound.
          if (
            mediaElement.tagName === "VIDEO" ||
            mediaElement.tagName === "AUDIO"
          ) {
            mediaElement.pause();
          }
          // Clear the src to stop buffering and free up memory.
          mediaElement.src = "";
        }
      },
      {
        // Optional: Adjust the margin to load/unload sooner or later.
        rootMargin: "2000px",
      }
    );

    // Store the observer on the element to access it in the unmounted hook.
    (el as any)._viewportObserver = observer;
    observer.observe(el);
  },
  unmounted: (el: HTMLElement) => {
    // Clean up the observer when the component is destroyed.
    const observer = (el as any)._viewportObserver;
    if (observer) {
      observer.disconnect();
      delete (el as any)._viewportObserver;
    }
  },
};

app.directive("viewport-load", vViewportLoad);

app.mount("#app");
