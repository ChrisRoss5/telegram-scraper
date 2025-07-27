<script setup lang="ts">
import { ref } from "vue";
import ImageModal from "./ImageModal.vue";

interface Props {
  message: TelegramMessage;
  server: string;
  isComment?: boolean;
}

const props = defineProps<Props>();

// Modal state
const isModalOpen = ref(false);
const modalImageSrc = ref("");
const modalImageAlt = ref("");

const openImageModal = (src: string, alt: string) => {
  modalImageSrc.value = src;
  modalImageAlt.value = alt;
  isModalOpen.value = true;
};

const closeImageModal = () => {
  isModalOpen.value = false;
};

const isAnonymous = (msg: TelegramMessage) => {
  return !msg.sender_id;
};

const getMediaUrl = (media: string) => {
  return props.server + media.replace(/\\/g, "/");
};

const getMediaType = (media: string) => {
  const path = media.toLowerCase();

  if (path.match(/\.(jpg|jpeg|png|gif|webp)$/)) return "image";
  if (path.match(/\.(mp4|webm|mov|avi|mkv)$/)) return "video";
  if (path.match(/\.(mp3|wav|ogg|m4a|flac)$/)) return "audio";
  return "file";
};

const formatFileSize = (path: string) => {
  // Extract filename from path
  return path.split(/[/\\]/).pop() || path;
};
</script>

