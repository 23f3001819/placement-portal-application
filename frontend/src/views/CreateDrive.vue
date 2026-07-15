<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/authstore.js';

const router = useRouter();
const auth_store = useAuthStore();

const jobRole = ref('');
const jobDesc = ref('');
const branchCriteria = ref('');
const cgpaCriteria = ref('');
const jobCtc = ref('');
const deadline = ref('');

const errorMessage = ref('');
const companyId = ref(null);

onMounted(async () => {
    try {
        const email = auth_store.getUserEmail();
        if (!email) {
            errorMessage.value = "User email not found. Please log in.";
            return;
        }

        const response = await fetch('http://127.0.0.1:5000/api/compdetails', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': auth_store.getAuthToken() || ''
            },
            body: JSON.stringify({ email })
        });

        const data = await response.json();

        if (response.ok) {
            companyId.value = data.id;
        } else {
            errorMessage.value = data.message || "Failed to load company details.";
        }
    } catch (error) {
        console.error("Error fetching company details:", error);
        errorMessage.value = "Failed to load company details due to a network error.";
    }
});

const submitDrive = async () => {
    if (!jobRole.value || !branchCriteria.value || !cgpaCriteria.value || !jobCtc.value || !deadline.value) {
        errorMessage.value = "Please fill in all required fields.";
        return;
    }

    if (!companyId.value) {
        errorMessage.value = "Company details are still loading. Please try again in a moment.";
        return;
    }

    const formattedDeadline = new Date(deadline.value).toISOString();

    const branchList = branchCriteria.value.split(',').map(s => s.trim()).filter(s => s.length > 0);

    const payload = {
        comp_id: companyId.value,
        job_role: jobRole.value,
        job_desc: jobDesc.value,
        branch_c: branchList,
        cgpa_c: parseFloat(cgpaCriteria.value),
        job_ctc: parseFloat(jobCtc.value),
        deadline: formattedDeadline
    };

    try {
        const response = await fetch('http://127.0.0.1:5000/api/drives', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': auth_store.getAuthToken() || '' 
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (response.ok) {
            alert(data.message);
            router.push({ name: 'company' });
        } else {
            errorMessage.value = data.message || "Failed to create drive.";
        }
    } catch (error) {
        console.error("Network error:", error);
        errorMessage.value = "A network error occurred. Please try again.";
    }
};
</script>

<template>
    <div class="container mt-5" style="max-width: 600px;">
        <h2 class="mb-4">Create New Placement Drive</h2>
        
        <div v-if="errorMessage" class="alert alert-danger">
            {{ errorMessage }}
        </div>

        <form @submit.prevent="submitDrive">
            
            <div class="mb-3">
                <label for="jobRole" class="form-label">Job Role *</label>
                <input type="text" class="form-control" id="jobRole" v-model="jobRole" required>
            </div>

            <div class="mb-3">
                <label for="jobDesc" class="form-label">Job Description</label>
                <textarea class="form-control" id="jobDesc" rows="3" v-model="jobDesc"></textarea>
            </div>

            <div class="row">
                <div class="col-md-6 mb-3">
                    <label for="jobCtc" class="form-label">Pay / CTC (in LPA) *</label>
                    <input type="number" step="0.1" class="form-control" id="jobCtc" v-model="jobCtc" required>
                </div>
                
                <div class="col-md-6 mb-3">
                    <label for="deadline" class="form-label">Application Deadline *</label>
                    <input type="datetime-local" class="form-control" id="deadline" v-model="deadline" required>
                </div>
            </div>

            <h5 class="mt-4 border-bottom pb-2">Eligibility Criteria</h5>
            
            <div class="row">
                <div class="col-md-6 mb-3">
                    <label for="cgpaCriteria" class="form-label">Minimum CGPA *</label>
                    <input type="number" step="0.1" min="0" max="10" class="form-control" id="cgpaCriteria" v-model="cgpaCriteria" required>
                </div>

                <div class="col-md-6 mb-3">
                    <label for="branchCriteria" class="form-label">Eligible Branches *</label>
                    <input type="text" class="form-control" id="branchCriteria" placeholder="e.g. CSE, IT or ALL" v-model="branchCriteria" required>
                </div>
            </div>

            <div class="d-flex justify-content-between mt-4">
                <RouterLink to="/company" class="btn btn-secondary">Cancel</RouterLink>
                <button type="submit" class="btn btn-primary">Create Drive</button>
            </div>
            
        </form>
    </div>
</template>