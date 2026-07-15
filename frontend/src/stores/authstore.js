import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const useAuthStore = defineStore('authStore', () => {
    const auth_token = ref(localStorage.getItem('token') || null)
    const user = ref(JSON.parse(localStorage.getItem('user')) || null)
    const isAuthenticated = computed(() => auth_token.value !== null)

    function setUserCred(token, newUser){
    localStorage.setItem('token', token)
    localStorage.setItem('user', JSON.stringify(newUser))
    auth_token.value = token
    user.value = newUser
}

    function clearAuthToken() {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        auth_token.value = null
        user.value = null
    }

    function getAuthToken() {
        return auth_token.value
    }

    function getUserEmail() {
        return user.value ? user.value.email : null
    }

    function getUserRoles(){
        if (!user.value) return [];
        if (Array.isArray(user.value.role)) return user.value.role;
        if (typeof user.value.role === 'string') return [user.value.role];
        return [];
    }

    return {isAuthenticated, getAuthToken, getUserEmail, getUserRoles, setUserCred, clearAuthToken}
})
