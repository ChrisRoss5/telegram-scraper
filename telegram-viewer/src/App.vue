<script setup lang="ts">
import rawMessages from "@root/messages";

const server = "http://127.0.0.1:5500/";
const messages: TelegramMessage[] = rawMessages.slice(-10).reverse();
console.log(messages);

const isAnonymous = (msg: TelegramMessage) => {
  return !msg.username && !msg.first_name && !msg.last_name;
};

const getMediaUrl = (mediaPath: string) => {
  return server + mediaPath.replace(/\\/g, "/");
};

const getMediaType = (media: MediaItem) => {
  const type = media.media_type.toLowerCase();
  const path = media.media_path.toLowerCase();

  if (type.includes("photo") || path.match(/\.(jpg|jpeg|png|gif|webp)$/))
    return "image";
  if (type.includes("video") || path.match(/\.(mp4|webm|mov|avi|mkv)$/))
    return "video";
  if (type.includes("audio") || path.match(/\.(mp3|wav|ogg|m4a|flac)$/))
    return "audio";
  return "file";
};

const formatFileSize = (path: string) => {
  // Extract filename from path
  return path.split(/[/\\]/).pop() || path;
};
</script>

<template>
  <div class="container">
    <header class="header">
      <h1>Telegram Messages</h1>
      <p class="stats">{{ messages.length }} messages loaded</p>
    </header>

    <div class="messages-list">
      <article
        v-for="message in messages"
        :key="message.id"
        class="message-card"
        :class="{ 'anonymous-message': isAnonymous(message) }"
      >
        <!-- Message Header -->
        <header
          class="message-header"
          :class="{ 'anonymous-header': isAnonymous(message) }"
        >
          <div class="sender-info">
            <span class="sender-name">{{ `@${message.username}` }}</span>
            <span v-if="message.first_name" class="first-name">{{
              message.first_name
            }}</span>
            <span v-if="message.last_name" class="last-name">{{
              message.last_name
            }}</span>
            <span class="message-id">#{{ message.id }}</span>
            <span v-if="message.sender_id" class="sender-id"
              >ID: {{ message.sender_id }}</span
            >
          </div>
          <time class="message-date">{{ message.date }}</time>
        </header>

        <!-- Forward Info -->
        <div v-if="message.is_forwarded" class="forward-info">
          <span class="forward-label">↩️ Forwarded</span>
          <span v-if="message.forward?.from_name" class="forward-from">
            from {{ message.forward.from_name }}
          </span>
          <span v-else-if="message.forward?.username" class="forward-from">
            from @{{ message.forward.username }}
          </span>
          <span v-if="message.forward?.id" class="forward-id">
            (ID: {{ message.forward.id }})
          </span>
        </div>

        <!-- Reply Info -->
        <div v-if="message.reply_to" class="reply-info">
          <span class="reply-label">↪️ Reply to #{{ message.reply_to }}</span>
        </div>

        <!-- Message Content -->
        <div v-if="message.message" class="message-text">
          <div class="notranslate">{{ message.message }}</div>
          <hr class="translation-separator" />
          <div>{{ message.message }}</div>
        </div>

        <!-- Poll -->
        <div v-if="message.poll" class="poll-section">
          <div class="poll-question">
            <div class="notranslate">{{ message.poll.question }}</div>
            <hr class="translation-separator" />
            <div>{{ message.poll.question }}</div>
          </div>
          <div class="poll-answers">
            <div
              v-for="(answer, index) in message.poll.answers"
              :key="index"
              class="poll-answer"
            >
              <div class="poll-answer-text">
                <div class="notranslate">{{ answer }}</div>
                <hr class="translation-separator-small" />
                <div>{{ answer }}</div>
              </div>
              <div class="poll-result">
                <span class="poll-votes"
                  >{{ message.poll.results[index] || 0 }} votes</span
                >
                <div class="poll-bar">
                  <div
                    class="poll-bar-fill"
                    :style="{
                      width:
                        message.poll.total_voters > 0
                          ? ((message.poll.results[index] || 0) /
                              message.poll.total_voters) *
                              100 +
                            '%'
                          : '0%',
                    }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
          <div class="poll-total">
            Total voters: {{ message.poll.total_voters }}
          </div>
        </div>

        <!-- Media -->
        <div v-if="message.media?.length" class="media-section">
          <div
            v-for="media in message.media"
            :key="media.media_path"
            class="media-item"
          >
            <!-- Image -->
            <img
              v-if="getMediaType(media) === 'image'"
              v-viewport-load
              :data-src="getMediaUrl(media.media_path)"
              :alt="media.media_path"
              class="media-image"
            />

            <!-- Video -->
            <video
              v-else-if="getMediaType(media) === 'video'"
              v-viewport-load
              :data-src="getMediaUrl(media.media_path)"
              controls
              class="media-video"
            ></video>

            <!-- Audio -->
            <audio
              v-else-if="getMediaType(media) === 'audio'"
              v-viewport-load
              :data-src="getMediaUrl(media.media_path)"
              controls
              class="media-audio"
            ></audio>

            <!-- File -->
            <div v-else class="media-file">
              <a
                :href="getMediaUrl(media.media_path)"
                target="_blank"
                class="file-link"
              >
                📎 {{ formatFileSize(media.media_path) }}
              </a>
              <span class="media-type-label">{{ media.media_type }}</span>
            </div>
          </div>
        </div>

        <!-- Message Stats -->
        <div class="message-stats">
          <span v-if="message.views" class="stat">👁️ {{ message.views }}</span>
          <span v-if="message.forwards" class="stat"
            >↗️ {{ message.forwards }}</span
          >

          <!-- Reactions -->
          <div v-if="message.reactions?.length" class="reactions">
            <span
              v-for="reaction in message.reactions"
              :key="reaction.reaction"
              class="reaction"
            >
              {{
                reaction.reaction == "Custom emoji" ? "🌫️" : reaction.reaction
              }}
              {{ reaction.count }}
            </span>
          </div>
        </div>

        <!-- Comments -->
        <details v-if="message.comments?.length" class="comments-section">
          <summary class="comments-toggle">
            💬 {{ message.comments.length }} comment{{
              message.comments.length !== 1 ? "s" : ""
            }}
          </summary>

          <div class="comments-list">
            <div
              v-for="comment in message.comments"
              :key="comment.id"
              class="comment"
              :class="{ 'anonymous-comment': isAnonymous(comment) }"
            >
              <div class="comment-header">
                <div class="comment-sender-info">
                  <span class="comment-sender"> @{{ comment.username }} </span>
                  <span v-if="comment.first_name" class="comment-first-name">{{
                    comment.first_name
                  }}</span>
                  <span v-if="comment.last_name" class="comment-last-name">{{
                    comment.last_name
                  }}</span>
                  <span v-if="comment.sender_id" class="comment-sender-id"
                    >ID: {{ comment.sender_id }}</span
                  >
                </div>
                <time class="comment-date">{{ comment.date }}</time>
              </div>

              <div v-if="comment.reply_to" class="reply-info">
                ↪️ Reply to #{{ comment.reply_to }}
              </div>

              <div v-if="comment.message" class="comment-text">
                <div class="notranslate">{{ comment.message }}</div>
                <hr class="translation-separator-small" />
                <div>{{ comment.message }}</div>
              </div>

              <!-- Comment Poll -->
              <div v-if="comment.poll" class="comment-poll">
                <div class="poll-question">
                  <div class="notranslate">{{ comment.poll.question }}</div>
                  <hr class="translation-separator-small" />
                  <div>{{ comment.poll.question }}</div>
                </div>
                <div class="poll-answers">
                  <div
                    v-for="(answer, index) in comment.poll.answers"
                    :key="index"
                    class="poll-answer"
                  >
                    <div class="poll-answer-text">
                      <div class="notranslate">{{ answer }}</div>
                      <hr class="translation-separator-small" />
                      <div>{{ answer }}</div>
                    </div>
                    <div class="poll-result">
                      <span class="poll-votes"
                        >{{ comment.poll.results[index] || 0 }} votes</span
                      >
                      <div class="poll-bar">
                        <div
                          class="poll-bar-fill"
                          :style="{
                            width:
                              comment.poll.total_voters > 0
                                ? ((comment.poll.results[index] || 0) /
                                    comment.poll.total_voters) *
                                    100 +
                                  '%'
                                : '0%',
                          }"
                        ></div>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="poll-total">
                  Total voters: {{ comment.poll.total_voters }}
                </div>
              </div>

              <div v-if="comment.media?.length" class="comment-media">
                <div
                  v-for="media in comment.media"
                  :key="media.media_path"
                  class="comment-media-item"
                >
                  <!-- Image -->
                  <img
                    v-if="getMediaType(media) === 'image'"
                    v-viewport-load
                    :data-src="getMediaUrl(media.media_path)"
                    :alt="media.media_path"
                    class="comment-media-image"
                  />

                  <!-- Video -->
                  <video
                    v-else-if="getMediaType(media) === 'video'"
                    v-viewport-load
                    :data-src="getMediaUrl(media.media_path)"
                    controls
                    class="comment-media-video"
                  ></video>

                  <!-- Audio -->
                  <audio
                    v-else-if="getMediaType(media) === 'audio'"
                    v-viewport-load
                    :data-src="getMediaUrl(media.media_path)"
                    controls
                    class="comment-media-audio"
                  ></audio>

                  <!-- File -->
                  <div v-else class="comment-media-file">
                    <a
                      :href="getMediaUrl(media.media_path)"
                      target="_blank"
                      class="file-link"
                    >
                      📎 {{ formatFileSize(media.media_path) }}
                    </a>
                  </div>
                </div>
              </div>

              <div v-if="comment.reactions?.length" class="comment-reactions">
                <span
                  v-for="reaction in comment.reactions"
                  :key="reaction.reaction"
                  class="reaction"
                >
                  {{ reaction.reaction }} {{ reaction.count }}
                </span>
              </div>
            </div>
          </div>
        </details>
      </article>
    </div>
  </div>
