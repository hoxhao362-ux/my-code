<script setup>
import { useRouter } from 'vue-router'
import Navigation from '../components/Navigation.vue'
import { useUserStore } from '../stores/user'
import { computed } from 'vue'

const router = useRouter()
const userStore = useUserStore()
const user = computed(() => userStore.user)

const goHome = () => {
  router.push('/home')
}

const goBack = () => {
  router.back()
}
</script>

<template>
  <div class="not-found-container">
    <Navigation :user="user" />
    
    <main class="not-found-content">
      <div class="error-code">404</div>
      <h1 class="error-title">Page Not Found</h1>
      <p class="error-message">
        The page you are looking for does not exist or has been moved.
      </p>
      <div class="error-actions">
        <button class="btn-primary" @click="goHome">
          Return to Homepage
        </button>
        <button class="btn-secondary" @click="goBack">
          Go Back
        </button>
      </div>
    </main>

    <footer class="footer">
      <div class="footer-content">
<<<<<<< HEAD
        <p>&copy; 2026 Journal Submission Platform. All rights reserved.</p>
=======
        <p>&copy; 2026 Peerex Peer. All rights reserved.</p>
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
      </div>
    </footer>
  </div>
</template>

<style scoped>
.not-found-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f9f9f9;
}

.not-found-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  text-align: center;
  margin-top: 80px;
}

.error-code {
  font-size: 8rem;
  font-weight: 700;
  color: #C93737;
  line-height: 1;
  margin-bottom: 1rem;
  font-family: Arial, sans-serif;
}

.error-title {
  font-size: 2rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 1rem 0;
  font-family: Arial, sans-serif;
}

.error-message {
  font-size: 1.1rem;
  color: #666;
  max-width: 500px;
  margin: 0 0 2rem 0;
  line-height: 1.6;
}

.error-actions {
  display: flex;
  gap: 1rem;
}

.btn-primary,
.btn-secondary {
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  font-weight: 500;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary {
  background-color: #C93737;
  color: white;
}

.btn-primary:hover {
  background-color: #a02020;
}

.btn-secondary {
  background-color: #f0f0f0;
  color: #333;
  border: 1px solid #ddd;
}

.btn-secondary:hover {
  background-color: #e0e0e0;
}

.footer {
  background: #2c3e50;
  color: white;
  padding: 1rem 0;
  text-align: center;
}

@media (max-width: 768px) {
  .error-code {
    font-size: 5rem;
  }

  .error-title {
    font-size: 1.5rem;
  }

  .error-actions {
    flex-direction: column;
    width: 100%;
    max-width: 300px;
  }

  .btn-primary,
  .btn-secondary {
    width: 100%;
  }
}
</style>