<template>
  <article
    :class="[
      props.isComment ? 'comment' : 'message-card',
      { 'anonymous-message': isAnonymous(props.message) },
      { 'anonymous-comment': props.isComment && isAnonymous(props.message) },
    ]"
  >
    <!-- Message Header -->
    <header
      :class="[
        props.isComment ? 'comment-header' : 'message-header',
        { 'anonymous-header': !props.isComment && isAnonymous(props.message) },
      ]"
    >
      <div :class="props.isComment ? 'comment-sender-info' : 'sender-info'">
        <span :class="props.isComment ? 'comment-sender' : 'sender-name'">
          @{{ props.message.username }}
        </span>
        <span
          v-if="props.message.first_name"
          :class="props.isComment ? 'comment-first-name' : 'first-name'"
        >
          {{ props.message.first_name }}
        </span>
        <span
          v-if="props.message.last_name"
          :class="props.isComment ? 'comment-last-name' : 'last-name'"
        >
          {{ props.message.last_name }}
        </span>
        <span v-if="!props.isComment" class="message-id">
          #{{ props.message.id }}
        </span>
        <span
          v-if="props.message.sender_id"
          :class="props.isComment ? 'comment-sender-id' : 'sender-id'"
        >
          ID: {{ props.message.sender_id }}
        </span>
      </div>
      <time :class="props.isComment ? 'comment-date' : 'message-date'">
        {{ props.message.date }}
      </time>
    </header>

    <!-- Forward Info -->
    <div v-if="props.message.is_forwarded" class="forward-info">
      <span class="forward-label">↩️ Forwarded</span>
      <span v-if="props.message.forward?.from_name" class="forward-from">
        from {{ props.message.forward.from_name }}
      </span>
      <span v-else-if="props.message.forward?.username" class="forward-from">
        from @{{ props.message.forward.username }}
      </span>
      <span v-if="props.message.forward?.id" class="forward-id">
        (ID: {{ props.message.forward.id }})
      </span>
    </div>

    <!-- Reply Info -->
    <div v-if="props.message.reply_to" class="reply-info">
      <span class="reply-label">↪️ Reply to #{{ props.message.reply_to }}</span>
    </div>

    <!-- Message Content -->
    <div
      v-if="props.message.message"
      :class="props.isComment ? 'comment-text' : 'message-text'"
    >
      <div class="notranslate">{{ props.message.message }}</div>
      <hr
        :class="
          props.isComment
            ? 'translation-separator-small'
            : 'translation-separator'
        "
      />
      <div>{{ props.message.message_translated || props.message.message }}</div>
    </div>

    <!-- Poll -->
    <div
      v-if="props.message.poll"
      :class="props.isComment ? 'comment-poll' : 'poll-section'"
    >
      <div class="poll-question">
        <div class="notranslate">{{ props.message.poll.question }}</div>
        <hr
          :class="
            props.isComment
              ? 'translation-separator-small'
              : 'translation-separator'
          "
        />
        <div>{{ props.message.poll.question }}</div>
      </div>
      <div class="poll-answers">
        <div
          v-for="(answer, index) in props.message.poll.answers"
          :key="index"
          class="poll-answer"
        >
          <div class="poll-answer-text">
            <div class="notranslate">{{ answer }}</div>
            <hr class="translation-separator-small" />
            <div>{{ answer }}</div>
          </div>
          <div class="poll-result">
            <span class="poll-votes">
              {{ props.message.poll.results[index] || 0 }} votes
            </span>
            <div class="poll-bar">
              <div
                class="poll-bar-fill"
                :style="{
                  width:
                    props.message.poll.total_voters > 0
                      ? ((props.message.poll.results[index] || 0) /
                          props.message.poll.total_voters) *
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
        Total voters: {{ props.message.poll.total_voters }}
      </div>
    </div>

    <!-- Media -->
    <div
      v-if="props.message.media?.length"
      :class="props.isComment ? 'comment-media' : 'media-section'"
    >
      <div
        v-for="media in props.message.media"
        :key="media"
        :class="props.isComment ? 'comment-media-item' : 'media-item'"
      >
        <!-- Image -->
        <img
          v-if="getMediaType(media) === 'image'"
          v-viewport-load
          :data-src="getMediaUrl(media)"
          :alt="media"
          :class="props.isComment ? 'comment-media-image' : 'media-image'"
          @click="openImageModal(getMediaUrl(media), media)"
          style="cursor: pointer"
        />

        <!-- Video -->
        <video
          v-else-if="getMediaType(media) === 'video'"
          v-viewport-load
          :data-src="getMediaUrl(media)"
          controls
          :class="props.isComment ? 'comment-media-video' : 'media-video'"
        ></video>

        <!-- Audio -->
        <audio
          v-else-if="getMediaType(media) === 'audio'"
          v-viewport-load
          :data-src="getMediaUrl(media)"
          controls
          :class="props.isComment ? 'comment-media-audio' : 'media-audio'"
        ></audio>

        <!-- File -->
        <div
          v-else
          :class="props.isComment ? 'comment-media-file' : 'media-file'"
        >
          <a :href="getMediaUrl(media)" target="_blank" class="file-link">
            📎 {{ formatFileSize(media) }}
          </a>
          <span class="media-type-label">{{ getMediaType(media) }}</span>
        </div>
      </div>
    </div>

    <!-- Message Stats (only for non-comments) -->
    <div v-if="!props.isComment" class="message-stats">
      <span v-if="props.message.views" class="stat"
        >👁️ {{ props.message.views }}</span
      >
      <span v-if="props.message.forwards" class="stat"
        >↗️ {{ props.message.forwards }}</span
      >

      <!-- Reactions -->
      <div v-if="props.message.reactions?.length" class="reactions">
        <span
          v-for="reaction in props.message.reactions"
          :key="reaction.reaction"
          class="reaction"
        >
          {{ reaction.reaction == "Custom emoji" ? "🌫️" : reaction.reaction }}
          {{ reaction.count }}
        </span>
      </div>
    </div>

    <!-- Comment Reactions (only for comments) -->
    <div
      v-if="props.isComment && props.message.reactions?.length"
      class="comment-reactions"
    >
      <span
        v-for="reaction in props.message.reactions"
        :key="reaction.reaction"
        class="reaction"
      >
        {{ reaction.reaction == "Custom emoji" ? "🌫️" : reaction.reaction }}
        {{ reaction.count }}
      </span>
    </div>

    <!-- Comments (only for non-comments) -->
    <details
      v-if="!props.isComment && props.message.comments?.length"
      class="comments-section"
    >
      <summary class="comments-toggle">
        💬 {{ props.message.comments.length }} comment{{
          props.message.comments.length !== 1 ? "s" : ""
        }}
      </summary>

      <div class="comments-list">
        <Message
          v-for="comment in props.message.comments"
          :key="comment.id"
          :message="comment"
          :server="props.server"
          :is-comment="true"
        />
      </div>
    </details>

    <!-- Image Modal -->
    <ImageModal
      :src="modalImageSrc"
      :alt="modalImageAlt"
      :is-open="isModalOpen"
      @close="closeImageModal"
    />
  </article>
</template>

<style lang="postcss" scoped>
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
