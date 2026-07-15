<script setup>
import { RouterLink, RouterView, useRouter, useRoute } from 'vue-router';
import { computed } from 'vue';
import { useAuthStore } from '@/stores/authstore.js';
const auth_store = useAuthStore();
const user_email = computed(() => {
  return auth_store.getUserEmail()
});
const router = useRouter()
const token = computed(() => {
  return auth_store.getAuthToken()
});
async function logoutfunc() {
    const response = await fetch('http://127.0.0.1:5000/api/logout', {
          method: 'POST',
          headers:{
              'Content-Type': 'application/json',
              'Authorization': token.value
          }
      })
    const receive_data = await response.json();
    if (response.ok){
        alert(receive_data.message);
        auth_store.clearAuthToken()
        router.push({ name: 'home' })
    }
    else{
        alert(receive_data.message || "Logout failed or session expired.");
        auth_store.clearAuthToken()
        router.push({ name: 'home' })
    }
}


</script>

<template>
  <div class="d-flex flex-column min-vh-100">
    <nav class="navbar navbar-expand-lg bg-body-tertiary">
      <div class="container-fluid">
        <a class="navbar-brand" href="#">Placement Portal</a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarSupportedContent" v-if="auth_store.isAuthenticated"> 
          <ul class="navbar-nav me-auto mb-2 mb-lg-0 align-items-center">
            <li class="nav-item">
              <span class="navbar-text me-3" style="color: black; font-family: 'Courier New', monospace;">Welcome, {{ user_email }}</span>
            </li>
            <li class="nav-item" v-if="auth_store.getUserRoles().includes('admin')">
              <RouterLink class="nav-link" to="/admin">Dashboard</RouterLink>
            </li>
            <li class="nav-item" v-else-if="auth_store.getUserRoles().includes('company')">
              <RouterLink class="nav-link" to="/company">Dashboard</RouterLink>
            </li>
            <li class="nav-item" v-else-if="auth_store.getUserRoles().includes('student')">
              <RouterLink class="nav-link" to="/student">Dashboard</RouterLink>
            </li>
            <li class="nav-item">
              <RouterLink class="nav-link" to="/profile">Profile</RouterLink>
            </li>
          </ul>
          <form class="d-flex" @submit.prevent="logoutfunc">
            <button class="btn btn-danger" type="submit">Logout</button>
          </form>
        </div>
        <div class="collapse navbar-collapse" id="navbarSupportedContent" v-else> 
          <ul class="navbar-nav me-auto mb-2 mb-lg-0">
            <li class="nav-item">
              <RouterLink class="nav-link active" aria-current="page" to="/login">Login</RouterLink>
            </li>
            <li class="nav-item">
              <RouterLink class="nav-link active" to="/register">Register</RouterLink>
            </li>
          </ul>
        </div>
      </div>
    </nav>
    <main class="flex-grow-1 d-flex align-items-center justify-content-center">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
</style>