</template>

<style lang="postcss" scoped>
.container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 1rem;
  font-family: "Whitney", "Helvetica Neue", Helvetica, Arial, sans-serif;
  background-color: #36393f;
  color: #dcddde;
  min-height: 100vh;
}

.header {
  text-align: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #40444b;
}

.header h1 {
  margin: 0 0 0.5rem 0;
  color: #ffffff;
  font-size: 2rem;
  font-weight: 600;
}

.stats {
  color: #b9bbbe;
  margin: 0;
}

.messages-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.message-card {
  background: #2f3136;
  border: 1px solid #40444b;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 1px 5px rgba(0, 0, 0, 0.2);
}

.anonymous-message {
  background: #3d2b1f;
  border-color: #8b4513;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.anonymous-header {
  background: rgba(255, 140, 0, 0.1);
  margin: -1rem -1rem 0.75rem -1rem;
  padding: 1rem;
  border-radius: 8px 8px 0 0;
  border-bottom: 2px solid #ff8c00;
}

.sender-info {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  flex-wrap: wrap;
}

.sender-name {
  font-weight: 600;
  color: #ffffff;
}

.first-name,
.last-name,
.username {
  color: #7289da;
  font-size: 0.875rem;
  background: #40444b;
  padding: 0.125rem 0.375rem;
  border-radius: 3px;
}

