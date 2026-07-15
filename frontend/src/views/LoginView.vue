<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/authstore.js';

const email = ref('');
const password = ref('');

const router = useRouter();
const auth_store = useAuthStore();

async function login() {
    const to_send = {
        email: email.value,
        password: password.value
    }    
    const response = await fetch('http://127.0.0.1:5000/api/login', {
        method: 'POST',
        headers:{
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(to_send)
    })
    const receive_data = await response.json();
    if (response.ok){
        alert(receive_data.message);
        auth_store.setUserCred(receive_data.auth_token, receive_data.user)
        
        const roles = receive_data.user.role || [];
        if (roles.includes('admin')) {
            router.push({ name: 'admin' });
        } else if (roles.includes('company')) {
            router.push({ name: 'company' });
        } else if (roles.includes('student')) {
            router.push({ name: 'student' });
        } else {
            router.push({ name: 'home' });
        }
    }
    else{
        alert(receive_data.message);
    }
}

</script>

<template>
    <div class="needs-validation w-100 px-3" style="max-width: 400px;" novalidate>
        <h3 class="text-center mb-4">Login</h3> 
        <form @submit.prevent = "login">
            <div class="mb-3">
                <label for="exampleInputEmail1" class="form-label">Email address</label>
                <input type="email" class="form-control" id="exampleInputEmail1" aria-describedby="emailHelp" v-model="email">
            </div>
            <div class="mb-3">
                <label for="exampleInputPassword1" class="form-label">Password</label>
                <input type="password" class="form-control" id="exampleInputPassword1" v-model="password">
            </div>
            <button type="submit" class="btn btn-primary w-100">Submit</button>
        </form>
    </div>
</template>