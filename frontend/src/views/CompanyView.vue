<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/authstore.js';
import drivelist from '@/components/drivelist.vue';

const router = useRouter(); 
const auth_store = useAuthStore();

const dashboardData = ref([]);
const id = ref('');
const email = auth_store.getUserEmail();
const to_send = {
    'email': email
}
onMounted(async () => {
    try {
        const compResponse = await fetch(`http://127.0.0.1:5000/api/compdetails`, { 
            method: 'POST',
            headers:{
            'Content-Type': 'application/json'
            },
            body: JSON.stringify(to_send)
        });
        const compData = await compResponse.json();
        
        if (!compResponse.ok) {
            alert(compData.message);
            router.push({ name: 'home' });
            return;
        }
        id.value = compData.id; 
        
        const driveResponse = await fetch(`http://127.0.0.1:5000/api/getcompdrive/${id.value}`, { method: 'GET' });
        const driveData = await driveResponse.json();
        
        if (driveResponse.ok) {
            dashboardData.value = driveData;
        } else {
            alert(driveData.message);
            router.push({ name: 'home' });
        }
    } catch (error) {
        console.error("Network error:", error);
    }
});
</script>

<template>
    <div>
        <RouterLink class="btn btn-primary" role="button" to="/createdrive">Create Drive</RouterLink>
    </div>
    <div>
        <drivelist :items="dashboardData" />
    </div>
</template>