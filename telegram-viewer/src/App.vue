<script setup lang="ts">
import rawMessages from "@root/messages.json";
import Message from "./components/Message.vue";

const server = "http://127.0.0.1:5500/telegram-scraper/";

const w = window as any;
const m = rawMessages as TelegramMessage[];

console.log("Total messages:", m.length);
console.log("Forwarded messages:", m.filter((m) => m.is_forwarded).length);
console.log("Replied messages:", m.filter((m) => m.reply_to).length);
console.log("Messages with media:", m.filter((m) => m.media).length);
console.log("Messages with text:", m.filter((m) => m.message).length);
console.log(
  "Messages with text and media:",
  m.filter((m) => m.message && m.media).length
);
console.log("Messages with polls:", m.filter((m) => m.poll).length);
console.log("Total comments:", m.flatMap((m) => m.comments || []).length);

w.m = m;
w.m2 = m
  .filter((m) => m.message && !m.is_forwarded)
  .map((m) => {
    if (m.poll)
      return `ID: ${m.id} | POLL | ${m.date}: ${JSON.stringify(m.poll)}`;
    return `ID: ${m.id}${m.media ? " | MEDIA" : ""}${
      m.reply_to ? ` | Reply to ID: ${m.reply_to}` : ""
    } | ${m.date}: ${m.message}`;
  });

const messages = m.slice(-10).reverse();
</script>

<template>
  <div class="container">
    <header class="header">
      <h1>Telegram Messages</h1>
      <p class="stats">{{ messages.length }} messages loaded</p>
    </header>

    <div class="messages-list">
      <Message
        v-for="message in messages"
        :key="message.id"
        :message="message"
        :server="server"
      />
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
</style>