.message-id,
.sender-id {
  color: #b9bbbe;
  font-size: 0.875rem;
  background: #40444b;
  padding: 0.125rem 0.375rem;
  border-radius: 3px;
}

.message-date {
  color: #72767d;
  font-size: 0.875rem;
}

.forward-info,
.reply-info {
  background: #40444b;
  padding: 0.5rem;
  border-radius: 4px;
  margin-bottom: 0.75rem;
  font-size: 0.875rem;
  color: #b9bbbe;
  border-left: 3px solid #7289da;
}

.forward-label,
.reply-label {
  font-weight: 500;
  color: #7289da;
}

.forward-id {
  color: #72767d;
  font-size: 0.8rem;
}

.message-text {
  margin-bottom: 0.75rem;
  line-height: 1.5;
  white-space: pre-wrap;
  color: #dcddde;
}

.translation-separator {
  border: none;
  border-top: 1px dashed #72767d;
  margin: 0.5rem 0;
  opacity: 0.5;
}

.translation-separator-small {
  border: none;
  border-top: 1px dashed #72767d;
  margin: 0.25rem 0;
  opacity: 0.3;
}

.notranslate {
  opacity: 0.7;
  font-style: italic;
}

.poll-section {
  margin-bottom: 0.75rem;
  background: #40444b;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #4f545c;
}

.poll-question {
  font-weight: 600;
  margin-bottom: 1rem;
  color: #ffffff;
  font-size: 1.1rem;
}

