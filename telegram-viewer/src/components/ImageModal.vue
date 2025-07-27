<script setup lang="ts">
interface Props {
  src: string;
  alt?: string;
  isOpen: boolean;
}

type Emits = {
  close: [];
};

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const closeModal = () => {
  emit("close");
};

const handleBackdropClick = (event: MouseEvent) => {
  if (event.target === event.currentTarget) {
    closeModal();
  }
};

const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === "Escape") {
    closeModal();
  }
};

// Add/remove event listener for escape key
import { onMounted, onUnmounted, watch } from "vue";

onMounted(() => {
  document.addEventListener("keydown", handleKeydown);
});

onUnmounted(() => {
  document.removeEventListener("keydown", handleKeydown);
});

// Prevent body scroll when modal is open
watch(
  () => props.isOpen,
  (isOpen) => {
    if (isOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
  }
);
</script>

<template>
  <Teleport to="body">
    <div v-if="isOpen" class="modal-backdrop" @click="handleBackdropClick">
      <div class="modal-container">
        <button
          class="close-button"
          @click="closeModal"
          aria-label="Close image"
        >
          ✕
        </button>
        <img
          :src="src"
          :alt="alt || 'Modal content'"
          class="modal-image"
          @click.stop
        />
      </div>
    </div>
  </Teleport>
</template>

<style lang="postcss" scoped>
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  box-sizing: border-box;
  animation: fadeIn 0.2s ease-out;
}

.modal-container {
  position: relative;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  border-radius: 8px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
  animation: scaleIn 0.2s ease-out;
}

.close-button {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: white;
  font-size: 1.5rem;
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s ease;
  z-index: 1001;
}

.close-button:hover {
  background: rgba(255, 255, 255, 0.2);
}

.close-button:focus {
  outline: 2px solid #7289da;
  outline-offset: 2px;
}

/* Animation */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes scaleIn {
  from {
    transform: scale(0.9);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}
</style>