.poll-answers {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.poll-answer {
  background: #36393f;
  padding: 0.75rem;
  border-radius: 6px;
  border: 1px solid #4f545c;
}

.poll-answer-text {
  margin-bottom: 0.5rem;
}

.poll-result {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.poll-votes {
  color: #b9bbbe;
  font-size: 0.875rem;
  min-width: 80px;
}

.poll-bar {
  flex: 1;
  height: 20px;
  background: #2f3136;
  border-radius: 10px;
  overflow: hidden;
}

.poll-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #7289da, #5865f2);
  transition: width 0.3s ease;
}

.poll-total {
  color: #72767d;
  font-size: 0.875rem;
  text-align: right;
  font-weight: 500;
}

.media-section {
  margin-bottom: 0.75rem;
}

.media-item {
  margin-bottom: 0.75rem;
}

.media-item:last-child {
  margin-bottom: 0;
}

.media-image {
  max-width: 100%;
  max-height: 400px;
  border-radius: 8px;
  object-fit: contain;
}

.media-video {
  max-width: 100%;
  max-height: 400px;
  border-radius: 8px;
}

.media-audio {
  width: 100%;
  max-width: 400px;
}

.media-file {
  background: #40444b;
  padding: 0.75rem;
  border-radius: 6px;
  border: 1px solid #4f545c;
}

.file-link {
  color: #00aff4;
  text-decoration: none;
  font-weight: 500;
}

.file-link:hover {
  text-decoration: underline;
}

.media-type-label {
  display: block;
  font-size: 0.75rem;
  color: #72767d;
  margin-top: 0.25rem;
  font-family: "Consolas", "Monaco", monospace;
}

.message-stats {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
  padding-top: 0.75rem;
  border-top: 1px solid #40444b;
}

.stat {
  color: #b9bbbe;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  background: #40444b;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
}

.reactions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.reaction {
  background: #40444b;
  border: 1px solid #4f545c;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.875rem;
  white-space: nowrap;
  color: #dcddde;
}

.comments-section {
  margin-top: 1rem;
  border-top: 1px solid #40444b;
  padding-top: 1rem;
}

.comments-toggle {
  cursor: pointer;
  font-weight: 500;
  color: #7289da;
  margin-bottom: 0.75rem;
  user-select: none;
}

.comments-toggle:hover {
  color: #677bc4;
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.comment {
  background: #40444b;
  padding: 0.75rem;
  border-radius: 6px;
  border-left: 3px solid #4f545c;
}

.anonymous-comment {
  background: #4a2c17;
  border-left: 3px solid #ff8c00;
  box-shadow: 0 0 10px rgba(255, 140, 0, 0.2);
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.comment-sender-info {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  flex-wrap: wrap;
}

.comment-sender {
  font-weight: 500;
  font-size: 0.875rem;
  color: #ffffff;
}

.comment-first-name,
.comment-last-name {
  color: #7289da;
  font-size: 0.75rem;
  background: #36393f;
  padding: 0.125rem 0.25rem;
  border-radius: 3px;
}

.comment-sender-id {
  font-size: 0.75rem;
  color: #72767d;
  background: #36393f;
  padding: 0.125rem 0.25rem;
  border-radius: 3px;
}

.comment-date {
  font-size: 0.75rem;
  color: #72767d;
}

.comment-text {
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
  line-height: 1.4;
  white-space: pre-wrap;
  color: #dcddde;
}

.comment-poll {
  margin-bottom: 0.5rem;
  background: #36393f;
  padding: 0.75rem;
  border-radius: 6px;
  border: 1px solid #4f545c;
}

.comment-media {
  margin-bottom: 0.5rem;
}

.comment-media-item {
  margin-bottom: 0.5rem;
}

.comment-media-item:last-child {
  margin-bottom: 0;
}

.comment-media-image {
  max-width: 100%;
  max-height: 200px;
  border-radius: 6px;
  object-fit: contain;
}

.comment-media-video {
  max-width: 100%;
  max-height: 200px;
  border-radius: 6px;
}

.comment-media-audio {
  width: 100%;
  max-width: 300px;
}

.comment-media-file {
  background: #36393f;
  padding: 0.5rem;
  border-radius: 4px;
  border: 1px solid #4f545c;
}

.comment-reactions {
  display: flex;
  gap: 0.25rem;
  flex-wrap: wrap;
}

.comment-reactions .reaction {
  font-size: 0.75rem;
  padding: 0.125rem 0.375rem;
}
</style>
